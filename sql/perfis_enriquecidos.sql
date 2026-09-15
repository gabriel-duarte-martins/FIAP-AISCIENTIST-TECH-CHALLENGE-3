-- SELECT materializado por prepare_data.py, no dataset US da Gold de ML.
WITH perfis AS (
  SELECT ano,id_municipio,codigo_uf,rede,serie,
    taxa_alfabetizacao_municipio_ano_anterior,
    media_portugues_municipio_ano_anterior,
    presenca_municipio_ano_anterior,quantidade_alunos_ano_anterior,
    alvo_alfabetizado,COUNT(*) AS peso
  FROM `PROJECT_ID.alfabetizacao_gold_ml.mart_alfabetizacao_aluno`
  GROUP BY ALL
), economia AS (
  SELECT e.id_municipio, SAFE_DIVIDE(e.pib,p.populacao) AS pib_per_capita_2021,
    SAFE_DIVIDE(e.va_agropecuaria,e.va) AS participacao_agro_2021,
    SAFE_DIVIDE(e.va_industria,e.va) AS participacao_industria_2021,
    SAFE_DIVIDE(e.va_servicos,e.va) AS participacao_servicos_2021,
    SAFE_DIVIDE(e.va_adespss,e.va) AS participacao_publica_2021
  FROM `basedosdados.br_ibge_pib.municipio` e
  LEFT JOIN `basedosdados.br_ibge_populacao.municipio` p
    ON e.id_municipio=p.id_municipio AND p.ano=2021
  WHERE e.ano=2021
)
SELECT a.*, p.populacao AS populacao_2022,
  e.* EXCEPT(id_municipio), d.nome AS nome_municipio,
  d.sigla_uf, d.nome_regiao
FROM perfis a
LEFT JOIN economia e USING(id_municipio)
LEFT JOIN `basedosdados.br_ibge_populacao.municipio` p
  ON a.id_municipio=p.id_municipio AND p.ano=2022
LEFT JOIN `basedosdados.br_bd_diretorios_brasil.municipio` d
  ON a.id_municipio=d.id_municipio
