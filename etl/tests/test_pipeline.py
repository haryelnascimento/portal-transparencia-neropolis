import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from etl import pipeline


class PipelineFailureTest(unittest.TestCase):
    """Uma fonte com erro preserva os dados anteriores sem impedir as demais (plano §31)."""

    def test_failed_source_keeps_previous_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            normalized = root / "data/normalized"
            normalized.mkdir(parents=True)
            (normalized / "amendments.json").write_text(json.dumps([{"id": "anterior"}]))
            ok = pipeline.Source("ok", "finances", lambda: [], lambda raw: [{"year": 2025}], lambda records: None)
            broken = pipeline.Source("quebrada", "amendments", mock.Mock(side_effect=TimeoutError("fora do ar")), list, lambda records: None)
            with mock.patch.multiple(pipeline, ROOT=root, NORMALIZED=normalized, SOURCES=[ok, broken]):
                records, status = pipeline._run_source(broken, {"lastSuccessAt": "2026-01-01T00:00:00Z"})
                self.assertEqual(records, [{"id": "anterior"}])
                self.assertEqual(status["status"], "FAILED")
                self.assertEqual(status["lastSuccessAt"], "2026-01-01T00:00:00Z")
                _, status = pipeline._run_source(ok, {})
                self.assertEqual(status["status"], "SUCCESS")

    def test_missing_token_is_skipped(self):
        source = pipeline.Source("t", "transfers", mock.Mock(), list, lambda r: None, "TOKEN_INEXISTENTE_XYZ")
        _, status = pipeline._run_source(source, {})
        self.assertEqual(status["status"], "SKIPPED")
        source.collect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
