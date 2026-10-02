import unicodedata


def _key(name: str) -> str:
    plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return " ".join(plain.lower().replace("-", " ").split())


def link_amendments_to_functions(amendments: list[dict], finances: list[dict]) -> None:
    """Liga cada emenda à função de governo onde a Prefeitura declarou que o recurso entra no orçamento.

    Estratégia "work-plan-function": a função vem do plano de trabalho do Transferegov (declarada pelo
    município) e é comparada pelo nome com as funções da DCA. O código não é usado porque o texto
    livre do plano às vezes traz códigos inconsistentes (ex.: "000051 - Urbanismo", cujo código é 15).
    """
    names = {_key(f["name"]): (f["code"], f["name"]) for year in finances for f in year["expenses"]["functions"]}
    for amendment in amendments:
        budget = (amendment.get("workPlan") or {}).get("budget") or []
        declared = next((b["function"]["name"] for b in budget if b.get("function")), None)
        match = names.get(_key(declared)) if declared else None
        amendment["links"]["function"] = {"code": match[0], "name": match[1], "strategy": "work-plan-function", "confidence": 0.9} if match else None
