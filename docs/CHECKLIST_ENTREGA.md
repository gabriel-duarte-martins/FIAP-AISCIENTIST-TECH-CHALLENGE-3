# Checklist de execução — Tech Challenge Fase 3

Referência: enunciado [IAST] — Tech Challenge — Fase 3, páginas 2–8.
Este checklist descreve requisitos acadêmicos; publicação e gravação serão registradas pelo estado real, sem evidências fabricadas.

| Etapa | O que fazer | Evidência esperada | Estado inicial |
|---|---|---|---|
| 1. Problema (p. 2) | Definir classificação de alfabetização por aluno e população elegível | Objetivo, alvo e instante de predição | Base inicial criada |
| 2. Gold (p. 2–4) | Reutilizar Fase 2 e rastrear integração individual | SQL, linhagem, qualidade, cobertura | Revisar |
| 3. Enriquecimento (p. 3–4) | Integrar contexto socioeconômico/populacional disponível antes de 2024 | Fonte, ano, dicionário, cobertura | Fazer |
| 4. EDA (p. 3–4) | Distribuições, faltantes, padrões territoriais, correlações e hipóteses | Tabelas e gráficos; decisões fundamentadas | Fazer |
| 5. Preparação (p. 3 e 5) | Imputação, transformações e encoding dentro da pipeline | Código reutilizável e testes de proteção | Revisar |
| 6. Leakage (p. 3 e 5) | Excluir proficiência contemporânea e separar municípios | Lista permitida, contrato temporal, partições | Revisar |
| 7. Modelos (p. 5) | Baseline, regressão logística e alternativa não linear | Comparação por validação, seleção de parâmetros | Fazer |
| 8. Avaliação (p. 3 e 5) | Métricas, incerteza por município, erro por UF/rede, calibração | JSON, CSV, gráficos, limites da generalização | Fazer |
| 9. Interpretação (p. 5) | Importância de variáveis e associação sem inferência causal | Importância por permutação e discussão | Fazer |
| 10. Negócio (p. 5) | Responder às cinco perguntas estratégicas | Relatório, grupos de municípios e ranking de risco | Fazer |
| 11. Organização (p. 6) | data, notebooks, src/preprocessing/modeling/evaluation/visualization, reports, images | Estrutura e execução pelo VS Code | Fazer |
| 12. Reprodutibilidade (p. 6–7) | Configuração, ambiente, cache, versões, semente, hashes | Executar análise sem novas consultas | Fazer |
| 13. README (p. 7) | Todos os onze tópicos pedidos | README final orientado ao alvo individual | Reescrever |
| 14. Documentação (p. 7) | Relatório técnico, dicionário e decisões | Artefatos rastreáveis e resultados reais | Fazer |
| 15. Git (p. 6–7) | Histórico real, branches e PR | Commits reais; PR apenas se publicado | Verificar repositório |
| 16. Vídeo (p. 7–8) | Preparar fala executiva de até 5 minutos | Roteiro e material visual; gravação pelo grupo | Preparar roteiro |

## Critérios de aceite

- Resultados produzidos pela execução real e ligados à versão da base.
- Nenhuma variável calculada com o resultado de 2024 entra como atributo do alvo de 2024.
- Municípios disjuntos entre treino, validação e teste; limiar escolhido sem usar teste.
- Métricas ponderadas pela contagem de alunos; contagem não é peso amostral do Inep.
- Desempenho comparado a um baseline aprendido no treino.
- Associações e limitações contextual, temporal e territorial explicitadas.
- Scripts executáveis por Run Python File, sem argumentos obrigatórios.
- Itens dependentes da conta GitHub ou da gravação do grupo não marcados como concluídos antes da execução.
