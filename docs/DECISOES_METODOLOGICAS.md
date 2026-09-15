# Decisões metodológicas

## Alvo e população

O objetivo principal é `alvo_alfabetizado` para o aluno presente com rótulo válido em 2024. A classe 1 é alfabetizado. Para priorização, o score de risco é `1 - probabilidade_alfabetizado` e o interesse é identificar a classe 0. Não misturar os nomes das duas classes ao interpretar AP, precisão e recall.

O modelo usa contexto do município, rede e UF. Não há atributos prévios próprios da criança. Por isso duas crianças com atributos iguais recebem probabilidades iguais. A base é individual, mas o poder de diferenciação é contextual. Não equivale a diagnóstico pedagógico.

## Cronologia e leakage

- Dados educacionais: ano de referência 2023; alvo: 2024.
- PIB e composição econômica: 2021. População: 2022. PIB per capita usa denominador populacional de 2021.
- As versões históricas são as disponíveis na consulta de 2026. Não recuperamos snapshots das publicações originais. Falta confirmar a data exata de disponibilidade de cada indicador educacional antes da avaliação individual; esta é uma análise retrospectiva.
- Proficiência individual contemporânea e resultados agregados de 2024 não entram nos atributos.
- Metas entram na análise estratégica e no cenário prospectivo, não no classificador individual como substitutas do rótulo.
- Município é chave de partição, não feature. Nenhum município aparece em dois conjuntos.
- O teste da primeira versão já foi visto; os resultados finais são exploratórios. Precisamos de novos dados para avaliação confirmatória, mesmo com a seleção atual restrita a treino/validação.

## Compressão e ponderação

A Gold individual tem 1.852.788 observações. Para o treino local, perfis idênticos de atributos e rótulo são agrupados em 12.989 linhas com multiplicidade `peso`. A soma das multiplicidades é igual à contagem original. Não é amostragem nem o peso amostral `peso_aluno` do Inep.

A mediana, média e escala do pré-processamento usam multiplicidades do treino. A regressão logística usa os mesmos pesos no objetivo. Um teste compara previsões com uma base sintética expandida e confirma equivalência numérica dentro da tolerância. Para boosting, os cortes de histogramas também dependem da distribuição dos perfis, portanto não se afirma identidade com uma execução expandida. Todas as métricas são ponderadas pela contagem real de observações.

## Seleção de modelos e limiar

As famílias são baseline de prevalência, regressão logística e HistGradientBoosting. Três dobras de GroupKFold no treino escolhem hiperparâmetros por Brier score. A validação escolhe a família; depois define um limiar exploratório que maximiza acurácia balanceada do risco. O modelo não é reajustado após essa escolha: permanece treinado só no treino. O teste informa desempenho, sem retroalimentar seleção de features, parâmetros ou limiar.

O limiar 0,38 identifica mais casos de risco e sinaliza cerca de 56,6% das observações. O limiar 0,5 sinaliza 18,6%. Isso mostra um compromisso entre sensibilidade e carga de atendimento. A seleção estatística do limiar não define capacidade ou prioridade de uma política pública.

## Incerteza e diferenças de erro

Os intervalos de confiança usam bootstrap de municípios. Reamostrar alunos individualmente criaria uma precisão artificial porque muitos compartilham atributos e contexto. São avaliados Brier, ROC-AUC, AP de risco, precisão, recall, F1, acurácia balanceada e calibração. Recortes por UF e rede com menos de 30 municípios ou 1.000 observações são marcados como amostra pequena.

As diferenças regionais de recall são grandes. Uma política não deve assumir a mesma qualidade de identificação em todas as UFs. A variável UF captura contexto e cobertura; não estima uma causa do desempenho. A coluna de contagem de alunos teve importância por permutação negativa neste teste; isso sugere investigação futura, mas não foi removida depois de olhar o teste para melhorar artificialmente a métrica.

## Clusters e metas futuras

Os clusters são uma análise descritiva separada, sem rótulo de 2024 entre os atributos. K entre 2 e 6 é comparado por silhouette; a execução escolheu 3 grupos. Eles descrevem estrutura econômica e porte populacional, não capacidades de alunos.

Para metas de 2025, são feitos cenários de estabilidade da taxa de 2024 e crescimento de 5 ou 10 pontos percentuais. Eles não são previsões validadas de 2025. O classificador municipal inicial continua no projeto como experimento anterior, mas não substitui o modelo individual e não deve ser usado para afirmar generalização temporal.
