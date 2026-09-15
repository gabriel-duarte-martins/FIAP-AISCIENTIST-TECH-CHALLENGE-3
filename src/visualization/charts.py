import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, precision_recall_curve
from src.config import IMAGES, REPORTS, NUMERIC, LABELS, TARGET, WEIGHT

plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,
    'axes.titleweight':'bold','axes.labelcolor':'#26364a','text.color':'#172a3a','figure.facecolor':'white',
    'axes.prop_cycle':plt.cycler(color=['#087f8c','#6554c0','#dd8d37','#c84d5d']),
    'savefig.dpi':160,'font.size':10})

def save(fig,name):
    IMAGES.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(IMAGES/name,bbox_inches='tight')
    plt.close(fig)


def eda(train):
    w=train.peso.to_numpy(dtype=float)
    y=train[TARGET].to_numpy(dtype=float)
    dist=train.groupby(TARGET).peso.sum().reindex([0,1])
    fig,ax=plt.subplots(figsize=(7,4))
    ax.bar(['Não alfabetizado','Alfabetizado'],dist, color=['#c84d5d','#087f8c'])
    ax.set(title='Distribuição do alvo no treino',ylabel='Observações de alunos')
    for i,n in enumerate(dist): ax.text(i,n,f'{n:,.0f}\n{n/dist.sum():.1%}',ha='center',va='bottom')
    ax.set_ylim(0,dist.max()*1.2)
    save(fig,'01_alvo_treino.png')
    missing=pd.Series({c:train.loc[train[c].isna(),WEIGHT].sum()/w.sum() for c in NUMERIC}).sort_values()
    missing.rename('fracao_alunos_sem_valor').to_csv(REPORTS/'faltantes_treino.csv')
    fig,ax=plt.subplots(figsize=(10,5))
    ax.barh([LABELS[c] for c in missing.index],missing*100)
    ax.set(xlabel='% de alunos representados',title='Dados faltantes no treino')
    save(fig,'02_faltantes_treino.png')
    fig,axes=plt.subplots(1,3,figsize=(13,4))
    for ax,col,log in zip(axes,['taxa_alfabetizacao_municipio_ano_anterior','pib_per_capita_2021','populacao_2022'],[False,True,True]):
        a=train[col].to_numpy(dtype=float,na_value=np.nan)
        if log: a=np.log10(np.maximum(a,1))
        mask=np.isfinite(a)
        ax.hist(a[mask],bins=25,weights=w[mask],color='#087f8c',alpha=.85)
        ax.set(title=LABELS[col],xlabel='log10' if log else '%',ylabel='Alunos')
    save(fig,'03_distribuicoes_treino.png')
    cols=NUMERIC+[TARGET]
    correlation=np.full((len(cols),len(cols)),np.nan)
    for i,c1 in enumerate(cols):
        for j,c2 in enumerate(cols):
            a=train[c1].to_numpy(dtype=float,na_value=np.nan); b=train[c2].to_numpy(dtype=float,na_value=np.nan)
            ok=np.isfinite(a)&np.isfinite(b)
            if not ok.any(): continue
            a,b,ww=a[ok],b[ok],w[ok]
            a=a-np.average(a,weights=ww); b=b-np.average(b,weights=ww)
            denom=np.sqrt(np.average(a*a,weights=ww)*np.average(b*b,weights=ww))
            if denom: correlation[i,j]=np.average(a*b,weights=ww)/denom
    corr=pd.DataFrame(correlation,index=cols,columns=cols)
    corr.to_csv(REPORTS/'correlacoes_treino.csv')
    fig,ax=plt.subplots(figsize=(11,8))
    im=ax.imshow(correlation,vmin=-1,vmax=1,cmap='RdBu_r')
    names=[LABELS.get(c,'Alvo alfabetizado').replace('municipal ','') for c in cols]
    ax.set_xticks(range(len(cols)),names,rotation=65,ha='right',fontsize=8)
    ax.set_yticks(range(len(cols)),names,fontsize=8)
    ax.set_title('Correlação ponderada no treino — associação, sem causalidade')
    fig.colorbar(im,ax=ax,shrink=.7)
    save(fig,'04_correlacoes_treino.png')
    rows=[]
    for col in NUMERIC:
        a=train[col].to_numpy(dtype=float,na_value=np.nan); ok=np.isfinite(a)
        order=np.argsort(a[ok]); vals=a[ok][order]; ww=w[ok][order]
        cs=np.cumsum(ww)/ww.sum()
        rows.append({'variavel':col,'media_ponderada':np.average(vals,weights=ww),
                     **{f'p{int(q*100)}':float(vals[np.searchsorted(cs,q)]) for q in [.1,.5,.9]}})
    pd.DataFrame(rows).to_csv(REPORTS/'estatisticas_treino.csv',index=False)


def evaluation(test,p,final,imp):
    validation=pd.read_csv(REPORTS/'comparacao_validacao.csv')
    fig,ax=plt.subplots(figsize=(7,4))
    ax.bar(validation.familia,validation.brier)
    ax.set(title='Comparação na validação',ylabel='Brier score — menor é melhor')
    save(fig,'05_comparacao_modelos.png')
    y=1-test[TARGET].to_numpy(dtype=int); risk=1-p; w=test[WEIGHT].to_numpy(dtype=float)
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    fpr,tpr,_=roc_curve(y,risk,sample_weight=w)
    axes[0].plot(fpr,tpr,label=f"AUC = {final['roc_auc']:.3f}")
    axes[0].plot([0,1],[0,1],'--',color='#9ca3af'); axes[0].legend()
    axes[0].set(title='ROC — teste',xlabel='Taxa de falsos positivos',ylabel='Sensibilidade ao risco')
    prec,rec,_=precision_recall_curve(y,risk,sample_weight=w)
    axes[1].plot(rec,prec,label=f"AP = {final['average_precision_risco']:.3f}")
    axes[1].axhline(np.average(y,weights=w),ls='--',color='#9ca3af',label='Prevalência')
    axes[1].legend(); axes[1].set(title='Precisão × recall — não alfabetizado',xlabel='Recall',ylabel='Precisão')
    save(fig,'06_roc_pr_teste.png')
    cal=pd.read_csv(REPORTS/'calibracao_teste.csv')
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    axes[0].plot([0,1],[0,1],'--',color='#9ca3af')
    axes[0].plot(cal.previsto,cal.observado,'o-')
    axes[0].set(title='Calibração — probabilidade de alfabetização',xlabel='Probabilidade média prevista',ylabel='Fração observada')
    cm=np.array(final['confusion_risco'])
    axes[1].imshow(cm,cmap='Blues')
    for i in range(2):
        for j in range(2): axes[1].text(j,i,f'{cm[i,j]:,}',ha='center',va='center',color='white' if cm[i,j]>cm.max()*.6 else '#172a3a')
    axes[1].set_xticks([0,1],['Sem sinalização','Em risco'])
    axes[1].set_yticks([0,1],['Alfabetizado','Não alfabetizado'])
    axes[1].set(title=f"Matriz de confusão — limiar {final['limiar_risco']:.2f}",xlabel='Predição',ylabel='Observado')
    save(fig,'07_calibracao_confusao.png')
    fig,ax=plt.subplots(figsize=(10,6))
    ordered=imp.sort_values('aumento_brier')
    ax.barh([LABELS[c] for c in ordered.feature],ordered.aumento_brier,xerr=ordered['std'])
    ax.set(title='Importância por permutação no teste',xlabel='Aumento no Brier ao permutar o atributo')
    save(fig,'08_importancia.png')
    groups=pd.read_csv(REPORTS/'metricas_por_grupo.csv')
    uf=groups[(groups.recorte=='sigla_uf') & (~groups.amostra_pequena)].sort_values('recall_risco')
    fig,ax=plt.subplots(figsize=(10,5))
    ax.bar(uf.grupo,uf.recall_risco)
    ax.set(title='Recall de não alfabetização por UF no teste',ylabel='Recall',ylim=(0,1))
    ax.tick_params(axis='x',rotation=45)
    save(fig,'09_recortes_uf.png')
