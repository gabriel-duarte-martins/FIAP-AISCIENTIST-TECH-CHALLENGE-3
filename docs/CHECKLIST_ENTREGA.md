# Checklist da entrega do Tech Challenge Fase 3

Referência: enunciado [IAST] Tech Challenge Fase 3, páginas 2 a 8. Atualizado em 14/09/2026. Os resultados são de uma execução real com os dados descritos abaixo.

| Etapa | Atendimento | Evidência | Situação |
|---|---|---|---|
| 1 Problema e alvo | Alfabetização por aluno elegível em 2024; finalidade contextual | README e relatório técnico | Concluído |
| 2 Gold da Fase 2 | Contexto de 2023 integrado à Gold individual; grão e regiões rastreados | SQL, arquitetura e linhagem_dados.json | Concluído |
| 3 Enriquecimento | PIB/composição 2021 e população 2022; cobertura 100% | perfis_enriquecidos.sql e dicionário | Concluído |
| 4 EDA | Distribuições, faltantes, correlações, hipóteses e decisões no treino | images/01 a 04 e CSVs exploratórios | Concluído |
| 5 Preparação | Imputação ponderada, log1p, escala, indicadores de ausência e one-hot integrados | src/preprocessing | Concluído |
| 6 Vazamento | Proficiência contemporânea excluída; municípios disjuntos; ajuste só no treino | Lista permitida, partições e testes | Concluído |
| 7 Modelagem | Baseline, logística e boosting; busca em três dobras por município | busca_hiperparametros.csv e comparacao_validacao.csv | Concluído |
| 8 Avaliação | Métricas, limiares, bootstrap municipal, calibração e recortes UF/rede | metricas_teste.json e images/05 a 09 | Concluído |
| 9 Explicabilidade | Importância por permutação contextual; associação sem causalidade | importancia_permutacao.csv | Concluído |
| 10 Negócio | Cinco perguntas; risco, grupos semelhantes e cenários de metas | Relatório, rankings, clusters e cenários | Concluído com limites explícitos |
| 11 Organização | data, notebooks, módulos src, reports, images e configuração | Estrutura do repositório | Concluído |
| 12 Reprodução | Cache, versões, sementes, hashes e repetição sem rede | execucao.json e verificacao_reproducibilidade.json | Concluído |
| 13 README | Contexto, base, preparo, algoritmo, métricas, insights, uso, limites, evolução, reprodução e organização | README.md | Concluído |
| 14 Relatório | Relatório técnico em Markdown, HTML e Word; dicionário e decisões | reports/final e docs | Concluído |
| 15 Git | Histórico inicial e branch de entrega; publicação e PR | Repositório GitHub e histórico real | Publicação final em andamento |
| 16 Vídeo executivo | Problema, insights, valor estratégico e uso público em 4min35s | media/video_executivo.mp4 e roteiro | Vídeo pronto com voz sintética; revisão do grupo pendente |

## Verificação executada

- A fonte original tem 3.867.999 registros em 2023 e 2024; a Gold usada representa 1.852.788 elegíveis de 2024.
- Não há municípios compartilhados entre treino, validação e teste.
- Os quatro testes do contrato passaram, incluindo equivalência da logística ponderada com dados expandidos em um caso controlado.
- A repetição completa com a conexão de rede bloqueada reproduziu exatamente os hashes das métricas, partições e comparação de modelos.
- Os 11 gráficos foram conferidos visualmente. O relatório Word foi renderizado para conferência de todas as páginas.
- O vídeo tem narração sintética identificada; não é uma gravação feita pelo grupo.

## Limites que não devem ser ocultados na apresentação

O modelo prevê alfabetização usando principalmente contexto, sem trajetória individual anterior. Não há validação temporal. O teste foi consultado na versão inicial e esta revisão é exploratória. A fonte histórica foi consultada na versão atual, sem reconstrução completa da disponibilidade original. As metas de 2025 entram somente em cenários. A importância das variáveis não identifica causas.

## Ações finais do grupo

Revisar a apresentação, conferir identificação dos integrantes e substituir a narração sintética por gravação do grupo se a orientação da turma exigir a participação em voz ou imagem. A submissão no portal acadêmico não foi realizada. Nenhum desses atos pessoais foi marcado como executado automaticamente.
