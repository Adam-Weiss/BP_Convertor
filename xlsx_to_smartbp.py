from __future__ import annotations

import argparse
import os
from datetime import datetime
from typing import Optional

from bp_converter.engine import convert_file
from bp_converter.options import ConversionOptions


def convert_xlsx_to_smartbp_csv(xlsx_path: str, out_csv_path: str, sheet: Optional[str], default_source: int = 0):
    # `sheet` is kept for backward compatibility but is currently ignored.
    options = ConversionOptions(source=default_source, output_format="smartbp_csv")
    convert_file(xlsx_path, options, output_path=out_csv_path)


def main():
    ap = argparse.ArgumentParser(
        description="Convert XLSX SmartBP-like table to SmartBP-optimized CSV (auto-detect table)."
    )
    ap.add_argument("xlsx", help="Input .xlsx path")
    ap.add_argument("--out", help="Output CSV path (optional). If omitted, a name will be generated.")
    ap.add_argument("--sheet", default=None, help="Sheet name (default: first sheet)")
    ap.add_argument("--source", type=int, default=0, help="SmartBP source field value (default: 0)")
    args = ap.parse_args()

    input_path = args.xlsx
    out_csv = args.out or f"{os.path.splitext(os.path.basename(input_path))[0]}_smartbp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    print(f"Input : {input_path}")
    print(f"Output: {out_csv}")
    convert_xlsx_to_smartbp_csv(input_path, out_csv, sheet=args.sheet, default_source=args.source)


if __name__ == "__main__":
    main()
