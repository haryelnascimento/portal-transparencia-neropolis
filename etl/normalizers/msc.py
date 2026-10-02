import json
import re
from collections import defaultdict
from pathlib import Path

from etl.config import IBGE_CODE, SICONFI_URL

# Contas de controle da despesa (PCASP, classe 6). Durante o ano o empenho passa por 6.2.2.1.3.01 (a liquidar),
# .02 (em liquidação), .03 (liquidado a pagar) e .04 (pago); no encerramento, o saldo vai para .05, .06 e .07
# (inscrição em restos a pagar). Empenhado é a soma de todas; liquidado, das contas já liquidadas.
COMMITTED = {"622130100", "622130200", "622130300", "622130400", "622130500", "622130600", "622130700"}
LIQUIDATED = {"622130300", "622130400", "622130700"}
PAID = {"622130400"}
# Receita realizada (6.2.1.2) e deduções da receita (6.2.1.3), as duas por fonte de recursos.
REVENUE = ("6212", "6213")
# Modalidade 91 (intraorçamentária) fica de fora, como no total por função da DCA, para os números baterem.
INTRA = "91"
STN_FONTE = re.compile(r"^[129]\d{3}$")
REFERENCE = json.loads((Path(__file__).resolve().parents[1] / "reference/fontes_stn.json").read_text(encoding="utf-8"))
FONTES, FONTES_SHORT = REFERENCE["codes"], REFERENCE["short"]
STAGES = ("committed", "liquidated", "paid")


def source_url(year: int, month: int) -> str:
    return f"{SICONFI_URL}/msc_orcamentaria?id_ente={IBGE_CODE}&an_referencia={year}&me_referencia={month}&co_tipo_matriz=MSCC&classe_conta=6&id_tv=ending_balance"


def _signed(item: dict) -> float:
    """Contas de controle da despesa e da receita têm saldo credor; saldo devedor reduz o valor."""
    return float(item["valor"]) * (1 if item["natureza_conta"] == "C" else -1)


def element_code(nature: str) -> str:
    """'33903036' (categoria, grupo, modalidade, elemento, subelemento) → '3.3.90.30.00.00', o elemento no formato da DCA."""
    return f"{nature[0]}.{nature[1]}.{nature[2:4]}.{nature[4:6]}.00.00"


class _Stages(defaultdict):
    def __init__(self):
        super().__init__(float)

    def add(self, item: dict) -> None:
        account, value = item["conta_contabil"], _signed(item)
        if account in COMMITTED:
            self["committed"] += value
        if account in LIQUIDATED:
            self["liquidated"] += value
        if account in PAID:
            self["paid"] += value

    def out(self) -> dict:
        return {stage: round(self[stage], 2) for stage in STAGES}


def _ranked(groups: dict[str, _Stages], extra: dict | None = None) -> list[dict]:
    rows = [{"code": code, **(extra or {}).get(code, {}), **stages.out()} for code, stages in groups.items()]
    return sorted(rows, key=lambda r: r["paid"], reverse=True)


def _expenses(items: list[dict]) -> list[dict]:
    return [i for i in items if i["conta_contabil"] in COMMITTED and i.get("natureza_despesa") and i["natureza_despesa"][2:4] != INTRA]


def _paid(groups: dict[str, float]) -> list[dict]:
    return sorted(({"code": code, "paid": round(value, 2)} for code, value in groups.items() if round(value, 2)), key=lambda r: r["paid"], reverse=True)


def _sources(items: list[dict], expenses: list[dict]) -> list[dict] | None:
    """Fonte de recursos: quanto entrou em cada fonte no ano e onde foi pago. Só existe na codificação nacional (a partir de 2022).

    Por fonte, só o valor pago é publicado: a Prefeitura pode trocar a fonte de um gasto entre o empenho e o pagamento
    (ex.: 2025, fonte 2706 com saldo "liquidado a pagar" negativo), então empenhado e liquidado por fonte não fecham.
    """
    codes = {i["fonte_recursos"] for i in items if i.get("fonte_recursos")}
    if not codes or not all(STN_FONTE.match(code) for code in codes):
        return None
    received, paid, previous = defaultdict(float), defaultdict(float), defaultdict(float)
    functions, elements = defaultdict(lambda: defaultdict(float)), defaultdict(lambda: defaultdict(float))
    for item in items:
        if item["conta_contabil"].startswith(REVENUE) and item["fonte_recursos"].startswith("1"):
            received[item["fonte_recursos"][1:]] += _signed(item)
    for item in expenses:
        if item["conta_contabil"] not in PAID:
            continue
        code, value = item["fonte_recursos"][1:], _signed(item)
        paid[code] += value
        functions[code][item["funcao"]] += value
        elements[code][element_code(item["natureza_despesa"])] += value
        if item["fonte_recursos"].startswith("2"):
            previous[code] += value
    rows = [
        {
            "code": code,
            "name": FONTES.get(code),
            "shortName": FONTES_SHORT.get(code),
            "received": round(received[code], 2),
            "paid": round(paid[code], 2),
            "paidFromPreviousYears": round(previous[code], 2),
            "functions": _paid(functions[code]),
            "elements": _paid(elements[code]),
        }
        for code in set(received) | set(paid)
    ]
    return sorted((r for r in rows if r["received"] or r["paid"]), key=lambda r: (r["paid"], r["received"]), reverse=True)


def normalize_year(year: int, months: dict[str, list[dict]]) -> dict:
    wrong = {str(i.get("cod_ibge")) for items in months.values() for i in items} - {IBGE_CODE}
    if wrong:
        raise ValueError(f"MSC contém registros de outro ente: {sorted(wrong)}")
    ordered = sorted((int(month), items) for month, items in months.items())
    last_month, last_items = ordered[-1]
    expenses = _expenses(last_items)

    timeline, function_months = [], defaultdict(list)
    for month, items in ordered:
        total, by_function = _Stages(), defaultdict(_Stages)
        for item in _expenses(items):
            total.add(item)
            by_function[item["funcao"]].add(item)
        timeline.append({"month": month, **total.out()})
        for code, stages in by_function.items():
            function_months[code].append({"month": month, **stages.out()})

    total, functions, elements = _Stages(), defaultdict(_Stages), defaultdict(lambda: defaultdict(_Stages))
    for item in expenses:
        total.add(item)
        functions[item["funcao"]].add(item)
        elements[item["funcao"]][element_code(item["natureza_despesa"])].add(item)
    sources = _sources(last_items, expenses)
    by_source = defaultdict(list)
    for source in sources or []:
        for function in source["functions"]:
            by_source[function["code"]].append({"code": source["code"], "name": source["name"], "shortName": source["shortName"], "paid": function["paid"]})
    extra = {code: {"months": function_months[code], "elements": _ranked(elements[code]), "sources": sorted(by_source[code], key=lambda r: r["paid"], reverse=True)} for code in functions}
    return {
        "year": year,
        "lastMonth": last_month,
        "months": timeline,
        **total.out(),
        "functions": _ranked(functions, extra),
        "sources": sources,
        "sourceUrl": source_url(year, last_month),
        "source": {"level": "MUNICIPAL", "system": "SICONFI_MSC"},
    }


def consistent(record: dict, tolerance: float = 0.01) -> bool:
    """Em todo mês do ano, empenhado ≥ liquidado ≥ pago."""
    return all(m["committed"] + tolerance >= m["liquidated"] >= m["paid"] - tolerance for m in record["months"])


def normalize_execution(raw: dict) -> list[dict]:
    """Anos com matriz inconsistente não são publicados (ex.: 2020, dezembro com "liquidado a pagar" negativo de R$ 8,3 mi).

    A inconsistência está no dado enviado pela Prefeitura; o ano segue disponível pela DCA.
    """
    records = []
    for year, months in sorted(raw.items()):
        record = normalize_year(int(year), months)
        if consistent(record):
            records.append(record)
        else:
            print(f"::warning::siconfi-msc: {year} não publicado: pago maior que o liquidado ou liquidado maior que o empenhado em algum mês")
    return records
