import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'config.json').read_text(encoding='utf-8'))
DATA = ROOT / 'data'
REPORTS = ROOT / 'reports' / 'final'
IMAGES = ROOT / 'images'
TARGET = 'alvo_alfabetizado'
WEIGHT = 'peso'
NUMERIC = [
    'taxa_alfabetizacao_municipio_ano_anterior',
    'media_portugues_municipio_ano_anterior',
    'presenca_municipio_ano_anterior',
    'quantidade_alunos_ano_anterior',
    'populacao_2022', 'pib_per_capita_2021',
    'participacao_agro_2021', 'participacao_industria_2021',
    'participacao_servicos_2021', 'participacao_publica_2021',
]
CATEGORICAL = ['codigo_uf', 'rede']
FEATURES = NUMERIC + CATEGORICAL
LOG_COLUMNS = ['quantidade_alunos_ano_anterior', 'populacao_2022', 'pib_per_capita_2021']
LABELS = {
    'taxa_alfabetizacao_municipio_ano_anterior':'Alfabetização municipal (2023)',
    'media_portugues_municipio_ano_anterior':'Média de português (2023)',
    'presenca_municipio_ano_anterior':'Presença na avaliação (2023)',
    'quantidade_alunos_ano_anterior':'Alunos avaliados (2023)',
    'populacao_2022':'População (2022)', 'pib_per_capita_2021':'PIB per capita (2021)',
    'participacao_agro_2021':'Participação agropecuária (2021)',
    'participacao_industria_2021':'Participação industrial (2021)',
    'participacao_servicos_2021':'Participação de serviços (2021)',
    'participacao_publica_2021':'Participação da administração pública (2021)',
    'codigo_uf':'Unidade da Federação', 'rede':'Rede de ensino',
}
