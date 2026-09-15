-- Executado por build_student_gold.py; PROJECT_ID é substituído pelo script.
-- Origem e destino ficam na região US. O contexto agregado de 2023 já foi carregado.
CREATE TABLE `PROJECT_ID.alfabetizacao_gold_ml.mart_alfabetizacao_aluno`
PARTITION BY RANGE_BUCKET(ano, GENERATE_ARRAY(2023, 2031, 1))
CLUSTER BY id_municipio, rede AS
WITH alunos_deduplicados AS (
  SELECT
    SAFE_CAST(ano AS INT64) AS ano,
    CAST(id_municipio AS STRING) AS id_municipio,
    CAST(rede AS STRING) AS rede_codigo,
    CAST(serie AS STRING) AS serie,
    SAFE_CAST(alfabetizado AS INT64) AS alfabetizado,
    SAFE_CAST(presenca AS INT64) AS presenca
  FROM `basedosdados.br_inep_avaliacao_alfabetizacao.alunos`
  WHERE ano = 2024
), alunos_normalizados AS (
  SELECT
    ano, id_municipio, serie, alfabetizado, presenca,
    CASE rede_codigo
      WHEN '0' THEN 'Total' WHEN '1' THEN 'Federal'
      WHEN '2' THEN 'Estadual' WHEN '3' THEN 'Municipal'
      WHEN '4' THEN 'Privada' WHEN '5' THEN 'Pública'
      ELSE rede_codigo
    END AS rede
  FROM alunos_deduplicados
)
SELECT
  a.ano,
  a.id_municipio,
  SUBSTR(a.id_municipio, 1, 2) AS codigo_uf,
  a.rede,
  a.serie,
  c.taxa_alfabetizacao_municipio_ano_anterior,
  c.media_portugues_municipio_ano_anterior,
  c.presenca_municipio_ano_anterior,
  c.quantidade_alunos_ano_anterior,
  a.alfabetizado AS alvo_alfabetizado
FROM alunos_normalizados AS a
LEFT JOIN `PROJECT_ID.alfabetizacao_gold_ml.contexto_municipal_2023` AS c
  ON c.ano + 1 = a.ano
 AND c.id_municipio = a.id_municipio
 AND c.rede = a.rede
WHERE a.presenca = 1 AND a.alfabetizado IN (0, 1);
