"""Treina o modelo individual contextual pelo botão Run Python File do VS Code.

Consulta contagens agregadas no BigQuery; não baixa linhas de alunos nem IDs.
"""
import json
from pathlib import Path

import joblib
import numpy as np
from google.cloud import bigquery
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, average_precision_score, brier_score_loss,
    classification_report, roc_auc_score,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ID = "sharp-gecko-439920-j4"
TABLE = f"{PROJECT_ID}.alfabetizacao_gold_ml.mart_alfabetizacao_aluno"
OUTPUT = BASE_DIR / "reports" / "alunos"
NUMERIC = [
    "taxa_alfabetizacao_municipio_ano_anterior",
    "media_portugues_municipio_ano_anterior",
    "presenca_municipio_ano_anterior",
    "quantidade_alunos_ano_anterior",
]
CATEGORICAL = ["codigo_uf", "rede", "serie"]
FEATURES = NUMERIC + CATEGORICAL


def pipeline(c: float) -> Pipeline:
    pre = ColumnTransformer([
        ("num", Pipeline([
            ("impute", SimpleImputer(strategy="median", keep_empty_features=True)),
            ("scale", StandardScaler()),
        ]), NUMERIC),
        ("cat", Pipeline([
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]), CATEGORICAL),
    ])
    return Pipeline([("preprocess", pre),
                     ("model", LogisticRegression(C=c, max_iter=2000, random_state=42))])


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    client = bigquery.Client(project=PROJECT_ID, location="US")
    sql = f"""
        SELECT ano, id_municipio, codigo_uf, rede, serie,
               taxa_alfabetizacao_municipio_ano_anterior,
               media_portugues_municipio_ano_anterior,
               presenca_municipio_ano_anterior,
               quantidade_alunos_ano_anterior,
               alvo_alfabetizado, COUNT(*) AS peso
        FROM `{TABLE}`
        GROUP BY ALL
    """
    frame = client.query(sql, location="US").to_dataframe()
    print(f"Recebidos {len(frame)} grupos que representam {int(frame.peso.sum())} alunos")
    for col in NUMERIC + ["peso"]:
        frame[col] = np.asarray(frame[col], dtype=float)
    frame["alvo_alfabetizado"] = frame["alvo_alfabetizado"].astype(int)
    groups = frame.id_municipio.astype(str)
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    development_idx, test_idx = next(splitter.split(frame, groups=groups))
    development, test = frame.iloc[development_idx], frame.iloc[test_idx]
    splitter_val = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=43)
    train_idx, val_idx = next(splitter_val.split(
        development, groups=development.id_municipio.astype(str)))
    train, validation = development.iloc[train_idx], development.iloc[val_idx]
    if any(part.alvo_alfabetizado.nunique() < 2 for part in (train, validation, test)):
        raise ValueError("Uma das partições contém apenas uma classe")
    scores = []
    for c in (0.01, 0.1, 1.0, 10.0):
        candidate = pipeline(c)
        candidate.fit(train[FEATURES], train.alvo_alfabetizado,
                      model__sample_weight=train.peso)
        p = candidate.predict_proba(validation[FEATURES])[:, 1]
        scores.append((brier_score_loss(validation.alvo_alfabetizado, p,
                                        sample_weight=validation.peso), c))
    best_c = min(scores)[1]
    model = pipeline(best_c)
    model.fit(development[FEATURES], development.alvo_alfabetizado,
              model__sample_weight=development.peso)
    probability = model.predict_proba(test[FEATURES])[:, 1]
    predicted = (probability >= 0.5).astype(int)
    metrics = {
        "target": "alfabetizado_em_2024",
        "unit": "aluno_presente_com_rotulo_valido",
        "validation_design": "municipios_disjuntos_mesmo_ano",
        "limitation": "Risco contextual; sem atributos individuais prévios nem validação temporal",
        "n_students": int(frame.peso.sum()),
        "n_train": int(train.peso.sum()),
        "n_validation": int(validation.peso.sum()),
        "n_test": int(test.peso.sum()),
        "n_municipalities_test": int(test.id_municipio.nunique()),
        "best_C": best_c,
        "accuracy": accuracy_score(test.alvo_alfabetizado, predicted,
                                   sample_weight=test.peso),
        "brier": brier_score_loss(test.alvo_alfabetizado, probability,
                                  sample_weight=test.peso),
        "roc_auc": roc_auc_score(test.alvo_alfabetizado, probability,
                                 sample_weight=test.peso),
        "average_precision": average_precision_score(test.alvo_alfabetizado,
                                                       probability, sample_weight=test.peso),
        "class_report": classification_report(
            test.alvo_alfabetizado, predicted, sample_weight=test.peso,
            output_dict=True, zero_division=0),
    }
    (OUTPUT / "metricas.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    joblib.dump({"model": model, "features": FEATURES, "source_table": TABLE},
                OUTPUT / "modelo.joblib")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
