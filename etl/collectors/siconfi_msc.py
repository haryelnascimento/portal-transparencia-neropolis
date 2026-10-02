from datetime import datetime, timezone

from etl.config import FIRST_YEAR, IBGE_CODE, SICONFI_URL
from etl.http import get_json

# Matriz de Saldos Contábeis: classe 6 (controles da execução do orçamento), saldo acumulado no fim de cada mês.
PARAMS = {"id_ente": IBGE_CODE, "co_tipo_matriz": "MSCC", "classe_conta": 6, "id_tv": "ending_balance"}


def _items(year: int, month: int) -> list[dict]:
    items, offset = [], 0
    while True:
        page = get_json(f"{SICONFI_URL}/msc_orcamentaria", {**PARAMS, "an_referencia": year, "me_referencia": month, "offset": offset})
        items += page.get("items", [])
        if not page.get("hasMore"):
            return items
        offset += len(page["items"])


def collect() -> dict:
    """Coleta a MSC mês a mês. Um mês só aparece depois que a Prefeitura envia a matriz; meses ausentes ficam de fora."""
    years = {}
    for year in range(FIRST_YEAR, datetime.now(timezone.utc).year + 1):
        months = {str(month): items for month in range(1, 13) if (items := _items(year, month))}
        if months:
            years[str(year)] = months
    if not years:
        raise ValueError("SICONFI não retornou nenhuma MSC para o município")
    return years
