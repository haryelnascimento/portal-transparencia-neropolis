import json
from pathlib import Path

from etl.config import MUNICIPALITY


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def export_public(public: Path, datasets: dict, metadata: dict) -> None:
    """Gera somente os arquivos consumidos pelo frontend, em partes pequenas."""
    finances = datasets.get("finances") or []
    amendments = datasets.get("amendments") or []

    for item in finances:
        write_json(public / f"finances/{item['year']}.json", item)
    write_json(public / "finances/index.json", [
        {"year": f["year"], "revenues": f["revenues"]["gross"], "origins": {o["key"]: o["value"] for o in f["revenues"]["origins"]}, "committed": f["expenses"]["committed"], "paid": f["expenses"]["paid"]}
        for f in finances
    ])
    write_json(public / "amendments/index.json", amendments)
    for item in datasets.get("execution") or []:
        write_json(public / f"execution/{item['year']}.json", item)
    if datasets.get("transfers") is not None:
        write_json(public / "transfers/index.json", datasets["transfers"])

    latest = finances[-1] if finances else None
    write_json(public / "summary.json", {
        "municipality": MUNICIPALITY,
        "updatedAt": metadata["finishedAt"],
        "environment": "HOMOLOGACAO",
        "latestYear": latest["year"] if latest else None,
        "years": [f["year"] for f in finances],
        "finances": {
            "revenues": latest["revenues"]["gross"], "origins": latest["revenues"]["origins"],
            "committed": latest["expenses"]["committed"], "liquidated": latest["expenses"]["liquidated"], "paid": latest["expenses"]["paid"],
        } if latest else None,
        "amendments": {
            "count": len(amendments),
            "planned": round(sum(a["values"]["planned"] for a in amendments), 2),
            "transferred": round(sum(a["values"]["transferred"] for a in amendments), 2),
        },
    })
    write_json(public / "metadata/last-update.json", metadata)
