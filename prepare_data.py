"""Run Python File: materializa a Gold de perfis e salva o cache agregado local."""
import hashlib
import json
from datetime import datetime, timezone

import pandas as pd
from google.api_core.exceptions import NotFound
from google.cloud import bigquery
from src.config import CONFIG, ROOT, DATA, REPORTS, FEATURES


def prepare():
    DATA.mkdir(exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = DATA / 'perfis_alunos_v2.parquet'
    if path.exists():
        print('Cache local encontrado. Para uma atualização explícita, arquive o cache atual primeiro.')
        return path
    project = CONFIG['project_id']
    client = bigquery.Client(project=project, location=CONFIG['location'])
    table = f"{project}.{CONFIG['dataset']}.{CONFIG['profile_gold']}"
    sql = (ROOT / 'sql' / 'perfis_enriquecidos.sql').read_text(encoding='utf-8').replace('PROJECT_ID', project)
    jobs = []
    try:
        client.get_table(table)
    except NotFound:
        try:
            client.get_table(f"{project}.{CONFIG['dataset']}.{CONFIG['student_gold']}")
        except NotFound:
            from build_student_gold import main as build_gold
            build_gold()
        dry = client.query(sql, job_config=bigquery.QueryJobConfig(dry_run=True), location='US')
        print(f'Leitura estimada do enriquecimento: {dry.total_bytes_processed/1e9:.3f} GB')
        job = client.query(sql, job_config=bigquery.QueryJobConfig(
            destination=table, write_disposition='WRITE_EMPTY', maximum_bytes_billed=5_000_000_000))
        job.result()
        jobs.append(job.job_id)
    frame = client.query(f'SELECT * FROM `{table}` ORDER BY id_municipio,rede,serie,alvo_alfabetizado').to_dataframe()
    if frame.peso.sum() != client.get_table(f"{project}.{CONFIG['dataset']}.{CONFIG['student_gold']}").num_rows:
        raise ValueError('A integração alterou a contagem de alunos. Verifique cardinalidade dos joins.')
    key = ['ano','id_municipio','rede','serie','alvo_alfabetizado']
    if frame.duplicated(key).any() or frame.id_municipio.isna().any():
        raise ValueError('Chaves inválidas ou duplicadas após integração')
    frame.to_parquet(path,index=False)
    meta = {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'gold_table': table, 'query_jobs':jobs,
        'query_sha256':hashlib.sha256(sql.encode()).hexdigest(),
        'data_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'profiles':len(frame),'students':int(frame.peso.sum()),
        'municipalities':int(frame.id_municipio.nunique()),
        'weighted_missing':{f:float(frame.loc[frame[f].isna(),'peso'].sum()/frame.peso.sum()) for f in FEATURES},
        'years':{'target':2024,'education_context':2023,'GDP':2021,'population':2022},
        'note':'Contagens de observações elegíveis, não pesos amostrais do Inep. Séries históricas na versão consultada; vintages não recuperadas.'
    }
    (REPORTS/'linhagem_dados.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(meta,ensure_ascii=False,indent=2))
    return path


def prepare_targets():
    path=DATA/'metas_municipais.parquet'
    if not path.exists():
        client=bigquery.Client(project=CONFIG['project_id'],location='US')
        sql='''SELECT ano,id_municipio,rede,meta_alfabetizacao_2025
        FROM `basedosdados.br_inep_avaliacao_alfabetizacao.meta_alfabetizacao_municipio`'''
        client.query(sql).to_dataframe().to_parquet(path,index=False)
    return path


if __name__=='__main__':
    prepare()
    prepare_targets()
