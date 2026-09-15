import argparse
import json
from pathlib import Path
from src.modeling import read_gold, train

BASE_DIR = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--gold", default=str(BASE_DIR / "data" / "mart_alfabetizacao_municipio.parquet"))
parser.add_argument("--output", default=str(BASE_DIR / "reports"))
args = parser.parse_args()
print(json.dumps(train(read_gold(args.gold), args.output), ensure_ascii=False, indent=2))
