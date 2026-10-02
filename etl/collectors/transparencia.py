import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from etl.config import API_URL, IBGE_CODE


def collect() -> list[dict]:
    """Coleta apenas transferências de Nerópolis; o token permanece no ambiente."""
    token = os.environ.get("TRANSPARENCIA_API_TOKEN")
    if not token:
        raise RuntimeError("Defina TRANSPARENCIA_API_TOKEN para executar a coleta real")
    query = urlencode({"codigoIbge": IBGE_CODE, "pagina": 1})
    request = Request(f"{API_URL}?{query}", headers={"chave-api-dados": token, "Accept": "application/json"})
    with urlopen(request, timeout=60) as response:  # noqa: S310 - origem pública fixa
        payload = json.load(response)
    if not isinstance(payload, list):
        raise ValueError("Resposta inesperada do Portal da Transparência")
    return payload

