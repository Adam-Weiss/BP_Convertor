# BP_Convertor

BP_Convertor converts blood-pressure exports (XLSX/CSV/TSV) into:

- **SmartBP-compatible CSV** (default)
- **Normalized XLSX** for analysis and auditing

The project keeps a stable engine API:

```python
convert_file(input_path: str, options: ConversionOptions, output_path: Optional[str] = None) -> ConversionResult
```

## Supported input formats

- `.xlsx` spreadsheets (auto-detects the best BP table)
- `.csv` delimited files
- `.tsv` tab-delimited files

The detector is hardened to handle:

- header text before data tables
- mixed capitalization and spacing in headers
- BP tables embedded in report-like files
- quoted CSV rows with embedded newlines
- split `date` + `time` columns or combined `datetime`

## Supported output formats

- `smartbp_csv`: strict SmartBP-oriented CSV with CRLF line endings and quoted fields
- `normalized_xlsx`: normalized measurements table plus optional stats sheet

## Architecture overview

- `bp_converter/`: conversion engine, normalization, validation, writers, stats
- `cli.py`: command-line interface
- `gui/`: Tkinter GUI
- `xlsx_to_smartbp.py`: compatibility wrapper

## Installation requirements

- Python 3.10+
- `openpyxl` (for XLSX read/write)

Install dependencies:

```bash
pip install openpyxl
```

## Quick start

### CLI conversion

```bash
python cli.py input.xlsx --format smartbp_csv
```

### GUI

```bash
python -m gui.main_window
```

### Compatibility wrapper

```bash
python xlsx_to_smartbp.py input.xlsx --out output.csv
```

## CLI usage examples

SmartBP CSV output:

```bash
python cli.py export.csv --format smartbp_csv --out smartbp_ready.csv
```

Normalized XLSX with selected columns:

```bash
python cli.py export.tsv --format normalized_xlsx --columns datetime,sys,dia,pulse,notes
```

Date filtering + fixed pulse policy:

```bash
python cli.py export.csv --start "2024-01-01" --end "2024-12-31 23:59" --pulse-policy fixed --pulse-value 70
```

## GUI usage instructions

1. Select an input file (`.xlsx`, `.csv`, `.tsv`).
2. Choose output format and optional explicit output path.
3. Configure pulse policy and date filters.
4. If using normalized XLSX, choose exported columns.
5. Click **Convert**.
6. Review output path, summary metrics, and warnings panel.

## Additional documentation

See [USER_GUIDE.md](USER_GUIDE.md) for detailed behavior, field mapping, filtering, troubleshooting, and common errors.
