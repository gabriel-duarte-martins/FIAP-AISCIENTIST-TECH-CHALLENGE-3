# Reprodução no VS Code

O projeto é executado pelo arquivo `run_project.py` com **Run Python File**, sem argumentos obrigatórios. O interpretador precisa conter as versões de `requirements-lock.txt`, e o projeto GCP é definido em `config.json`. Senhas, tokens e arquivos de credenciais não fazem parte do repositório.

Na primeira execução, `prepare_data.py` consulta a Gold e salva somente perfis agregados em `data/perfis_alunos_v2.parquet`. Com os caches da Gold e das metas, as execuções seguintes são locais. O relatório é gravado em `reports/final/relatorio_tecnico.html` e `reports/final/relatorio_tecnico.md`. O contrato da modelagem é verificado por `verify_project.py`.

## Arquivos de entrada

- `data/mart_alfabetizacao_municipio.parquet`: Gold da Fase 2, exportada por `export_bigquery.py`.
- `data/perfis_alunos_v2.parquet`: perfis da Gold individual enriquecida, consultados por `prepare_data.py`.
- `data/metas_municipais.parquet`: metas para cenários, consultadas por `prepare_data.py`.

## Se estiver reproduzindo em outro computador

O cache e o modelo não são versionados. É necessário acesso ao projeto BigQuery e às credenciais padrão do Google Cloud. O ambiente é descrito em `requirements-lock.txt`. A autenticação e a instalação de dependências são pré-requisitos de configuração do ambiente; os scripts de análise não pedem argumentos.

Quando a Gold individual ainda não existe, `build_student_gold.py` realiza sua materialização após a exportação da Gold municipal. A origem da Base dos Dados está em `US`; a Gold de ML também usa `US`, enquanto a Gold antiga permanece em `us-central1`.

## Resultados principais

- `metricas_teste.json`: resultados do modelo selecionado, baseline, limiar 0,5 e intervalos.
- `comparacao_validacao.csv`: comparação entre famílias.
- `busca_hiperparametros.csv`: validação cruzada das configurações.
- `risco_municipios_teste.csv`: ranking em municípios de teste.
- `cenario_metas2025.csv`: cenários condicionais para metas.
- `images/`: gráficos em PNG.
- `models/modelo_individual_final.joblib`: pipeline, features e limiar. Carregue apenas modelos confiáveis.
