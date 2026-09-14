# Tech Challenge Fase 3 — risco municipal de não atingir a meta

Este projeto reutiliza `mart_alfabetizacao_municipio`, a camada Gold do [Tech Challenge Fase 2](https://github.com/gabriel-duarte-martins/FIAP-AISCIENTIST-TECH-CHALLENGE-2). Cada linha representa **ano, município e rede**. O modelo estima, com indicadores conhecidos no ano `t`, a probabilidade de o município **não atingir a meta de alfabetização em `t+1`**.

**Extensão individual:** `build_student_gold.py` cria, no BigQuery, uma segunda Gold em `alfabetizacao_gold_ml.mart_alfabetizacao_aluno` com uma linha por aluno avaliado em 2024, rótulo `alfabetizado` e contexto municipal de 2023. `train_students.py` treina a partir de contagens agregadas, sem baixar microdados individuais. Resultados em `reports/alunos/metricas.json`. Veja [a arquitetura](docs/arquitetura_gold_fase3.md).

## Decisão metodológica

O enunciado da Fase 3 solicita classificação de alfabetização **por aluno**, mas a Gold original da Fase 2 publica apenas agregados municipais. A nova Gold individual resolve o problema do grão, sem publicar IDs de aluno ou escola. Porém, seus atributos individuais prévios são limitados: as previsões refletem principalmente o contexto do município, rede e série. O modelo municipal continua respondendo à pergunta estratégica sobre municípios que podem deixar de atingir metas futuras.

O modelo não interpreta importância estatística como efeito causal. Variáveis socioeconômicas adicionais não estão presentes na Gold atual; sua inclusão exigirá integração por município e ano com disponibilidade anterior ao período previsto.

## Dados e rótulo

- Fonte: `alfabetizacao_gold.mart_alfabetizacao_municipio` da Fase 2.
- Grão: `(ano, id_municipio, rede)`; duplicatas nessa chave geram erro.
- Rótulo: `1` se `taxa_alfabetizacao(t+1) >= meta_alfabetizacao(t+1)`; `0` caso contrário. Linhas sem resultado ou meta futuros são excluídas do treinamento.
- Atributos: indicadores observados em `t` da própria Gold, rede e UF. IDs são usados apenas para pareamento e relatório. `gap_para_meta`, `atingiu_meta`, rankings, classificações e todos os campos de `t+1` ficam fora dos atributos. Assim, o resultado futuro não vaza para o modelo.
- Limitação temporal: a Gold exportada contém 2023 e 2024, produzindo somente uma coorte rotulada (atributos de 2023, resultado de 2024). Nesse caso, o script separa municípios inteiros em treino, validação e teste. Isso avalia generalização entre municípios em 2024, **não entre anos**. Com ao menos três coortes rotuladas, a divisão muda automaticamente para temporal.

## Execução

Requer Python 3.12 e acesso à Gold da Fase 2. No VS Code, abra `export_bigquery.py` e clique em **Run Python File**. O script tenta identificar o projeto GCP pelas credenciais configuradas; se encontrar outro projeto ou não identificar nenhum, preencha `PROJECT_ID` no início do arquivo e execute novamente. O Parquet será salvo em `data/`. Depois, abra `train.py` e clique em **Run Python File**. Nenhum dos dois scripts exige argumentos.

Também é possível executar pelo terminal:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
gcloud auth application-default login
python export_bigquery.py --project SEU_PROJECT_ID
python train.py --gold data/mart_alfabetizacao_municipio.parquet
```

Também é possível fornecer um CSV ou Parquet local por `--gold`. Dados e modelos ficam fora do Git por padrão.

## Pipeline e avaliação

O pré-processamento integra o `Pipeline` do scikit-learn: mediana e escala para numéricos; moda e one-hot para categóricos. A regressão logística usa pesos balanceados e regularização; `C` é escolhido por Brier score na validação. Quando há histórico suficiente, a divisão é cronológica: anos anteriores para treino, penúltima coorte para validação e última para teste. Com a Gold atual, a divisão usa municípios disjuntos em proporção 60/20/20. Após selecionar `C`, treino e validação são reunidos para ajustar o modelo final; o teste é avaliado uma vez. A semente fixa torna a execução replicável.

Saídas em `reports/`: `metricas.json` (Brier, PR-AUC, ROC-AUC quando aplicável e precisão/recall/F1), `importancia_variaveis.csv` (permutação no teste), `riscos_teste.csv` e `riscos_proximo_ano.csv`. O último é uma pontuação prospectiva, **sem resultado observado ainda**. `modelo.joblib` contém o pipeline e metadados; carregue somente artefatos gerados por você.

As métricas de teste devem ser comparadas com a taxa-base de não atingimento e analisadas por UF e rede antes de qualquer uso operacional. Probabilidades podem precisar de calibração. A previsão para 2025 é apenas exploratória: o modelo foi treinado com o alvo de 2024 e não usa a meta futura de 2025 como atributo; mudanças nas metas ou no contexto podem alterar o risco real. Um risco alto deve orientar investigação e apoio pedagógico, nunca sanção automática.

## Exploração e hipóteses

Antes do treino, verificar cobertura anual, ausência de metas, distribuição do rótulo por ano/UF/rede, frequência de valores faltantes e evolução da taxa de alfabetização. Hipóteses a testar: desempenho anterior e proficiência média podem antecipar risco; baixa presença e desigualdade entre redes podem sinalizar vulnerabilidade. Esses são candidatos a associação, não conclusões causais.

## Estado desta entrega

O GitHub da Fase 2 contém código e documentação, mas não inclui o arquivo Gold. A exportação real feita no projeto contém 23.995 linhas de 2023 e 2024; há 5.232 pares rotulados 2023→2024. Para afirmar desempenho prospectivo, será preciso obter histórico adicional e refazer a avaliação temporal.

O enunciado também pede visualizações, documentação técnica, histórico de Git/branches/PRs e vídeo executivo de até 5 minutos. Esses itens dependem dos resultados reais e da entrega final do grupo.
