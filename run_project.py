"""Run Python File: execução completa, com cache agregado local e sem argumentos."""
import hashlib
import json
import platform
import os
os.environ.setdefault('LOKY_MAX_CPU_COUNT',str(os.cpu_count() or 1))
from datetime import datetime,timezone
import importlib.metadata
import pandas as pd
from prepare_data import prepare,prepare_targets
from src.config import REPORTS, ROOT, NUMERIC, CATEGORICAL
from src.preprocessing import split_profiles
from src.visualization.charts import eda,evaluation
from src.modeling.students import run_models,importance
from src.evaluation.business import business


def main():
    path=prepare()
    prepare_targets()
    frame=pd.read_parquet(path)
    for col in NUMERIC:
        frame[col]=pd.to_numeric(frame[col],errors='coerce').astype(float)
    frame['peso']=frame.peso.astype(float)
    frame['alvo_alfabetizado']=frame.alvo_alfabetizado.astype(int)
    parts=split_profiles(frame)
    partition=pd.concat([p[['id_municipio']].drop_duplicates().assign(particao=name) for name,p in parts.items()])
    partition.sort_values('id_municipio').to_csv(REPORTS/'particoes_municipios.csv',index=False)
    summary={name:{'perfis':len(p),'alunos':int(p.peso.sum()),'municipios':p.id_municipio.nunique()} for name,p in parts.items()}
    (REPORTS/'particoes_resumo.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print('1/5: análise exploratória do treino',flush=True)
    eda(parts['treino'])
    print('2/5: comparação de modelos e validação por município',flush=True)
    model,final,p=run_models(parts)
    print('3/5: interpretação e visualizações',flush=True)
    imp=importance(model,parts['teste'])
    evaluation(parts['teste'],p,final,imp)
    print('4/5: análises territoriais',flush=True)
    ranks,k=business(frame,model,parts)
    versions={x:importlib.metadata.version(x) for x in ['pandas','numpy','scikit-learn','pyarrow','matplotlib','joblib','google-cloud-bigquery']}
    manifest={'executed_at_utc':datetime.now(timezone.utc).isoformat(),'python':platform.python_version(),
              'packages':versions,'data_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
              'partitions':summary,'winner':final['modelo'],'clusters':k}
    (REPORTS/'execucao.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print('5/5: relatórios',flush=True)
    from src.reporting import generate_report
    generate_report(final,manifest,imp,ranks)
    print(json.dumps(final,indent=2,ensure_ascii=False))


if __name__=='__main__':
    main()
