from __future__ import annotations

import argparse
from datetime import datetime

from bp_converter import ConversionOptions, convert_file
from bp_converter.reporting import stats_to_lines


def _parse_dt(value: str):
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Invalid datetime: {value}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Blood-pressure conversion engine CLI")
    ap.add_argument("input_file")
    ap.add_argument("--format", dest="output_format", default="smartbp_csv", choices=["smartbp_csv", "normalized_xlsx"])
    ap.add_argument("--pulse-policy", default="empty", choices=["empty", "fixed", "user"])
    ap.add_argument("--pulse-value", type=int, default=None)
    ap.add_argument("--source", type=int, default=0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--columns", default=None, help="Comma-separated XLSX export columns")
    ap.add_argument("--start", default=None)
    ap.add_argument("--end", default=None)
    ap.add_argument("--include-stats", action="store_true")
    ap.add_argument("--stats-scope", default="selected", choices=["selected", "all"])
    args = ap.parse_args()

    selected_columns = [c.strip() for c in args.columns.split(",")] if args.columns else None
    options = ConversionOptions(
        source=args.source,
        missing_pulse_policy=args.pulse_policy,
        fixed_pulse_value=args.pulse_value,
        output_format=args.output_format,
        selected_columns=selected_columns,
        filter_start=_parse_dt(args.start) if args.start else None,
        filter_end=_parse_dt(args.end) if args.end else None,
        include_stats=args.include_stats,
        stats_scope=args.stats_scope,
    )

    result = convert_file(args.input_file, options, output_path=args.out)
    print(f"Output: {result.output_file}")
    if options.include_stats:
        for line in stats_to_lines(result.stats):
            print(line)


if __name__ == "__main__":
    main()
