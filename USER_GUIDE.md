# BP_Convertor User Guide

## 1) Input formats

BP_Convertor accepts:

- **XLSX** files from health apps and manual logs
- **CSV/TSV** exports with either combined or split date/time fields

Detection strategy:

- scans candidate header rows
- infers semantic roles (`sys`, `dia`, `pulse`, `date`/`datetime`, etc.)
- scores candidates and picks the strongest BP-like table

## 2) SmartBP CSV format

The SmartBP writer emits columns:

1. Date
2. Systolic(mmHg)
3. Diastolic(mmHg)
4. Pulse(BPM)
5. Weight(kgs)
6. Pulse pressure(mmHg)
7. MAP( mmHg)
8. Notes
9. Tags
10. csRecordId
11. source

Compatibility details:

- all fields are quoted
- CRLF line endings are used
- notes are normalized to SmartBP-friendly line formatting

## 3) Normalized XLSX export

Normalized XLSX contains:

- `Measurements` sheet with selectable columns
- optional `Stats` sheet when `include_stats=True`

Useful columns include raw provenance (`original_date`, `original_time`) and diagnostics (`warnings`, `corrections_applied`).

## 4) Filtering options

`filter_start` and `filter_end` restrict exported rows by measurement timestamp.

Accepted GUI datetime patterns:

- `YYYY-MM-DD`
- `YYYY-MM-DD HH:MM`
- `YYYY-MM-DD HH:MM:SS`

If both start and end are supplied, start must be <= end.

## 5) Pulse handling policies

- `empty`: leave missing pulse blank
- `fixed`: fill missing pulse with configured value
- `user`: same behavior as fixed, for compatibility with prior UX semantics

When filling is applied, the row records correction metadata and warning text.

## 6) Statistics

Generated statistics include:

- row counts (`read`, `selected`, `exported`, `skipped`)
- correction counters (swapped Sys/Dia, PP mismatch, pulse fill)
- timestamp bounds
- average/min/max vitals where available

`stats_scope` controls whether stats are computed on selected rows only or all validated rows.

## 7) Troubleshooting

### Error: no BP table detected

Likely causes:

- file has no real BP data table
- headers are heavily non-standard
- delimiter differs from CSV/TSV assumptions

Try:

- exporting again as CSV
- removing extra report sections
- ensuring table includes date/datetime + systolic + diastolic columns

### Error: table detected but no valid measurements parsed

Likely causes:

- date/time format unsupported in source data
- non-numeric systolic/diastolic cells

Try:

- standardize date formats in source file
- clean non-numeric BP values

### GUI validation errors

- **Source must be an integer**: enter numeric source id
- **Pulse value required/invalid**: set positive integer when policy is fixed/user
- **Invalid datetime**: use one of supported GUI formats
- **Start after end**: adjust range ordering

## 8) Common errors and solutions

- **Unsupported columns requested**: ensure XLSX columns are from allowed set.
- **Unsupported input extension**: use `.xlsx`, `.csv`, or `.tsv`.
- **Conversion failed unexpectedly**: run CLI with same options to see full traceback context.
