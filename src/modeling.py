"""Previsão municipal do atingimento da meta no ano seguinte.

A Gold da Fase 2 é agregada: este módulo NÃO prevê alfabetização individual.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, classification_report, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import GroupShuffleSplit

KEY = ["id_municipio", "rede"]
NUMERIC_CANDIDATES = [
    "taxa_alfabetizacao", "meta_alfabetizacao", "media_portugues",
    "quantidade_alunos", "percentual_presenca_alunos",
    "taxa_alfabetizacao_alunos", "proficiencia_media_alunos",
    "peso_medio_alunos", "percentual_participacao",
    *[f"proporcao_aluno_nivel_{i}" for i in range(9)],
]


def read_gold(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, dtype={"id_municipio": "string"})
    raise ValueError("Use arquivo Gold .parquet ou .csv")


def prepare_pairs(gold: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str], list[str]]:
    """Une atributos do ano t ao resultado observado em t+1, sem usar variáveis futuras."""
    required = {*KEY, "ano", "taxa_alfabetizacao", "meta_alfabetizacao"}
    missing = required - set(gold)
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {sorted(missing)}")
    frame = gold.copy()
    frame["ano"] = pd.to_numeric(frame["ano"], errors="coerce")
    frame = frame.dropna(subset=["ano", *KEY])
    frame["ano"] = frame["ano"].astype(int)
    frame["id_municipio"] = frame["id_municipio"].astype("string").str.zfill(7)
    frame["rede"] = frame["rede"].astype("string")
    if frame.duplicated(["ano", *KEY]).any():
        raise ValueError("Gold contém duplicatas por ano, município e rede")
    frame["sigla_uf"] = frame["id_municipio"].str[:2].map({
        "11":"RO","12":"AC","13":"AM","14":"RR","15":"PA","16":"AP","17":"TO",
        "21":"MA","22":"PI","23":"CE","24":"RN","25":"PB","26":"PE","27":"AL",
        "28":"SE","29":"BA","31":"MG","32":"ES","33":"RJ","35":"SP","41":"PR",
        "42":"SC","43":"RS","50":"MS","51":"MT","52":"GO","53":"DF"})
    numeric = [c for c in NUMERIC_CANDIDATES if c in frame]
    for col in numeric:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    # Campos derivados de resultado, ranking e proficiência do próprio ano alvo
    # são excluídos. A meta futura só define o rótulo, jamais entra em X.
    future = frame[["ano", *KEY, "taxa_alfabetizacao", "meta_alfabetizacao"]].copy()
    future["ano"] -= 1
    future = future.rename(columns={"taxa_alfabetizacao": "resultado_futuro", "meta_alfabetizacao": "meta_futura"})
    labeled = frame.merge(future, on=["ano", *KEY], how="inner", validate="one_to_one")
    labeled = labeled.dropna(subset=["resultado_futuro", "meta_futura"])
    labeled["alvo"] = (labeled["resultado_futuro"] >= labeled["meta_futura"]).astype(int)
    # Campos inteiramente vazios no período de treino não fornecem sinal.
    numeric = [c for c in numeric if labeled[c].notna().any()]
    categorical = ["rede", "sigla_uf"]
    features = [*numeric, *categorical]
    if not labeled.empty and labeled["alvo"].nunique() < 2:
        raise ValueError("O alvo tem apenas uma classe; não é possível avaliar classificação")
    return labeled, frame, numeric, categorical


def build_pipeline(numeric: list[str], categorical: list[str], c: float = 1.0) -> Pipeline:
    pre = ColumnTransformer([
        ("num", Pipeline([("impute", SimpleImputer(strategy="median", keep_empty_features=True)),
                           ("scale", StandardScaler())]), numeric),
        ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                           ("encode", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])
    return Pipeline([("preprocess", pre), ("model", LogisticRegression(
        C=c, class_weight="balanced", max_iter=2000, random_state=42))])


def train(gold: pd.DataFrame, output: str | Path) -> dict:
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    labeled, frame, numeric, categorical = prepare_pairs(gold)
    years = sorted(labeled["ano"].unique())
    if not years:
        raise ValueError("Nenhum par ano t / ano t+1 com resultado e meta futuros foi encontrado")
    if len(years) >= 3:
        train_years, validation_year, test_year = years[:-2], years[-2], years[-1]
        train_df = labeled[labeled.ano.isin(train_years)]
        val_df = labeled[labeled.ano.eq(validation_year)]
        test_df = labeled[labeled.ano.eq(test_year)]
        validation_design = "temporal"
    else:
        # Com 1-2 coortes, não há três períodos independentes. Separamos
        # municípios inteiros para evitar o mesmo município em dois conjuntos.
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
        development_idx, test_idx = next(splitter.split(labeled, groups=labeled.id_municipio))
        development_df = labeled.iloc[development_idx]
        test_df = labeled.iloc[test_idx]
        splitter_val = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=43)
        train_idx, val_idx = next(splitter_val.split(
            development_df, groups=development_df.id_municipio))
        train_df = development_df.iloc[train_idx]
        val_df = development_df.iloc[val_idx]
        train_years = sorted(train_df.ano.unique())
        validation_year = None
        test_year = None
        validation_design = "municipios_disjuntos_mesmos_anos_sem_validacao_temporal"
    features = numeric + categorical
    if train_df.alvo.nunique() < 2:
        raise ValueError("Treino possui só uma classe")
    # Validação seleciona hiperparâmetro; teste permanece intocado até o fim.
    scores = []
    for c in (0.01, 0.1, 1.0, 10.0):
        candidate = build_pipeline(numeric, categorical, c).fit(train_df[features], train_df.alvo)
        pred = candidate.predict_proba(val_df[features])[:, 1]
        scores.append((brier_score_loss(val_df.alvo, pred), c))
    best_c = min(scores)[1]
    development = pd.concat([train_df, val_df], ignore_index=True)
    model = build_pipeline(numeric, categorical, best_c).fit(development[features], development.alvo)
    probability = model.predict_proba(test_df[features])[:, 1]
    predicted = (probability >= 0.5).astype(int)
    metrics = {
        "unit": "municipio-ano-rede", "target": "atingir_meta_no_ano_seguinte",
        "validation_design": validation_design,
        "train_years": [int(y) for y in train_years],
        "validation_year": int(validation_year) if validation_year is not None else None,
        "test_year": int(test_year) if test_year is not None else None,
        "test_cohort_years": [int(y) for y in sorted(test_df.ano.unique())],
        "limitation": "Sem validação temporal; resultados não comprovam generalização para anos futuros"
        if validation_design != "temporal" else None,
        "best_C": best_c,
        "n_train": len(train_df), "n_validation": len(val_df), "n_test": len(test_df),
        "brier": brier_score_loss(test_df.alvo, probability),
        "average_precision": average_precision_score(test_df.alvo, probability),
        "roc_auc": roc_auc_score(test_df.alvo, probability) if test_df.alvo.nunique() == 2 else None,
        "classification_report": classification_report(test_df.alvo, predicted, output_dict=True, zero_division=0),
    }
    importance = permutation_importance(model, test_df[features], test_df.alvo,
                                        scoring="neg_brier_score", n_repeats=5, random_state=42)
    pd.DataFrame({"feature": features, "importance_mean": importance.importances_mean,
                  "importance_std": importance.importances_std}).sort_values(
                      "importance_mean", ascending=False).to_csv(output / "importancia_variaveis.csv", index=False)
    risks = test_df[["ano", *KEY, "sigla_uf", "alvo"]].copy()
    risks["probabilidade_nao_atingir_meta"] = 1 - probability
    risks.sort_values("probabilidade_nao_atingir_meta", ascending=False).to_csv(
        output / "riscos_teste.csv", index=False)
    latest = frame[frame.ano.eq(frame.ano.max())].copy()
    latest["ano_previsto"] = latest.ano + 1
    latest["probabilidade_nao_atingir_meta"] = 1 - model.predict_proba(latest[features])[:, 1]
    latest[["ano", "ano_previsto", *KEY, "sigla_uf", "probabilidade_nao_atingir_meta"]].sort_values(
        "probabilidade_nao_atingir_meta", ascending=False
    ).to_csv(output / "riscos_proximo_ano.csv", index=False)
    joblib.dump({"model": model, "features": features, "source_year": int(frame.ano.max())}, output / "modelo.joblib")
    (output / "metricas.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    return metrics
