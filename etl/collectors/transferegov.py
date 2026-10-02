from etl.config import CNPJ, TRANSFEREGOV_URL
from etl.http import get_json


def _get(table: str, **filters) -> list[dict]:
    return get_json(f"{TRANSFEREGOV_URL}/{table}", {key: f"eq.{value}" for key, value in filters.items()})


def _in(table: str, column: str, values: list) -> list[dict]:
    if not values:
        return []
    return get_json(f"{TRANSFEREGOV_URL}/{table}", {column: f"in.({','.join(map(str, values))})"})


def collect() -> list[dict]:
    """Coleta as transferências especiais (emendas Pix) destinadas ao CNPJ da prefeitura, com toda a cadeia de execução."""
    plans = _get("plano_acao_especial", cnpj_beneficiario_plano_acao=CNPJ)
    programs = {p["id_programa"]: p for p in _in("programa_especial", "id_programa", sorted({p["id_programa"] for p in plans}))}
    for plan in plans:
        plan_id = plan["id_plano_acao"]
        plan["programa"] = programs.get(plan["id_programa"])
        plan["executores"] = _get("executor_especial", id_plano_acao=plan_id)
        plan["empenhos"] = _get("empenho_especial", id_plano_acao=plan_id)
        plan["relatorios_gestao"] = _get("relatorio_gestao_novo_especial", id_plano_acao=plan_id)
        plan["planos_trabalho"] = _get("plano_trabalho_especial", id_plano_acao=plan_id)
        plan["metas"] = _in("meta_especial", "id_executor", [e["id_executor"] for e in plan["executores"]])
        documents = _in("documento_habil_especial", "id_empenho", [e["id_empenho"] for e in plan["empenhos"]])
        orders = _in("ordem_pagamento_ordem_bancaria_especial", "id_dh", [d["id_dh"] for d in documents])
        for document in documents:
            document["ordens_pagamento"] = [o for o in orders if o["id_dh"] == document["id_dh"]]
        plan["documentos_habeis"] = documents
    return plans
