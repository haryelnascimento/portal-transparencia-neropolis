from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IBGE_CODE = "5214507"
MUNICIPALITY = {"name": "Nerópolis", "state": "GO", "ibgeCode": IBGE_CODE}
API_URL = "https://api.portaldatransparencia.gov.br/api-de-dados/transferencias"

