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
