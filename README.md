# Tech Challenge Fase 3 — Alfabetização no Brasil

Projeto de Gabriel Duarte Carneiro Martins — RM372453.

Classificação supervisionada de alfabetização em 2024 usando contexto educacional anterior, territorial e socioeconômico. A pipeline reutiliza a Gold do [Tech Challenge Fase 2](https://github.com/gabriel-duarte-martins/FIAP-AISCIENTIST-TECH-CHALLENGE-2) e acrescenta uma Gold individual e outra de perfis ponderados no BigQuery.

## Resultado principal

A regressão logística foi selecionada na validação por Brier score. O teste abrange 330.968 observações de alunos de 1.104 municípios que não aparecem no treino nem na validação.

| Métrica de teste | Baseline de prevalência | Modelo com limiar 0,5 | Modelo com limiar 0.38 |
|---|---:|---:|---:|
| Acurácia | 61.9% | 65.1% | 58.3% |
| Acurácia balanceada | 50.0% | 58.1% | 60.5% |
| Recall de não alfabetização | 0,0% | 28.6% | 69.6% |
| Precisão de risco | 0,0% | 58.7% | 46.9% |
| Fração sinalizada | 0,0% | 18.6% | 56.6% |
| Brier score | 0.237 | 0.220 | 0.220 |
| ROC-AUC | 0,500 | 0.649 | 0.649 |

O limiar menor aumenta o recall, mas também a demanda potencial por acompanhamento. É uma simulação estatística, não uma regra de política pública. O IC 95% municipal para ROC-AUC foi 0.612–0.682. O modelo tem capacidade discriminatória limitada e deve apoiar investigação contextual.

## Contexto e objetivo analítico

Gestores precisam identificar contextos de vulnerabilidade educacional e organizar apoio pedagógico. O alvo principal é `alvo_alfabetizado`: 1 significa alfabetizado, 0 não alfabetizado. Para os relatórios de risco, usamos `1 - P(alfabetizado)`. Não é uma avaliação individual diagnóstica: crianças com os mesmos atributos contextuais recebem a mesma probabilidade.

## Base utilizada

- Origem: [Avaliação da Alfabetização — Base dos Dados](https://basedosdados.org/dataset/073a39d4-89cf-4068-b1e8-34ed0d9c0b72), com 3.867.999 registros de 2023 e 2024.
- População elegível: 1.852.788 presentes com rótulo válido em 2024, em 5.517 municípios.
- Gold individual: `alfabetizacao_gold_ml.mart_alfabetizacao_aluno`; não publica IDs de aluno/escola.
- Gold local de modelagem: 12.989 perfis de atributos e rótulo, com contagem `peso`; representa todos os elegíveis, sem amostragem.
- Atributos anteriores: alfabetização, português, presença e quantidade de alunos em 2023.
- Enriquecimento: PIB/composição econômica de 2021 e população de 2022, com cobertura de 100% na base.
- Metas de 2025 são usadas em cenários estratégicos, fora do classificador individual.

O contexto municipal veio da Gold da Fase 2 em `us-central1`. Como a origem da Base dos Dados está em `US`, apenas o contexto agregado foi copiado para a Gold de ML em `US`. O tratamento individual acontece no BigQuery.

## Execução no VS Code

1. Abra esta pasta inteira no VS Code e selecione o interpretador Python configurado.
2. Confira `project_id` em `config.json`.
3. Abra **run_project.py** e clique em **Run Python File**. Não exige argumentos.
4. Abra **verify_project.py** e clique em **Run Python File** para executar os testes.
5. Veja `reports/final/relatorio_tecnico.html` ou o Markdown e os gráficos em `images/`.

O cache agregado em `data/` permite repetir a análise localmente. Em outro computador, é necessário instalar `requirements-lock.txt` e configurar credenciais GCP para a primeira coleta. Detalhes em [Guia do VS Code](docs/GUIA_VSCODE.md).

## Etapas da modelagem

1. Auditoria de chaves, rótulos, contagens e cardinalidade dos joins.
2. Partições de municípios disjuntos em aproximadamente 60/20/20; proporções de alunos podem diferir.
3. EDA do treino: distribuições ponderadas, faltantes e correlações.
4. Pipeline com mediana e escala ponderadas, log1p, indicadores de ausência e one-hot.
5. Baseline, regressão logística e HistGradientBoosting; otimização com GroupKFold de três dobras no treino.
6. Seleção de família e limiar na validação, preservando o teste para avaliação.
7. Métricas ponderadas, bootstrap por município, calibração, recortes por UF/rede e importância por permutação.
8. Rankings de risco, agrupamentos territoriais e cenários para metas de 2025.

## Escolha do algoritmo

A regressão logística regularizada teve o menor Brier na validação, com diferença muito pequena para o boosting. A escolha favoreceu o critério declarado antes do teste. Os resultados das configurações estão em `reports/final/busca_hiperparametros.csv`; a comparação das famílias, em `comparacao_validacao.csv`.

## Insights e aplicação prática

A média municipal anterior de português e a UF tiveram maior importância por permutação. As diferenças de recall entre UFs são grandes, portanto uma regra única de risco não tem o mesmo comportamento em todos os territórios. Identificamos três grupos descritivos de municípios por porte e estrutura econômica. Os relatórios apoiam definição de prioridades para investigação, formação docente e apoio pedagógico; associações preditivas não medem efeitos causais.

Para metas futuras, `cenario_metas2025.csv` compara a taxa observada de 2024 com as metas de 2025 sob estabilidade ou aumento de 5/10 pontos percentuais. Isso é análise de cenário, não uma previsão validada de 2025.

## Limitações

- Poucos atributos próprios da criança; previsões essencialmente contextuais.
- Uma única coorte de modelagem e nenhuma validação temporal.
- O teste foi consultado na versão inicial do projeto: esta revisão é exploratória, não confirmatória.
- Séries históricas consultadas na versão atual; datas exatas de disponibilidade dos indicadores educacionais não foram recuperadas.
- Apenas presentes com rótulo válido; a população não representa automaticamente todas as crianças brasileiras.
- `peso` é multiplicidade de registros, não peso amostral do Inep.
- Presença e quantidade anteriores ausentes para 23,17% dos alunos; rede privada com 24 observações, insuficiente para análise própria.

## Evoluções futuras

Adicionar novas coortes, dados prévios da trajetória individual com vínculo e governança adequados, enriquecer o contexto escolar, validar externamente, analisar intervenções com desenhos causais e monitorar calibração e diferenças regionais de erro.

## Organização e entregáveis

```text
data/                 caches agregados, fora do Git
notebooks/            roteiro das análises executáveis
src/
  preprocessing/      transformação ponderada e partições
  modeling/           modelos individual e municipal complementar
  evaluation/         métricas, bootstrap e análises estratégicas
  visualization/      gráficos
reports/final/        relatório, métricas, tabelas e linhagem
images/               11 gráficos em PNG
models/               pipeline serializada, fora do Git
docs/                 checklist, decisões, dicionário e roteiro executivo
sql/                  consultas da Gold
tests/                testes do contrato de modelagem
config.json           projeto GCP e parâmetros
run_project.py        ponto de entrada principal
verify_project.py     testes pelo VS Code
```

O modelo municipal inicial (`train.py`) é um experimento complementar preservado no histórico; o ponto de entrada da entrega final é `run_project.py`.

## Documentação e reprodução

- [Checklist do enunciado](docs/CHECKLIST_ENTREGA.md)
- [Relatório técnico](reports/final/relatorio_tecnico.md)
- [Decisões e limites metodológicos](docs/DECISOES_METODOLOGICAS.md)
- [Dicionário da base](docs/DICIONARIO_DADOS.md)
- [Roteiro do vídeo executivo](docs/ROTEIRO_VIDEO.md)
- `reports/final/execucao.json`: versões e hash dos dados.
- `requirements-lock.txt`: versões de dependências usadas.

Os testes verificam isolamento de municípios, exclusão de atributos proibidos, categorias inéditas e equivalência entre perfis ponderados e registros expandidos na regressão logística.

## Apresentação e evidências de entrega

- [Relatório Word](reports/final/Relatorio_Tecnico_Fase3.docx)
- [Vídeo executivo de 4min35s](media/video_executivo.mp4), com narração sintética em português identificada e roteiro para revisão ou regravação pelo grupo.
- [Verificação da reprodução sem rede](reports/final/verificacao_reproducibilidade.json)

A base agregada e o modelo serializado ficam no ambiente local e não são publicados no Git. As consultas permitem refazer a coleta com acesso autorizado ao BigQuery.
