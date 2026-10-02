import json
import unittest
from pathlib import Path

from etl.normalizers import normalize_amendment, normalize_finances
from etl.normalizers.transfer import money, normalize_transfer
from etl.validators import ValidationError, validate_amendments, validate_finances

FIXTURES = Path(__file__).parent / "fixtures"


def fixture(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class MoneyTest(unittest.TestCase):
    def test_brazilian_format(self):
        self.assertEqual(money("R$ 1.234,56"), 1234.56)

    def test_thousands_without_cents(self):
        self.assertEqual(money("1.000"), 1000.0)
        self.assertEqual(money("R$ 2.500.000"), 2500000.0)

    def test_decimal_point(self):
        self.assertEqual(money("12.5"), 12.5)


class TransferTest(unittest.TestCase):
    def test_normalizes_transfer(self):
        result = normalize_transfer({"id": 42, "valorTransferido": "1.000,00", "ano": 2026})
        self.assertEqual(result["id"], "federal-transferencia-42")
        self.assertEqual(result["transferred"], 1000.0)
        self.assertEqual(result["municipality"]["ibgeCode"], "5214507")

    def test_identifier_is_required(self):
        with self.assertRaises(ValueError):
            normalize_transfer({})


class SiconfiTest(unittest.TestCase):
    """Snapshot de respostas reais da DCA: detecta mudanças no ementário ou no contrato da API."""

    def setUp(self):
        self.finances = {f["year"]: f for f in normalize_finances(fixture("siconfi_dca.json"))}

    def test_revenue_totals_and_origins(self):
        revenues = self.finances[2025]["revenues"]
        self.assertEqual(revenues["gross"], 255744626.53)
        origins = {o["key"]: o["value"] for o in revenues["origins"]}
        self.assertEqual(origins["union"], 90348230.52)
        self.assertEqual(origins["state"], 76281847.82)
        self.assertAlmostEqual(sum(origins.values()), revenues["gross"], places=2)

    def test_highlights_cover_both_classification_schemes(self):
        for year in (2021, 2025):
            keys = {h["key"] for h in self.finances[year]["revenues"]["highlights"]}
            self.assertTrue({"fpm", "icms", "iss", "iptu", "fundeb"} <= keys, year)
        fpm = next(h for h in self.finances[2025]["revenues"]["highlights"] if h["key"] == "fpm")
        self.assertEqual(fpm["value"], 48684022.77)

    def test_expenses_by_function(self):
        expenses = self.finances[2025]["expenses"]
        self.assertEqual(expenses["paid"], 205566859.01)
        health = next(f for f in expenses["functions"] if f["code"] == "10")
        self.assertEqual((health["name"], health["paid"]), ("Saúde", 90291220.38))
        self.assertNotIn(".", "".join(f["code"] for f in expenses["functions"]))

    def test_validation_passes_and_rejects_inconsistency(self):
        validate_finances(list(self.finances.values()))
        broken = json.loads(json.dumps(self.finances[2025]))
        broken["revenues"]["origins"][0]["value"] += 1000
        with self.assertRaises(ValidationError):
            validate_finances([broken])

    def test_rejects_other_municipality(self):
        raw = fixture("siconfi_dca.json")
        raw["2025"]["revenues"][0]["cod_ibge"] = 5208707
        with self.assertRaises(ValueError):
            normalize_finances(raw)


class TransferegovTest(unittest.TestCase):
    def setUp(self):
        self.amendments = {a["id"]: a for a in map(normalize_amendment, fixture("transferegov_planos.json"))}

    def test_amendment_execution_chain(self):
        lake = self.amendments["transferegov-especial-64812"]
        self.assertEqual(lake["parliamentarian"], "Wilder Morais")
        self.assertEqual(lake["purpose"], "Revitalização do lago municipal de Nerópolis")
        self.assertEqual(lake["values"]["transferred"], 3500000.0)
        self.assertEqual([e["date"] for e in lake["timeline"]], sorted(e["date"] for e in lake["timeline"]))

    def test_report_in_progress_has_no_executed_value(self):
        lake = self.amendments["transferegov-especial-64812"]
        self.assertEqual(lake["managementReport"]["status"], "Em elaboração")
        self.assertIsNone(lake["values"]["reportedExecuted"])

    def test_sums_multiple_commitments(self):
        cameras = self.amendments["transferegov-especial-67648"]
        self.assertEqual(cameras["values"]["committed"], 300000.0)
        self.assertEqual(cameras["values"]["transferred"], 300000.0)

    def test_validation(self):
        validate_amendments(list(self.amendments.values()))
        broken = json.loads(json.dumps(self.amendments["transferegov-especial-64812"]))
        broken["values"]["transferred"] = 9e9
        with self.assertRaises(ValidationError):
            validate_amendments([broken])

    def test_rejects_other_beneficiary(self):
        plan = fixture("transferegov_planos.json")[0]
        plan["cnpj_beneficiario_plano_acao"] = "00000000000000"
        with self.assertRaises(ValueError):
            normalize_amendment(plan)


if __name__ == "__main__":
    unittest.main()
