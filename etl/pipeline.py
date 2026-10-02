import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from etl.collectors import siconfi, transferegov, transparencia
from etl.config import ROOT
from etl.correlators import link_amendments_to_functions
from etl.exporters import export_public, write_json
from etl.normalizers import normalize_amendment, normalize_finances, normalize_transfer
from etl.validators import validate_amendments, validate_finances, validate_transfers

PUBLIC = ROOT / "frontend/public/data"
NORMALIZED = ROOT / "data/normalized"
METADATA = PUBLIC / "metadata/last-update.json"


@dataclass
class Source:
    name: str
    dataset: str
    collect: Callable[[], object]
    normalize: Callable[[object], list]
    validate: Callable[[list], None]
    required_env: str | None = None


SOURCES = [
    Source("siconfi", "finances", siconfi.collect, normalize_finances, validate_finances),
    Source("transferegov", "amendments", transferegov.collect, lambda raw: [normalize_amendment(p) for p in raw], validate_amendments),
    Source("transparencia", "transfers", transparencia.collect, lambda raw: [normalize_transfer(r) for r in raw], validate_transfers, "TRANSPARENCIA_API_TOKEN"),
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _previous(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def _run_source(source: Source, previous_status: dict) -> tuple[list | None, dict]:
    stored = NORMALIZED / f"{source.dataset}.json"
    started = time.monotonic()
    if source.required_env and not os.environ.get(source.required_env):
        return _previous(stored, None), {"status": "SKIPPED", "message": f"{source.required_env} não configurado", "lastSuccessAt": previous_status.get("lastSuccessAt")}
    try:
        raw = source.collect()
        write_json(ROOT / f"data/raw/{source.name}/latest.json", raw)
        records = source.normalize(raw)
        source.validate(records)
    except Exception as error:  # uma fonte indisponível não derruba as demais (plano §31)
        print(f"::warning::{source.name}: {error}")
        return _previous(stored, None), {"status": "FAILED", "message": str(error)[:300], "lastSuccessAt": previous_status.get("lastSuccessAt")}
    previous = _previous(stored, [])
    known = {item["id"] if "id" in item else item.get("year") for item in previous}
    write_json(stored, records)
    status = {
        "status": "SUCCESS", "records": len(records),
        "newRecords": sum((item["id"] if "id" in item else item.get("year")) not in known for item in records),
        "durationSeconds": round(time.monotonic() - started, 1), "lastSuccessAt": _now(),
    }
    print(f"{source.name}: {status['records']} registros, {status['newRecords']} novos")
    return records, status


def run() -> None:
    started = _now()
    previous = _previous(METADATA, {}).get("sources", {})
    datasets, sources = {}, {}
    for source in SOURCES:
        datasets[source.dataset], sources[source.name] = _run_source(source, previous.get(source.name) if isinstance(previous.get(source.name), dict) else {})
    if not any(s["status"] == "SUCCESS" for s in sources.values()) and not any(datasets.values()):
        raise SystemExit("Nenhuma fonte disponível e não há dados anteriores para publicar")
    if datasets.get("amendments") and datasets.get("finances"):
        link_amendments_to_functions(datasets["amendments"], datasets["finances"])
    statuses = {s["status"] for s in sources.values() if s["status"] != "SKIPPED"}
    metadata = {"startedAt": started, "finishedAt": _now(), "status": "SUCCESS" if statuses == {"SUCCESS"} else "PARTIAL", "sources": sources}
    export_public(PUBLIC, datasets, metadata)
