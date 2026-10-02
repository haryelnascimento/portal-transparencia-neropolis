from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IBGE_CODE = "5214507"
CNPJ = "01105626000125"  # Prefeitura Municipal de Nerópolis (cadastro de entes do SICONFI)
MUNICIPALITY = {"name": "Nerópolis", "state": "GO", "ibgeCode": IBGE_CODE, "cnpj": CNPJ}
FIRST_YEAR = 2020

API_URL = "https://api.portaldatransparencia.gov.br/api-de-dados/transferencias"
SICONFI_URL = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"
TRANSFEREGOV_URL = "https://api.transferegov.gestao.gov.br/transferenciasespeciais"
