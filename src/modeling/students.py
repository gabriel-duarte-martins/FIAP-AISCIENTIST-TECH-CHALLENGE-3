import json
import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from src.config import FEATURES, REPORTS, ROOT, CONFIG, TARGET, WEIGHT
from src.preprocessing import ProfilePreprocessor
from src.evaluation.metrics import metrics, bootstrap_municipal, calibration


def build(family,params):
    if family=='baseline':
        estimator=DummyClassifier(strategy='prior')
    elif family=='logistica':
        estimator=LogisticRegression(max_iter=2000,random_state=42,**params)
    else:
        estimator=HistGradientBoostingClassifier(early_stopping=False,random_state=42,**params)
    return Pipeline([('preprocess',ProfilePreprocessor()),('model',estimator)])


def fit(model,frame):
    w=frame[WEIGHT].to_numpy(dtype=float)
    return model.fit(frame[FEATURES],frame[TARGET].astype(int),preprocess__sample_weight=w,model__sample_weight=w)


def predict(model,frame):
    return model.predict_proba(frame[FEATURES])[:,1]


def run_models(parts):
    train,val,test = parts['treino'],parts['validacao'],parts['teste']
    candidates=[('baseline',{})]+[('logistica',{'C':c}) for c in [.0001,.001,.01,.1]]+[
        ('boosting',{'max_leaf_nodes':leaves,'l2_regularization':reg,'max_iter':120,'learning_rate':.06})
        for leaves in [7,15] for reg in [10,100]]
    cv=GroupKFold(n_splits=3)
    rows=[]
    for family,params in candidates:
        fold_scores=[]
        for train_i,valid_i in cv.split(train,groups=train.id_municipio):
            model=fit(build(family,params),train.iloc[train_i])
            fold=train.iloc[valid_i]
            fold_scores.append(metrics(fold[TARGET],predict(model,fold),fold[WEIGHT])['brier'])
        row=dict(familia=family,parametros=json.dumps(params),cv_brier=np.mean(fold_scores),cv_std=np.std(fold_scores))
        rows.append(row)
        print(f"CV {family} {params}: Brier={row['cv_brier']:.4f}",flush=True)
    tuning=pd.DataFrame(rows)
    tuning.to_csv(REPORTS/'busca_hiperparametros.csv',index=False)
    selected={}
    validation=[]
    for family,group in tuning.groupby('familia'):
        best=group.sort_values('cv_brier').iloc[0]
        model=fit(build(family,json.loads(best.parametros)),train)
        selected[family]=model
        m=metrics(val[TARGET],predict(model,val),val[WEIGHT])
        validation.append({'familia':family,**{k:v for k,v in m.items() if k!='confusion_risco'}})
    validation=pd.DataFrame(validation).sort_values('brier')
    validation.to_csv(REPORTS/'comparacao_validacao.csv',index=False)
    winner=validation.iloc[0].familia
    champion=selected[winner]
    pval=predict(champion,val)
    threshold_rows=[metrics(val[TARGET],pval,val[WEIGHT],t) for t in np.arange(.1,.81,.01)]
    threshold_frame=pd.DataFrame([{k:v for k,v in m.items() if k!='confusion_risco'} for m in threshold_rows])
    threshold_frame.to_csv(REPORTS/'sensibilidade_limiar_validacao.csv',index=False)
    threshold=float(threshold_frame.sort_values(['balanced_accuracy','limiar_risco'],ascending=[False,False]).iloc[0].limiar_risco)
    # Teste consultado só depois da escolha de família, hiperparâmetros e limiar.
    ptest=predict(champion,test)
    final=metrics(test[TARGET],ptest,test[WEIGHT],threshold)
    final.update(modelo=winner,avaliacao='municipios_disjuntos_2024',
                 observacao='Revisão exploratória; teste já foi consultado na versão inicial do projeto.',
                 intervalo95_bootstrap_municipios=bootstrap_municipal(test,ptest,threshold,CONFIG['bootstrap_repeats']))
    final['baseline']=metrics(test[TARGET],predict(selected['baseline'],test),test[WEIGHT],.5)
    final['limiar_05']=metrics(test[TARGET],ptest,test[WEIGHT],.5)
    (REPORTS/'metricas_teste.json').write_text(json.dumps(final,indent=2,ensure_ascii=False),encoding='utf-8')
    calibration(test[TARGET].to_numpy(),ptest,test[WEIGHT].to_numpy(dtype=float)).to_csv(REPORTS/'calibracao_teste.csv',index=False)
    test_export=test[['id_municipio','nome_municipio','sigla_uf','nome_regiao','rede','serie',TARGET,WEIGHT]].copy()
    test_export['prob_alfabetizado']=ptest
    test_export.to_parquet(ROOT/'data'/'predicoes_teste_perfis.parquet',index=False)
    groups=[]
    for column in ['sigla_uf','rede']:
        for name,idx in test.groupby(column,dropna=False).indices.items():
            sub=test.iloc[idx]
            m=metrics(sub[TARGET],ptest[idx],sub[WEIGHT],threshold)
            groups.append({'recorte':column,'grupo':str(name),'municipios':sub.id_municipio.nunique(),
                           'amostra_pequena':sub.id_municipio.nunique()<30 or sub.peso.sum()<1000,
                           **{k:v for k,v in m.items() if k!='confusion_risco'}})
    pd.DataFrame(groups).to_csv(REPORTS/'metricas_por_grupo.csv',index=False)
    modeldir=ROOT/'models'
    modeldir.mkdir(exist_ok=True)
    joblib.dump({'pipeline':champion,'features':FEATURES,'threshold_risk':threshold,'target':'alfabetizado_2024'},modeldir/'modelo_individual_final.joblib')
    return champion,final,ptest


def importance(model,test,repeats=5):
    """Permuta atributos por perfil contextual, mantendo juntas as duas classes."""
    test=test.reset_index(drop=True)
    keys=test[['id_municipio','rede','serie']].astype(str).agg('|'.join,axis=1)
    base=metrics(test[TARGET],predict(model,test),test[WEIGHT])['brier']
    rng=np.random.default_rng(42)
    rows=[]
    for feature in FEATURES:
        values=test.assign(_key=keys).groupby('_key',sort=True)[feature].first()
        diffs=[]
        for _ in range(repeats):
            shuffled=pd.Series(rng.permutation(values.to_numpy()),index=values.index)
            permuted=test.copy()
            permuted[feature]=keys.map(shuffled)
            diffs.append(metrics(test[TARGET],predict(model,permuted),test[WEIGHT])['brier']-base)
        rows.append({'feature':feature,'aumento_brier':np.mean(diffs),'std':np.std(diffs)})
    out=pd.DataFrame(rows).sort_values('aumento_brier',ascending=False)
    out.to_csv(REPORTS/'importancia_permutacao.csv',index=False)
    return out
