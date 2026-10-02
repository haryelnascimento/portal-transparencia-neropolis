import unittest

from etl.normalizers.transfer import money, normalize_transfer


class NormalizerTest(unittest.TestCase):
    def test_money_accepts_brazilian_format(self):
        self.assertEqual(money("R$ 1.234,56"), 1234.56)

    def test_normalizes_transfer(self):
        result = normalize_transfer({"id": 42, "valorTransferido": "1.000,00", "ano": 2026})
        self.assertEqual(result["id"], "federal-transferencia-42")
        self.assertEqual(result["transferred"], 1000.0)
        self.assertEqual(result["municipality"]["ibgeCode"], "5214507")

    def test_identifier_is_required(self):
        with self.assertRaises(ValueError):
            normalize_transfer({})


if __name__ == "__main__":
    unittest.main()

