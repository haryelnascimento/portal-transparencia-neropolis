import json
import os
from datetime import datetime, timezone
from pathlib import Path

from etl.collectors.transparencia import collect
from etl.config import MUNICIPALITY, ROOT
from etl.normalizers import normalize_transfer


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run() -> None:
    started = datetime.now(timezone.utc)
    public = ROOT / "frontend/public/data"
    source_status = "SUCCESS"
    try:
        raw = collect()
        _write(ROOT / "data/raw/transparencia/latest.json", raw)
        transfers = [normalize_transfer(record) for record in raw]
    except Exception as error:
        source_status = "STALE"
        existing = public / "transfers/index.json"
        if not existing.exists() or os.environ.get("CI"):
            raise
        transfers = json.loads(existing.read_text(encoding="utf-8"))
        print(f"Coleta indisponível; mantendo dados anteriores: {error}")

    received = sum(item["transferred"] for item in transfers)
    paid = sum(item["paid"] for item in transfers)
    summary = {
        "municipality": MUNICIPALITY,
        "updatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "totals": {"received": received, "committed": paid, "liquidated": paid, "paid": paid},
        "counts": {"transfers": len(transfers), "amendments": sum("emenda" in item["type"].lower() for item in transfers), "agreements": 0, "works": 0, "suppliers": 0},
    }
    _write(ROOT / "data/normalized/transfers.json", transfers)
    _write(public / "transfers/index.json", transfers)
    _write(public / "summary.json", summary)
    _write(public / "metadata/last-update.json", {"startedAt": started.isoformat(), "finishedAt": datetime.now(timezone.utc).isoformat(), "status": "SUCCESS", "sources": {"transparencia": source_status}})

