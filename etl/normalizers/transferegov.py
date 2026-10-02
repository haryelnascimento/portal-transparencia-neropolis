from etl.config import MUNICIPALITY, TRANSFEREGOV_URL

PAID_ORDER = "OB Enviada à instituição bancária para pagamento"
REPORT_STATUS = {"EM_ELABORACAO": "Em elaboração", "DISPONIBILIZADO": "Disponibilizado", "ENVIADO": "Enviado"}
# Só relatórios entregues têm valor executado declarado; em elaboração o valor 0 é provisório.
DELIVERED_REPORTS = {"DISPONIBILIZADO", "ENVIADO"}


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
        "timeline": sorted(events, key=lambda e: e["date"]),
        "sourceUrl": f"{TRANSFEREGOV_URL}/plano_acao_especial?id_plano_acao=eq.{plan_id}",
        "municipality": MUNICIPALITY,
        "source": {"level": "FEDERAL", "system": "TRANSFEREGOV_ESPECIAIS"},
    }
