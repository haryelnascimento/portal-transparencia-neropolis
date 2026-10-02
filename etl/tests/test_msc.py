import copy
import json
import unittest
from pathlib import Path

from etl.correlators import enrich_execution
from etl.normalizers import normalize_execution, normalize_finances
from etl.normalizers.msc import element_code
from etl.validators import ValidationError, validate_execution

FIXTURES = Path(__file__).parent / "fixtures"


def fixture(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class ExecutionTest(unittest.TestCase):
    """Fixture: MSC real de 2025 recortada (Saúde, Assistência Social e receitas da fonte 706) e um trecho de 2021."""

    def setUp(self):
        self.finances = normalize_finances(fixture("siconfi_dca.json"))
        self.execution = normalize_execution(fixture("siconfi_msc.json"))
        enrich_execution(self.execution, self.finances)
        self.year = {e["year"]: e for e in self.execution}[2025]
        self.health = next(f for f in self.year["functions"] if f["code"] == "10")

    def test_function_matches_dca_to_the_cent(self):
        dca = next(f for f in {f["year"]: f for f in self.finances}[2025]["expenses"]["functions"] if f["code"] == "10")
        self.assertEqual(self.health["name"], "Saúde")
        for stage in ("committed", "liquidated", "paid"):
            self.assertAlmostEqual(self.health[stage], dca[stage], places=2)

    def test_elements_sum_to_function_and_skip_intra(self):
        self.assertAlmostEqual(sum(e["paid"] for e in self.health["elements"]), self.health["paid"], places=2)
        self.assertFalse(any(e["code"].split(".")[2] == "91" for e in self.health["elements"]))
        self.assertEqual(self.health["elements"][0]["name"], "Outros Serviços de Terceiros - Pessoa Jurídica")

    def test_monthly_series_is_cumulative(self):
        self.assertEqual([m["month"] for m in self.health["months"]], [6, 12])
        self.assertLess(self.health["months"][0]["paid"], self.health["months"][1]["paid"])
        self.assertEqual(self.health["months"][-1]["paid"], self.health["paid"])

    def test_funding_source_tracks_where_money_was_paid(self):
        special = next(s for s in self.year["sources"] if s["code"] == "706")
        self.assertEqual(special["name"], "Transferência Especial da União")
        self.assertEqual(special["shortName"], "Transferência especial da União (emendas Pix)")
        self.assertAlmostEqual(special["received"], 2245236.84, places=2)
        self.assertAlmostEqual(special["paid"], 1201100.80, places=2)
        self.assertAlmostEqual(special["paidFromPreviousYears"], 298050.93, places=2)
        self.assertEqual([f["name"] for f in special["functions"]], ["Saúde", "Assistência Social"])
        self.assertAlmostEqual(sum(s["paid"] for s in self.year["sources"]), self.year["paid"], places=2)

    def test_legacy_funding_codes_are_not_published(self):
        self.assertIsNone({e["year"]: e for e in self.execution}[2021]["sources"])

    def test_divergence_from_dca_is_reported(self):
        # O recorte não traz todas as funções, então o total não pode bater com a DCA e a diferença aparece.
        self.assertFalse(self.year["reconciliation"]["matches"])
        complete = copy.deepcopy(self.year)
        dca = {f["year"]: f for f in self.finances}[2025]["expenses"]
        complete.update({stage: dca[stage] for stage in ("committed", "liquidated", "paid")})
        enrich_execution([complete], self.finances)
        self.assertTrue(complete["reconciliation"]["matches"])

    def test_validator_rejects_inconsistent_stages(self):
        broken = copy.deepcopy(self.year)
        broken["liquidated"] = broken["committed"] + 1000
        with self.assertRaises(ValidationError):
            validate_execution([broken])

    def test_inconsistent_year_is_not_published(self):
        # Como em dezembro de 2020: saldo devedor em "liquidado a pagar" deixa o pago acima do liquidado.
        raw = fixture("siconfi_msc.json")
        row = next(i for i in raw["2025"]["12"] if i["conta_contabil"] == "622130400")
        raw["2025"]["12"].append({**row, "conta_contabil": "622130300", "natureza_conta": "D", "valor": 8308427.0})
        self.assertEqual([e["year"] for e in normalize_execution(raw)], [2021])

    def test_element_code_matches_dca_format(self):
        self.assertEqual(element_code("33903036"), "3.3.90.30.00.00")


if __name__ == "__main__":
    unittest.main()
