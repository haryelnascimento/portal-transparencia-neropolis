import re

from etl.config import IBGE_CODE, SICONFI_URL

GROSS = "Receitas Brutas Realizadas"
TOTAL = "ReceitasExcetoIntraOrcamentarias"

# Origem da receita a partir dos códigos de natureza (os níveis superiores não mudaram em 2022).
ORIGINS = [
    ("union", "União", ["1.7.1.0.00.0.0", "2.4.1.0.00.0.0"]),
    ("state", "Estado de Goiás", ["1.7.2.0.00.0.0", "2.4.2.0.00.0.0"]),
    ("fundeb", "FUNDEB", ["1.7.5.0.00.0.0"]),
    ("own", "Arrecadação própria", ["1.1.0.0.00.0.0", "1.2.0.0.00.0.0", "1.3.0.0.00.0.0", "1.4.0.0.00.0.0", "1.5.0.0.00.0.0", "1.6.0.0.00.0.0", "1.9.0.0.00.0.0"]),
]

# Principais receitas. Cada item lista alternativas (ementário a partir de 2022 e o anterior); vale a primeira presente.
HIGHLIGHTS = [
    ("fpm", "FPM (federal)", "union", [["1.7.1.1.51.0.0"], ["1.7.1.8.01.2.0", "1.7.1.8.01.3.0", "1.7.1.8.01.4.0"]]),
    ("sus-union", "SUS — União", "union", [["1.7.1.3.00.0.0"], ["1.7.1.8.03.0.0"]]),
    ("fnde", "FNDE (educação)", "union", [["1.7.1.4.00.0.0"], ["1.7.1.8.05.0.0"]]),
    ("icms", "ICMS (cota-parte)", "state", [["1.7.2.1.50.0.0"], ["1.7.2.8.01.1.0"]]),
    ("ipva", "IPVA (cota-parte)", "state", [["1.7.2.1.51.0.0"], ["1.7.2.8.01.2.0"]]),
    ("sus-state", "SUS — Estado", "state", [["1.7.2.3.00.0.0"], ["1.7.2.8.03.0.0"]]),
    ("fundeb", "FUNDEB", "fundeb", [["1.7.5.0.00.0.0"]]),
    ("iss", "ISS", "own", [["1.1.1.4.51.0.0"], ["1.1.1.8.02.3.0"]]),
    ("iptu", "IPTU", "own", [["1.1.1.2.50.0.0"], ["1.1.1.8.01.1.0"]]),
    ("irrf", "IR retido na fonte", "own", [["1.1.1.3.03.0.0"]]),
    ("itbi", "ITBI", "own", [["1.1.1.2.53.0.0"], ["1.1.1.8.01.4.0"]]),
]

EXPENSE_COLUMNS = {"Despesas Empenhadas": "committed", "Despesas Liquidadas": "liquidated", "Despesas Pagas": "paid"}
FUNCTION = re.compile(r"^(\d{2}) - (.+)$")
SUBFUNCTION = re.compile(r"^(\d{2})\.(\d{3}) - (.+)$")
OTHER_SUBFUNCTIONS = re.compile(r"^FU(\d{2}) - (.+)$")
CODE_PREFIX = re.compile(r"^[\d.]+\s*-?\s*")


def _check_entity(items: list[dict]) -> None:
    wrong = {str(i.get("cod_ibge")) for i in items} - {IBGE_CODE}
    if wrong:
        raise ValueError(f"DCA contém registros de outro ente: {sorted(wrong)}")


def _source_url(year: int, annex: str) -> str:
    return f"{SICONFI_URL}/dca?an_exercicio={year}&no_anexo={annex.replace(' ', '%20')}&id_ente={IBGE_CODE}"


def clean_name(raw: str) -> str:
    """Remove o código do início e corrige o caractere '¿' que a API devolve no lugar de travessões e aspas."""
    name = CODE_PREFIX.sub("", raw.strip()).replace(" ¿ ", " – ").replace("¿", "–")
    return re.sub(r"\s+", " ", name).strip()


def parent_code(code: str, known: set[str]) -> str | None:
    """Ancestral mais próximo existente, zerando o último segmento não nulo do código de natureza."""
    parts = code.split(".")
    while True:
        index = max((i for i, part in enumerate(parts) if int(part)), default=-1)
        if index <= 0:
            return None
        parts[index] = "0" * len(parts[index])
        candidate = ".".join(parts)
        if candidate in known:
            return candidate


def build_tree(nodes: dict[str, dict]) -> list[dict]:
    known = set(nodes)
    for code, node in nodes.items():
        node["parent"] = parent_code(code, known)
    return sorted(nodes.values(), key=lambda n: n["code"])


def normalize_revenues(items: list[dict], year: int) -> dict:
    _check_entity(items)
    rows = [i for i in items if i["coluna"] == GROSS and i["cod_conta"].startswith("RO")]
    gross = {i["cod_conta"].removeprefix("RO"): float(i["valor"]) for i in rows}
    totals = {i["coluna"]: float(i["valor"]) for i in items if i["cod_conta"] == TOTAL}
    if GROSS not in totals:
        raise ValueError(f"DCA {year} sem total de receitas")
    total = totals[GROSS]
    deductions = sum(value for column, value in totals.items() if column != GROSS)

    origins = [{"key": key, "label": label, "codes": [c for c in codes if c in gross], "value": round(sum(gross.get(code, 0.0) for code in codes), 2)} for key, label, codes in ORIGINS]
    origins.append({"key": "other", "label": "Outras receitas", "codes": [], "value": round(total - sum(o["value"] for o in origins), 2)})

    highlights = []
    for key, label, origin, alternatives in HIGHLIGHTS:
        codes = next((alt for alt in alternatives if any(code in gross for code in alt)), None)
        if codes:
            highlights.append({"key": key, "label": label, "origin": origin, "codes": [c for c in codes if c in gross], "value": round(sum(gross.get(c, 0.0) for c in codes), 2)})
    highlights.sort(key=lambda item: item["value"], reverse=True)

    tree = build_tree({i["cod_conta"].removeprefix("RO"): {"code": i["cod_conta"].removeprefix("RO"), "name": clean_name(i["conta"]), "value": round(float(i["valor"]), 2)} for i in rows})
    return {
        "gross": round(total, 2),
        "deductions": round(deductions, 2),
        "net": round(total - deductions, 2),
        "origins": origins,
        "highlights": highlights,
        "tree": tree,
        "sourceUrl": _source_url(year, "DCA-Anexo I-C"),
    }


def _empty(code: str, name: str) -> dict:
    return {"code": code, "name": name, "committed": 0.0, "liquidated": 0.0, "paid": 0.0}


def normalize_expenses(items: list[dict], year: int) -> dict:
    _check_entity(items)
    totals = {"committed": 0.0, "liquidated": 0.0, "paid": 0.0}
    functions: dict[str, dict] = {}
    subfunctions: dict[tuple[str, str], dict] = {}
    for item in items:
        field = EXPENSE_COLUMNS.get(item["coluna"])
        if not field or item["cod_conta"] != "TotalDespesas":
            continue
        value, account = float(item["valor"]), item["conta"].strip()
        if account == "Despesas Exceto Intraorçamentárias":
            totals[field] = value
        elif match := FUNCTION.match(account):
            code, name = match.groups()
            functions.setdefault(code, {**_empty(code, name.strip()), "subfunctions": []})[field] = value
        elif match := SUBFUNCTION.match(account):
            function, code, name = match.groups()
            subfunctions.setdefault((function, code), _empty(code, name.strip()))[field] = value
        elif match := OTHER_SUBFUNCTIONS.match(account):
            function, name = match.groups()
            subfunctions.setdefault((function, "outras"), _empty("outras", name.strip()))[field] = value
    if not totals["committed"]:
        raise ValueError(f"DCA {year} sem total de despesas")
    for (function, _), sub in subfunctions.items():
        if function in functions:
            functions[function]["subfunctions"].append(sub)
    for function in functions.values():
        function["subfunctions"].sort(key=lambda s: s["paid"], reverse=True)
    return {
        **{key: round(value, 2) for key, value in totals.items()},
        "functions": sorted(functions.values(), key=lambda f: f["paid"], reverse=True),
        "sourceUrl": _source_url(year, "DCA-Anexo I-E"),
    }


def normalize_natures(items: list[dict], year: int) -> dict:
    """Despesa por natureza (Anexo I-D): categoria → grupo (pessoal, custeio, investimento) → modalidade → elemento."""
    _check_entity(items)
    nodes: dict[str, dict] = {}
    for item in items:
        field = EXPENSE_COLUMNS.get(item["coluna"])
        # DO = despesa orçamentária; DI = intraorçamentária (entre órgãos do próprio município, ex.: contribuição ao RPPS).
        # Os totais dos grupos incluem as duas, então ambas entram na árvore para que os filhos somem ao pai.
        if not field or not item["cod_conta"].startswith(("DO", "DI")):
            continue
        code = item["cod_conta"][2:]
        node = nodes.setdefault(code, _empty(code, clean_name(item["conta"])))
        node[field] = round(float(item["valor"]), 2)
        node["intra"] = item["cod_conta"].startswith("DI")
    tree = build_tree(nodes)
    roots = [n for n in tree if n["parent"] is None]
    return {"tree": tree, "paid": round(sum(n["paid"] for n in roots), 2), "sourceUrl": _source_url(year, "DCA-Anexo I-D")}


def normalize_finances(raw: dict) -> list[dict]:
    return [
        {
            "year": int(year),
            "revenues": normalize_revenues(data["revenues"], int(year)),
            "expenses": {**normalize_expenses(data["expenses"], int(year)), "natures": normalize_natures(data.get("natures", []), int(year))},
            "source": {"level": "MUNICIPAL", "system": "SICONFI_DCA"},
        }
        for year, data in sorted(raw.items())
    ]
