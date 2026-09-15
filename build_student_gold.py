"""Cria a Gold individual no BigQuery pelo botão Run Python File do VS Code.

Microdados não são baixados. A tabela final não contém ID de aluno/escola.
Se a tabela final já existir, a execução para sem substituí-la.
"""
from pathlib import Path

import pandas as pd
from google.api_core.exceptions import NotFound
from google.cloud import bigquery

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ID = "sharp-gecko-439920-j4"
DATASET_ID = "alfabetizacao_gold_ml"
LOCATION = "US"
MUNICIPAL_PARQUET = BASE_DIR / "data" / "mart_alfabetizacao_municipio.parquet"
DEST = f"{PROJECT_ID}.{DATASET_ID}.mart_alfabetizacao_aluno"
CONTEXT = f"{PROJECT_ID}.{DATASET_ID}.contexto_municipal_2023"


def main() -> None:
    if not MUNICIPAL_PARQUET.exists():
        raise SystemExit(f"Gold municipal não encontrada: {MUNICIPAL_PARQUET}")
    client = bigquery.Client(project=PROJECT_ID, location=LOCATION)
    try:
        client.get_table(DEST)
    except NotFound:
        pass
    else:
        raise SystemExit(f"A tabela {DEST} já existe. Nenhum dado foi substituído.")

    frame = pd.read_parquet(MUNICIPAL_PARQUET)
    frame = frame.loc[frame["ano"].eq(2023), [
        "ano", "id_municipio", "rede", "taxa_alfabetizacao",
        "media_portugues", "percentual_presenca_alunos", "quantidade_alunos",
    ]].copy()
    frame = frame.rename(columns={
        "taxa_alfabetizacao": "taxa_alfabetizacao_municipio_ano_anterior",
        "media_portugues": "media_portugues_municipio_ano_anterior",
        "percentual_presenca_alunos": "presenca_municipio_ano_anterior",
        "quantidade_alunos": "quantidade_alunos_ano_anterior",
    })
    frame["id_municipio"] = frame["id_municipio"].astype("string")
    frame["rede"] = frame["rede"].astype("string")
    if frame.duplicated(["ano", "id_municipio", "rede"]).any():
        raise ValueError("Contexto municipal de 2023 tem chaves duplicadas")
    for column in frame.columns.difference(["ano", "id_municipio", "rede"]):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    dataset = bigquery.Dataset(f"{PROJECT_ID}.{DATASET_ID}")
    dataset.location = LOCATION
    client.create_dataset(dataset, exists_ok=True)
    print(f"Enviando {len(frame)} linhas agregadas de 2023 para {CONTEXT} ...")
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    client.load_table_from_dataframe(frame, CONTEXT, job_config=job_config, location=LOCATION).result()

    sql = (BASE_DIR / "sql" / "mart_alfabetizacao_aluno.sql").read_text(encoding="utf-8")
    sql = sql.replace("PROJECT_ID", PROJECT_ID)
    dry_run = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    estimated = client.query(sql, job_config=dry_run, location=LOCATION).total_bytes_processed
    print(f"Consulta validada; leitura estimada: {estimated / 1e9:.2f} GB")
    print(f"Criando {DEST} ...")
    client.query(sql, location=LOCATION).result()
    checks = client.query(f"""
        SELECT COUNT(*) AS linhas, COUNTIF(alvo_alfabetizado = 1) AS alfabetizados,
               COUNTIF(alvo_alfabetizado = 0) AS nao_alfabetizados,
               COUNTIF(taxa_alfabetizacao_municipio_ano_anterior IS NOT NULL)
                 AS com_contexto_anterior,
               COUNT(DISTINCT id_municipio) AS municipios
        FROM `{DEST}`
    """, location=LOCATION).result()
    row = next(iter(checks))
    print(f"Gold criada: {DEST}")
    print({name: row[name] for name in (
        "linhas", "alfabetizados", "nao_alfabetizados",
        "com_contexto_anterior", "municipios")})


if __name__ == "__main__":
    main()
