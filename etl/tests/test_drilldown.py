import json
import unittest
from pathlib import Path

from etl.correlators import link_amendments_to_functions
from etl.normalizers import normalize_amendment, normalize_finances
from etl.normalizers.siconfi import clean_name, parent_code
from etl.normalizers.transferegov import parse_budget

FIXTURES = Path(__file__).parent / "fixtures"


def fixture(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class TreeTest(unittest.TestCase):
    def setUp(self):
        self.finance = {f["year"]: f for f in normalize_finances(fixture("siconfi_dca.json"))}[2025]

    def test_parent_skips_missing_levels(self):
        known = {"1.7.0.0.00.0.0", "1.7.1.0.00.0.0", "1.7.1.1.51.0.0"}
        self.assertEqual(parent_code("1.7.1.1.51.1.0", known), "1.7.1.1.51.0.0")
        self.assertEqual(parent_code("1.7.1.1.51.0.0", known), "1.7.1.0.00.0.0")
        self.assertIsNone(parent_code("1.0.0.0.00.0.0", known))

    def test_revenue_children_sum_to_parent(self):
        tree = self.finance["revenues"]["tree"]
        union = next(n for n in tree if n["code"] == "1.7.1.0.00.0.0")
        children = [n for n in tree if n["parent"] == union["code"]]
        self.assertAlmostEqual(sum(c["value"] for c in children), union["value"], places=2)

    def test_names_are_cleaned(self):
        self.assertEqual(clean_name("1.7.1.3.00.0.0 -Transferências do SUS ¿ Repasses"), "Transferências do SUS – Repasses")

    def test_subfunctions_sum_to_function(self):
        health = next(f for f in self.finance["expenses"]["functions"] if f["name"] == "Saúde")
        self.assertAlmostEqual(sum(s["paid"] for s in health["subfunctions"]), health["paid"], places=2)
        self.assertIn("Atenção Básica", [s["name"] for s in health["subfunctions"]])

    def test_natures_tree(self):
        tree = self.finance["expenses"]["natures"]["tree"]
        roots = {n["code"] for n in tree if n["parent"] is None}
        self.assertEqual(roots, {"3.0.00.00.00.00", "4.0.00.00.00.00"})
        services = next(n for n in tree if n["code"] == "3.3.90.39.00.00")
        self.assertEqual(services["name"], "Outros Serviços de Terceiros - Pessoa Jurídica")
        self.assertEqual(services["parent"], "3.3.90.00.00.00")

    def test_natures_include_intra_budget_so_children_sum_to_parent(self):
        natures = self.finance["expenses"]["natures"]
        tree = natures["tree"]
        staff = next(n for n in tree if n["code"] == "3.1.00.00.00.00")
        children = [n for n in tree if n["parent"] == staff["code"]]
        self.assertAlmostEqual(sum(c["paid"] for c in children), staff["paid"], places=2)
        self.assertTrue(any(c["intra"] for c in children))
        self.assertGreater(natures["paid"], self.finance["expenses"]["paid"])


class WorkPlanTest(unittest.TestCase):
    def test_parse_budget_blocks(self):
        text = "Investimento:\nFunção.......: 000014 - Direitos da Cidadania\nElemento....: 449052 - Equipamento\n\nCusteio:\nFunção.......: 000014 - Direitos da Cidadania\nElemento....: 339039 - Serviços PJ"
        blocks = parse_budget(text)
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[1]["element"], {"code": "339039", "name": "Serviços PJ"})

    def test_links_amendment_to_function_by_name(self):
        finances = normalize_finances(fixture("siconfi_dca.json"))
        amendments = [normalize_amendment(p) for p in fixture("transferegov_planos.json")]
        link_amendments_to_functions(amendments, finances)
        links = {a["id"]: a["links"]["function"] for a in amendments}
        self.assertEqual(links["transferegov-especial-64812"]["name"], "Desporto e Lazer")
        # O plano declara "000051 - Urbanismo"; o vínculo usa o nome e chega ao código correto (15).
        self.assertEqual(links["transferegov-especial-70089"]["code"], "15")

    def test_amendment_detail_fields(self):
        lake = next(normalize_amendment(p) for p in fixture("transferegov_planos.json") if p["id_plano_acao"] == 64812)
        self.assertEqual(lake["workPlan"]["months"], 36)
        self.assertEqual(lake["goals"][0]["description"], "Revitalização do lago municipal de Nerópolis")
        self.assertEqual(lake["payments"][0]["order"], "2024OB007382")


if __name__ == "__main__":
    unittest.main()
