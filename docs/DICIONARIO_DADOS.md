# Dicionário da Gold de modelagem

| Campo | Papel | Referência e transformação |
|---|---|---|
| ano | Metadado | 2024, ano do alvo |
| id_municipio | Chave e grupo de validação | Código IBGE; não entra no modelo |
| codigo_uf | Categórico | One-hot; contexto geográfico |
| rede | Categórico | One-hot; Municipal, Estadual e poucos registros Privada |
| serie | Metadado | Valor 2 em toda a base atual; excluído por ser constante |
| alvo_alfabetizado | Alvo | 1 alfabetizado; 0 não alfabetizado |
| peso | Multiplicidade | Número de observações do perfil; não é `peso_aluno` do Inep |
| taxa_alfabetizacao_municipio_ano_anterior | Numérico | Percentual de alfabetização em 2023 |
| media_portugues_municipio_ano_anterior | Numérico | Média municipal de português em 2023 |
| presenca_municipio_ano_anterior | Numérico | Percentual de presença em 2023 |
| quantidade_alunos_ano_anterior | Numérico | Contagem anterior; transformação log1p |
| populacao_2022 | Numérico | População do município; transformação log1p |
| pib_per_capita_2021 | Numérico | PIB de 2021 em reais / população de 2021; log1p |
| participacao_agro_2021 | Numérico | Valor adicionado agropecuário / total, fração 0–1 |
| participacao_industria_2021 | Numérico | Valor adicionado industrial / total |
| participacao_servicos_2021 | Numérico | Serviços exceto administração pública / total |
| participacao_publica_2021 | Numérico | Administração, defesa, educação e saúde públicas e seguridade social / total |
| nome_municipio, sigla_uf, nome_regiao | Rótulos dos relatórios | Diretório territorial atual; nomes não são features |

Na pipeline, são acrescentados indicadores binários de ausência para os numéricos. Medianas, médias e escalas são ajustadas por multiplicidade somente no treino. Dados econômicos são contextuais: PIB per capita não é renda familiar do aluno.

## Tabelas e consultas

- Origem educacional: `basedosdados.br_inep_avaliacao_alfabetizacao.alunos`.
- Gold anterior: `sharp-gecko-439920-j4.alfabetizacao_gold.mart_alfabetizacao_municipio`.
- Gold individual: `sharp-gecko-439920-j4.alfabetizacao_gold_ml.mart_alfabetizacao_aluno`.
- Gold de perfis enriquecidos: `sharp-gecko-439920-j4.alfabetizacao_gold_ml.mart_modelagem_aluno_perfis_v2`.
- Economia: `basedosdados.br_ibge_pib.municipio`, filtro 2021.
- População: `basedosdados.br_ibge_populacao.municipio`, filtros 2021/2022.
- Metas: `basedosdados.br_inep_avaliacao_alfabetizacao.meta_alfabetizacao_municipio`.

Linhagem, contagem, anos e hashes estão em `reports/final/linhagem_dados.json`.
