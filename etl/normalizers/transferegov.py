import re

from etl.config import MUNICIPALITY, TRANSFEREGOV_URL

PAID_ORDER = "OB Enviada à instituição bancária para pagamento"
REPORT_STATUS = {"EM_ELABORACAO": "Em elaboração", "DISPONIBILIZADO": "Disponibilizado", "ENVIADO": "Enviado"}
# Só relatórios entregues têm valor executado declarado; em elaboração o valor 0 é provisório.
DELIVERED_REPORTS = {"DISPONIBILIZADO", "ENVIADO"}


BUDGET_FIELDS = {
    "Órgão": "organ", "Unidade": "unit", "Função": "function", "Sub-Função": "subfunction",
    "Programa": "program", "Projeto/Atividade": "action", "Elemento": "element", "Fonte de Recurso": "fundingSource",
}
BUDGET_LINE = re.compile(r"^\s*([^.:]+?)\.*:\s*(.+?)\s*$")
WORK_PLAN_STATUS = {"CONCLUIDO_NT_TCU": "Concluído", "APROVADO": "Aprovado", "EM_ELABORACAO": "Em elaboração"}


def parse_budget(text: str | None) -> list[dict]:
    """Converte a classificação orçamentária em texto livre do plano de trabalho em blocos estruturados.

    Exemplo de linha: "Função.......................: 000027 - Desporto e Lazer".
    Um plano pode ter blocos separados para investimento e custeio.
    """
    blocks, current = [], {}
    for line in (text or "").splitlines():
        match = BUDGET_LINE.match(line)
        if not match:
            if line.strip().rstrip(":") in ("Investimento", "Custeio") and current:
                blocks.append(current)
                current = {}
            continue
        key = BUDGET_FIELDS.get(match.group(1).strip())
        if not key:
            continue
        code, _, name = match.group(2).partition(" - ")
        if key in current:
            blocks.append(current)
            current = {}
        current[key] = {"code": code.strip(), "name": re.sub(r"\s+", " ", name).strip() or code.strip()}
    if current:
        blocks.append(current)
    unique = []
    for block in blocks:
        if block not in unique:
            unique.append(block)
    return unique


def _area(raw: str | None) -> str:
    """'15-Urbanismo / 451-Infraestrutura Urbana' → 'Urbanismo'."""
    if not raw:
        return "Não informada"
    first = raw.split(",")[0].split("/")[0]
    return first.split("-", 1)[-1].strip()


def normalize_amendment(plan: dict) -> dict:
    plan_id = plan.get("id_plano_acao")
    if not plan_id:
        raise ValueError("Plano de ação sem identificador")
    if plan.get("cnpj_beneficiario_plano_acao") != MUNICIPALITY["cnpj"]:
        raise ValueError(f"Plano {plan_id} não pertence a Nerópolis")

    planned = float(plan.get("valor_custeio_plano_acao") or 0) + float(plan.get("valor_investimento_plano_acao") or 0)
    commitments = plan.get("empenhos", [])
    committed = sum(float(e["valor_empenho"]) for e in commitments)
    events = [{"date": e["data_emissao_empenho"], "label": f"Empenho {e['numero_empenho']} emitido pela União", "amount": float(e["valor_empenho"])} for e in commitments]

    transferred = 0.0
    for document in plan.get("documentos_habeis", []):
        for order in document.get("ordens_pagamento", []):
            if order.get("descricao_situacao_op") == PAID_ORDER:
                transferred += float(document["valor_dh"])
                events.append({"date": order["data_emissao_ob"], "label": f"Ordem bancária {order['numero_ordem_bancaria']}: recurso enviado à conta do município", "amount": float(document["valor_dh"])})

    reports = sorted(plan.get("relatorios_gestao", []), key=lambda r: r["data_e_hora_relatorio_gestao_novo"])
    report = reports[-1] if reports else None
    for item in reports:
        events.append({"date": item["data_e_hora_relatorio_gestao_novo"][:10], "label": f"Relatório de gestão {item['tipo_relatorio_gestao_novo'].lower()}: {REPORT_STATUS.get(item['situacao_relatorio_gestao_novo'], item['situacao_relatorio_gestao_novo'])}", "amount": None})

    executors = plan.get("executores", [])
    program = plan.get("programa") or {}
    work_plans = plan.get("planos_trabalho", [])
    work_plan = work_plans[0] if work_plans else None
    commitment_list = [{"number": e["numero_empenho"], "date": e["data_emissao_empenho"], "amount": float(e["valor_empenho"]), "category": (e.get("categoria_despesa_empenho") or "").capitalize() or None, "status": e.get("descricao_situacao_empenho")} for e in commitments]
    payments = [
        {"order": o["numero_ordem_bancaria"], "document": d["numero_documento_habil"], "date": o["data_emissao_ob"], "amount": float(d["valor_dh"]), "status": o.get("descricao_situacao_op")}
        for d in plan.get("documentos_habeis", []) for o in d.get("ordens_pagamento", [])
    ]
    goals = [
        {"name": g.get("nome_meta"), "description": (g.get("desc_meta") or "").strip(), "unit": g.get("un_medida_meta"), "quantity": float(g.get("qt_uniade_meta") or 0), "months": g.get("qt_meses_meta"),
         "amount": round(sum(float(g.get(k) or 0) for k in ("vl_custeio_emenda_especial_meta", "vl_investimento_emenda_especial_meta")), 2),
         "ownResources": round(sum(float(g.get(k) or 0) for k in ("vl_custeio_recursos_proprios_meta", "vl_investimento_recursos_proprios_meta")), 2)}
        for g in sorted(plan.get("metas", []), key=lambda g: g.get("sequencial_meta") or 0)
    ]
    return {
        "id": f"transferegov-especial-{plan_id}",
        "code": plan.get("codigo_plano_acao"),
        "year": int(plan["ano_plano_acao"]),
        "type": "Emenda parlamentar — transferência especial",
        "parliamentarian": plan.get("nome_parlamentar_emenda_plano_acao") or "Não informado",
        "amendmentNumber": plan.get("numero_emenda_parlamentar_plano_acao"),
        "area": _area(plan.get("codigo_descricao_areas_politicas_publicas_plano_acao")),
        "purpose": "; ".join(e["objeto_executor"].strip() for e in executors if e.get("objeto_executor")) or "Objeto não informado pela fonte",
        "agency": program.get("nome_orgao_superior_programa") or "Governo Federal",
        "status": plan.get("situacao_plano_acao"),
        "values": {"planned": round(planned, 2), "committed": round(committed, 2), "transferred": round(transferred, 2), "reportedExecuted": float(report["valor_executado_relatorio_gestao_novo"]) if report and report["situacao_relatorio_gestao_novo"] in DELIVERED_REPORTS else None},
        "managementReport": {"type": report["tipo_relatorio_gestao_novo"], "status": REPORT_STATUS.get(report["situacao_relatorio_gestao_novo"], report["situacao_relatorio_gestao_novo"]), "date": report["data_e_hora_relatorio_gestao_novo"][:10]} if report else None,
        "costing": round(float(plan.get("valor_custeio_plano_acao") or 0), 2),
        "investment": round(float(plan.get("valor_investimento_plano_acao") or 0), 2),
        "workPlan": {
            "status": WORK_PLAN_STATUS.get(work_plan["situacao_plano_trabalho"], work_plan["situacao_plano_trabalho"]),
            "start": (work_plan.get("data_inicio_execucao_plano_trabalho") or "")[:10] or None,
            "end": (work_plan.get("data_fim_execucao_plano_trabalho") or "")[:10] or None,
            "months": work_plan.get("prazo_execucao_meses_plano_trabalho"),
            "budget": parse_budget(work_plan.get("classificacao_orcamentaria_pt")),
        } if work_plan else None,
        "goals": goals,
        "commitments": commitment_list,
        "payments": payments,
        "links": {"function": None},
        "timeline": sorted(events, key=lambda e: e["date"]),
        "sourceUrl": f"{TRANSFEREGOV_URL}/plano_acao_especial?id_plano_acao=eq.{plan_id}",
        "municipality": MUNICIPALITY,
        "source": {"level": "FEDERAL", "system": "TRANSFEREGOV_ESPECIAIS"},
    }
