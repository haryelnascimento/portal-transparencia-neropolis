import unicodedata

# Nomes nacionais usados quando o código não aparece em nenhuma DCA do município.
# Funções: Portaria MOG nº 42/1999. Elementos: Portaria Interministerial STN/SOF nº 163/2001, Anexo II (só os já vistos na MSC).
FUNCTION_NAMES = {
    "01": "Legislativa", "02": "Judiciária", "03": "Essencial à Justiça", "04": "Administração", "05": "Defesa Nacional",
    "06": "Segurança Pública", "07": "Relações Exteriores", "08": "Assistência Social", "09": "Previdência Social", "10": "Saúde",
    "11": "Trabalho", "12": "Educação", "13": "Cultura", "14": "Direitos da Cidadania", "15": "Urbanismo", "16": "Habitação",
    "17": "Saneamento", "18": "Gestão Ambiental", "19": "Ciência e Tecnologia", "20": "Agricultura", "21": "Organização Agrária",
    "22": "Indústria", "23": "Comércio e Serviços", "24": "Comunicações", "25": "Energia", "26": "Transporte",
    "27": "Desporto e Lazer", "28": "Encargos Especiais", "99": "Reserva de Contingência",
}
ELEMENT_NAMES = {"43": "Subvenções Sociais", "93": "Indenizações e Restituições", "99": "A Classificar"}


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


def enrich_execution(execution: list[dict], finances: list[dict]) -> None:
    """Completa a MSC com os nomes da DCA e confere os totais anuais com ela.

    A MSC traz só códigos; função e elemento de despesa recebem o nome usado na DCA (do mesmo código, em
    qualquer exercício). A conferência compara dezembro da MSC com a DCA do mesmo ano: a diferença é publicada
    em `reconciliation` e exibida no portal, nunca ajustada.
    """
    functions = {**FUNCTION_NAMES, **{f["code"]: f["name"] for year in finances for f in year["expenses"]["functions"]}}
    elements = {n["code"]: n["name"] for year in finances for n in year["expenses"]["natures"]["tree"]}
    by_year = {f["year"]: f["expenses"] for f in finances}

    def element_name(code: str) -> str:
        # O nome do elemento não depende da modalidade: 3.3.50.43 tem o mesmo nome de 3.3.90.43.
        parts = code.split(".")
        return elements.get(code) or elements.get(".".join([*parts[:2], "90", *parts[3:]])) or ELEMENT_NAMES.get(parts[3]) or f"Elemento de despesa {code}"

    for item in execution:
        for function in item["functions"]:
            function["name"] = functions.get(function["code"], f"Função {function['code']}")
            for element in function["elements"]:
                element["name"] = element_name(element["code"])
        for source in item["sources"] or []:
            for function in source["functions"]:
                function["name"] = functions.get(function["code"], f"Função {function['code']}")
            for element in source["elements"]:
                element["name"] = element_name(element["code"])
        dca = by_year.get(item["year"])
        if dca and item["lastMonth"] == 12:
            diffs = {stage: round(item[stage] - dca[stage], 2) for stage in ("committed", "liquidated", "paid")}
            item["reconciliation"] = {"reference": "DCA", "matches": all(abs(v) <= 0.01 for v in diffs.values()), "differences": diffs}
        else:
            item["reconciliation"] = None
