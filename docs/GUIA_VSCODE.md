# Execução pelo VS Code

1. Abra a pasta `tech-challenge-fase3` inteira no VS Code.
2. Selecione o interpretador Python em que as dependências já foram instaladas.
3. Confira o projeto GCP em `config.json`. Não coloque senhas, tokens ou arquivos de credenciais no repositório.
4. Abra `run_project.py` e clique em **Run Python File**. Não há argumentos obrigatórios.
5. Na primeira execução, `prepare_data.py` consulta a Gold e salva apenas perfis agregados em `data/perfis_alunos_v2.parquet`. Com esse cache e o cache das metas presentes, as execuções seguintes são locais.
6. Acompanhe as cinco etapas impressas. Ao terminar, abra `reports/final/relatorio_tecnico.html` no navegador ou `reports/final/relatorio_tecnico.md` no VS Code.
7. Para verificar as proteções, abra `verify_project.py` e clique em **Run Python File**.

## Arquivos de entrada

- `data/mart_alfabetizacao_municipio.parquet`: Gold da Fase 2, exportada por `export_bigquery.py`.
- `data/perfis_alunos_v2.parquet`: perfis da Gold individual enriquecida, consultados por `prepare_data.py`.
- `data/metas_municipais.parquet`: metas para cenários, consultadas por `prepare_data.py`.

## Se estiver reproduzindo em outro computador

O cache e o modelo não são versionados. É necessário acesso ao projeto BigQuery e às credenciais padrão do Google Cloud. O ambiente é descrito em `requirements-lock.txt`. A autenticação e a instalação de dependências são pré-requisitos de configuração do ambiente; os scripts de análise não pedem argumentos.

Se a Gold individual ainda não existir no seu projeto, execute `build_student_gold.py` depois de exportar a Gold municipal. A origem da Base dos Dados está em `US`; a Gold de ML também usa `US`, enquanto a Gold antiga permanece em `us-central1`.

## Resultados principais

- `metricas_teste.json`: resultados do modelo selecionado, baseline, limiar 0,5 e intervalos.
- `comparacao_validacao.csv`: comparação entre famílias.
- `busca_hiperparametros.csv`: validação cruzada das configurações.
- `risco_municipios_teste.csv`: ranking em municípios de teste.
- `cenario_metas2025.csv`: cenários condicionais para metas.
- `images/`: gráficos em PNG.
- `models/modelo_individual_final.joblib`: pipeline, features e limiar. Carregue apenas modelos confiáveis.
