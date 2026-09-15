import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from src.config import REPORTS, IMAGES, TARGET, WEIGHT, DATA
from src.modeling.students import predict
from src.visualization.charts import save


def business(frame,model,parts):
    scoring=frame.copy()
    scoring['risco']=1-predict(model,frame)
    assignment={id:name for name,part in parts.items() for id in part.id_municipio.unique()}
    rows=[]
    for id,sub in scoring.groupby('id_municipio'):
        w=sub[WEIGHT]
        rows.append({'id_municipio':id,'nome_municipio':sub.nome_municipio.iloc[0],
                     'sigla_uf':sub.sigla_uf.iloc[0],'regiao':sub.nome_regiao.iloc[0],
                     'particao':assignment[id],'alunos':int(w.sum()),
                     'risco_contextual_2024':np.average(sub.risco,weights=w),
                     'fracao_observada_nao_alfabetizado':np.average(1-sub[TARGET],weights=w)})
    ranks=pd.DataFrame(rows).sort_values('risco_contextual_2024',ascending=False)
    ranks.to_csv(REPORTS/'risco_municipios_2024.csv',index=False)
    ranks[ranks.particao=='teste'].to_csv(REPORTS/'risco_municipios_teste.csv',index=False)
    # Perfil territorial descritivo: sem utilizar o alvo de 2024.
    columns=['pib_per_capita_2021','populacao_2022','participacao_agro_2021','participacao_industria_2021','participacao_publica_2021']
    cities=frame.drop_duplicates('id_municipio').copy()
    X=cities[columns].to_numpy(dtype=float)
    X[:,:2]=np.log1p(X[:,:2])
    X=StandardScaler().fit_transform(SimpleImputer(strategy='median').fit_transform(X))
    scores=[]; estimators={}
    for k in range(2,7):
        estimator=KMeans(n_clusters=k,n_init=10,random_state=42).fit(X)
        score=silhouette_score(X,estimator.labels_,sample_size=min(2000,len(X)),random_state=42)
        scores.append({'k':k,'silhouette':score}); estimators[k]=estimator
    best=max(scores,key=lambda x:x['silhouette'])['k']
    cities['cluster']=estimators[best].labels_
    cities[['id_municipio','nome_municipio','sigla_uf','nome_regiao','cluster']].to_csv(REPORTS/'clusters_municipios.csv',index=False)
    pd.DataFrame(scores).to_csv(REPORTS/'selecao_clusters.csv',index=False)
    cities.groupby('cluster')[columns].median().to_csv(REPORTS/'perfis_clusters.csv')
    pd.crosstab(cities.nome_regiao,cities.cluster,normalize='index').to_csv(REPORTS/'clusters_por_regiao.csv')
    fig,ax=plt.subplots(figsize=(8,5))
    for cluster,sub in cities.groupby('cluster'):
        ax.scatter(sub.populacao_2022,sub.pib_per_capita_2021,s=12,alpha=.4,label=f'Grupo {cluster}')
    ax.set(xscale='log',yscale='log',xlabel='População 2022',ylabel='PIB per capita 2021 (R$)',title='Municípios com perfis socioeconômicos semelhantes')
    ax.legend(); save(fig,'10_perfis_territoriais.png')
    observed=pd.read_parquet(DATA/'mart_alfabetizacao_municipio.parquet')
    observed=observed[observed.ano.eq(2024)].copy()
    targets=pd.read_parquet(DATA/'metas_municipais.parquet')
    targets['rede']=targets.rede.astype(str).replace({'0':'Total','1':'Federal','2':'Estadual','3':'Municipal','4':'Privada','5':'Pública'})
    targets=targets.sort_values('ano').drop_duplicates(['id_municipio','rede'],keep='last')
    scenario=observed[['id_municipio','rede','taxa_alfabetizacao']].merge(
        targets[['id_municipio','rede','meta_alfabetizacao_2025']],on=['id_municipio','rede'],validate='one_to_one')
    scenario=scenario.dropna(subset=['taxa_alfabetizacao','meta_alfabetizacao_2025'])
    scenario['gap_necessario_pp']=scenario.meta_alfabetizacao_2025-scenario.taxa_alfabetizacao
    scenario['nao_atingiria_sem_crescimento']=scenario.gap_necessario_pp>0
    scenario=scenario.merge(cities[['id_municipio','nome_municipio','sigla_uf']],on='id_municipio',validate='many_to_one')
    scenario.sort_values('gap_necessario_pp',ascending=False).to_csv(REPORTS/'cenario_metas2025.csv',index=False)
    if len(scenario):
        fig,ax=plt.subplots(figsize=(8,4))
        ax.bar(['Sem crescimento','+5 pontos percentuais','+10 pontos percentuais'],[(scenario.gap_necessario_pp>gain).sum() for gain in [0,5,10]])
        ax.set(title='Cenários para metas de 2025 — não são previsões validadas',ylabel='Pares município/rede abaixo da meta')
        save(fig,'11_cenarios_metas.png')
    return ranks,best
