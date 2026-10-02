import re

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TOLERANCE = 0.01


class ValidationError(ValueError):
    pass


def _fail(errors: list[str], source: str) -> None:
    if errors:
        raise ValidationError(f"{source}: " + "; ".join(errors[:10]))


def validate_finances(finances: list[dict]) -> None:
    errors = []
    years = [f["year"] for f in finances]
    if len(years) != len(set(years)):
        errors.append("exercícios duplicados")
    for item in finances:
        year, revenues, expenses = item["year"], item["revenues"], item["expenses"]
        if revenues["gross"] <= 0:
            errors.append(f"{year}: receita total não positiva")
        if abs(sum(o["value"] for o in revenues["origins"]) - revenues["gross"]) > TOLERANCE:
            errors.append(f"{year}: origens não somam a receita total")
        if not expenses["committed"] + TOLERANCE >= expenses["liquidated"] >= expenses["paid"] - TOLERANCE:
            errors.append(f"{year}: esperado empenhado ≥ liquidado ≥ pago")
        if any(f["paid"] < 0 for f in expenses["functions"]):
            errors.append(f"{year}: função com valor pago negativo")
    _fail(errors, "SICONFI")


def validate_execution(execution: list[dict]) -> None:
    errors = []
    years = [e["year"] for e in execution]
    if len(years) != len(set(years)):
        errors.append("exercícios duplicados")
    for item in execution:
        year, months = item["year"], [m["month"] for m in item["months"]]
        if months != sorted(set(months)) or not set(months) <= set(range(1, 13)):
            errors.append(f"{year}: meses fora de ordem ou inválidos")
        if not item["committed"] + TOLERANCE >= item["liquidated"] >= item["paid"] - TOLERANCE:
            errors.append(f"{year}: esperado empenhado ≥ liquidado ≥ pago")
        if abs(sum(f["paid"] for f in item["functions"]) - item["paid"]) > TOLERANCE * len(item["functions"]):
            errors.append(f"{year}: funções não somam o total pago")
        if item["sources"] is not None and abs(sum(s["paid"] for s in item["sources"]) - item["paid"]) > TOLERANCE * len(item["sources"]):
            errors.append(f"{year}: fontes não somam o total pago")
    _fail(errors, "SICONFI MSC")


def validate_amendments(amendments: list[dict]) -> None:
    errors = []
    ids = [a["id"] for a in amendments]
    if len(ids) != len(set(ids)):
        errors.append("emendas duplicadas")
    for item in amendments:
        values = item["values"]
        if values["transferred"] > values["committed"] + TOLERANCE:
            errors.append(f"{item['id']}: transferido maior que o empenhado")
        if any(not ISO_DATE.match(event["date"]) for event in item["timeline"]):
            errors.append(f"{item['id']}: data fora do padrão ISO 8601")
    _fail(errors, "Transferegov")


def validate_transfers(transfers: list[dict]) -> None:
    ids = [t["id"] for t in transfers]
    _fail(["transferências duplicadas"] if len(ids) != len(set(ids)) else [], "Portal da Transparência")
