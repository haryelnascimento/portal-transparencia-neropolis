from datetime import datetime, timezone

from etl.config import FIRST_YEAR, IBGE_CODE, SICONFI_URL
from etl.http import get_json

ANNEXES = {"revenues": "DCA-Anexo I-C", "expenses": "DCA-Anexo I-E"}


def _items(annex: str, year: int) -> list[dict]:
    items, offset = [], 0
    while True:
        page = get_json(f"{SICONFI_URL}/dca", {"an_exercicio": year, "no_anexo": annex, "id_ente": IBGE_CODE, "offset": offset})
        items += page.get("items", [])
        if not page.get("hasMore"):
            return items
        offset += len(page["items"])


def collect() -> dict:
    """Coleta a Declaração de Contas Anuais (receitas e despesas por função) de cada exercício publicado."""
    years = {}
    for year in range(FIRST_YEAR, datetime.now(timezone.utc).year + 1):
        data = {key: _items(annex, year) for key, annex in ANNEXES.items()}
        if data["revenues"] and data["expenses"]:
            years[str(year)] = data
    if not years:
        raise ValueError("SICONFI não retornou nenhuma DCA para o município")
    return years
