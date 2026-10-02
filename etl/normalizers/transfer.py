from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import re

from etl.config import MUNICIPALITY


def money(value: object) -> float:
    """Converte números e valores no formato brasileiro para decimal."""
    if value is None or value == "":
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = re.sub(r"[^\d,.-]", "", str(value))
    if "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return float(Decimal(cleaned))
    except InvalidOperation as error:
        raise ValueError(f"Valor monetário inválido: {value}") from error


def normalize_transfer(raw: dict) -> dict:
    identifier = str(raw.get("id") or raw.get("codigo") or raw.get("numero") or "").strip()
    if not identifier:
        raise ValueError("Transferência sem identificador")
    amount = money(raw.get("valorTransferido") or raw.get("valor") or 0)
    return {
        "id": f"federal-transferencia-{identifier}",
        "title": raw.get("programa") or raw.get("tipoTransferencia") or "Transferência federal",
        "agency": raw.get("orgaoSuperior") or raw.get("orgao") or "Governo Federal",
        "type": raw.get("tipoTransferencia") or "Transferência",
        "status": raw.get("situacao") or "Recebido",
        "year": int(raw.get("ano") or datetime.now(timezone.utc).year),
        "purpose": raw.get("acao") or raw.get("descricao") or "Finalidade não informada pela fonte",
        "transferred": amount,
        "paid": money(raw.get("valorPago") or amount),
        "sourceUrl": raw.get("link") or "https://portaldatransparencia.gov.br/transferencias",
        "municipality": MUNICIPALITY,
        "source": {"level": "FEDERAL", "system": "TRANSPARENCIA_GOV_BR"},
    }

