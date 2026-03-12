from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from bp_converter.detectors import detect_table
from bp_converter.engine import convert_file
from bp_converter.options import ConversionOptions


class SanityTests(unittest.TestCase):
    def test_detect_embedded_csv_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "input.csv"
            src.write_text(
                "Report Generated,2025-01-01\n\n"
                "Measurement Date, Measurement Time, Systolic (mmHg), Diastolic (mmHg), Pulse(BPM)\n"
                "2025-01-02,08:00,120,80,70\n"
            )
            table = detect_table(str(src))
            self.assertIn("sys", table.roles)
            self.assertIn("dia", table.roles)

    def test_convert_and_warning_for_swapped_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "input.csv"
            out = Path(tmp) / "out.csv"
            src.write_text(
                "Date,Systolic(mmHg),Diastolic(mmHg),Pulse(BPM)\n"
                "2025-01-02 08:00:00,80,120,70\n"
            )
            result = convert_file(str(src), ConversionOptions(output_format="smartbp_csv"), str(out))
            self.assertTrue(out.exists())
            self.assertTrue(any("swapped" in w for w in result.warnings))

            with out.open(newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))
            self.assertEqual(rows[1][1], "120")
            self.assertEqual(rows[1][2], "80")


if __name__ == "__main__":
    unittest.main()
