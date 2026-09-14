import argparse
from pathlib import Path
from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from src.config import CONFIG

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ID = CONFIG['project_id']

parser = argparse.ArgumentParser()
parser.add_argument("--project", default=None, help="ID do projeto GCP da Fase 2")
parser.add_argument("--output", default=str(BASE_DIR / "data" / "mart_alfabetizacao_municipio.parquet"))
args = parser.parse_args()
try:
    client = bigquery.Client(project=args.project or PROJECT_ID or None)
except Exception as exc:
    raise SystemExit(
        "Não foi possível identificar o projeto GCP. Preencha PROJECT_ID no início "
        "de export_bigquery.py e confirme que as credenciais do Google Cloud estão configuradas."
    ) from exc
table = f"{client.project}.alfabetizacao_gold.mart_alfabetizacao_municipio"
dataset_id = f"{client.project}.alfabetizacao_gold"
try:
    dataset = client.get_dataset(dataset_id)
except NotFound as exc:
    try:
        datasets = sorted(item.dataset_id for item in client.list_datasets())
        available = ", ".join(datasets) if datasets else "nenhum dataset encontrado"
    except Exception:
        available = "não foi possível listar os datasets"
    raise SystemExit(
        f"O dataset {dataset_id} não existe ou sua conta não tem acesso a ele.\n"
        f"Datasets visíveis em {client.project}: {available}.\n"
        "Confira se PROJECT_ID aponta para o projeto usado na Fase 2. "
        "Se estiver correto e a Gold não aparecer, execute novamente a etapa Gold "
        "da pipeline da Fase 2 antes de exportar."
    ) from exc
print(f"Lendo {table} na região {dataset.location} ...")
frame = client.query(
    f"SELECT * FROM `{table}`", location=dataset.location
).to_dataframe()
Path(args.output).parent.mkdir(parents=True, exist_ok=True)
frame.to_parquet(args.output, index=False)
print(f"{len(frame)} linhas exportadas de {table} para {args.output}")
