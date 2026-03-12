from __future__ import annotations

import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from bp_converter.engine import DEFAULT_XLSX_COLUMNS, convert_file
from bp_converter.options import ConversionOptions
from bp_converter.writer import ALLOWED_COLUMNS
from gui.view_models import GuiState, ResultSummary
from gui.widgets import append_text, clear_text, labeled_entry, set_widget_state

DATETIME_HELP = "YYYY-MM-DD HH:MM:SS"


class ConverterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("BP Converter")
        self.state = GuiState(selected_columns=list(DEFAULT_XLSX_COLUMNS))

        self.status_var = tk.StringVar(value="Ready")
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.output_format_var = tk.StringVar(value="smartbp_csv")
        self.file_type_var = tk.StringVar(value="")
        self.source_var = tk.StringVar(value="0")
        self.pulse_policy_var = tk.StringVar(value="empty")
        self.pulse_value_var = tk.StringVar(value="")
        self.start_var = tk.StringVar(value="")
        self.end_var = tk.StringVar(value="")
        self.include_stats_var = tk.BooleanVar(value=True)
        self.stats_scope_var = tk.StringVar(value="selected")
        self.column_vars = {col: tk.BooleanVar(value=(col in DEFAULT_XLSX_COLUMNS)) for col in ALLOWED_COLUMNS}

        self.summary_labels: dict[str, ttk.Label] = {}
        self.convert_button: Optional[ttk.Button] = None
        self.column_checks: list[ttk.Checkbutton] = []
        self.columns_frame: Optional[ttk.LabelFrame] = None
        self.pulse_entry: Optional[ttk.Entry] = None
        self.details_text: Optional[tk.Text] = None

        self._build_ui()

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        self._build_file_section(main)
        self._build_output_section(main)
        self._build_pulse_section(main)
        self._build_filter_section(main)
        self._build_columns_section(main)
        self._build_controls_section(main)
        self._build_summary_section(main)
        self._build_details_section(main)

    def _build_file_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="File selection", padding=8)
        frame.pack(fill="x", pady=4)
        frame.columnconfigure(1, weight=1)

        labeled_entry(frame, "Input file", self.input_var, row=0)
        ttk.Button(frame, text="Browse", command=self._choose_input_file).grid(row=0, column=2, padx=4)
        ttk.Label(frame, textvariable=self.file_type_var).grid(row=1, column=1, sticky="w", padx=4, pady=2)

    def _build_output_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Output options", padding=8)
        frame.pack(fill="x", pady=4)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Format").grid(row=0, column=0, sticky="w", padx=4)
        format_combo = ttk.Combobox(
            frame,
            textvariable=self.output_format_var,
            values=["smartbp_csv", "normalized_xlsx"],
            state="readonly",
            width=20,
        )
        format_combo.grid(row=0, column=1, sticky="w", padx=4)
        format_combo.bind("<<ComboboxSelected>>", lambda _: self._sync_output_mode())

        labeled_entry(frame, "Output path", self.output_var, row=1)
        ttk.Button(frame, text="Browse", command=self._choose_output_file).grid(row=1, column=2, padx=4)
        labeled_entry(frame, "Source", self.source_var, row=2, width=12)

    def _build_pulse_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Missing pulse options", padding=8)
        frame.pack(fill="x", pady=4)

        for idx, policy in enumerate(["empty", "fixed", "user"]):
            rb = ttk.Radiobutton(frame, text=policy, value=policy, variable=self.pulse_policy_var, command=self._sync_pulse_state)
            rb.grid(row=0, column=idx, sticky="w", padx=4, pady=2)

        self.pulse_entry = labeled_entry(frame, "Pulse value", self.pulse_value_var, row=1, width=12)
        self._sync_pulse_state()

    def _build_filter_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Date range filtering", padding=8)
        frame.pack(fill="x", pady=4)
        frame.columnconfigure(1, weight=1)

        labeled_entry(frame, f"Start ({DATETIME_HELP})", self.start_var, row=0)
        labeled_entry(frame, f"End ({DATETIME_HELP})", self.end_var, row=1)

    def _build_columns_section(self, parent: ttk.Frame) -> None:
        self.columns_frame = ttk.LabelFrame(parent, text="XLSX column selection", padding=8)
        self.columns_frame.pack(fill="x", pady=4)
        for idx, col in enumerate(ALLOWED_COLUMNS):
            cb = ttk.Checkbutton(self.columns_frame, text=col, variable=self.column_vars[col])
            cb.grid(row=idx // 4, column=idx % 4, sticky="w", padx=4, pady=2)
            self.column_checks.append(cb)
        self._sync_output_mode()

    def _build_controls_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Run/convert controls", padding=8)
        frame.pack(fill="x", pady=4)

        ttk.Checkbutton(frame, text="Include stats", variable=self.include_stats_var).grid(row=0, column=0, sticky="w", padx=4)
        ttk.Label(frame, text="Stats scope").grid(row=0, column=1, sticky="w", padx=4)
        ttk.Combobox(frame, textvariable=self.stats_scope_var, values=["selected", "all"], state="readonly", width=12).grid(
            row=0, column=2, sticky="w", padx=4
        )

        self.convert_button = ttk.Button(frame, text="Convert", command=self._run_conversion)
        self.convert_button.grid(row=0, column=3, padx=8)
        ttk.Label(frame, textvariable=self.status_var).grid(row=0, column=4, sticky="w", padx=4)

    def _build_summary_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Results summary", padding=8)
        frame.pack(fill="x", pady=4)

        keys = [
            "output_file", "rows_read", "rows_selected", "rows_exported", "rows_skipped", "first_timestamp", "last_timestamp",
            "swapped_sys_dia_fixed", "pp_mismatch_count", "pulse_missing", "pulse_filled", "avg_sys", "avg_dia", "avg_pulse",
        ]
        for row, key in enumerate(keys):
            ttk.Label(frame, text=f"{key}:").grid(row=row // 2, column=(row % 2) * 2, sticky="w", padx=4, pady=1)
            lbl = ttk.Label(frame, text="")
            lbl.grid(row=row // 2, column=(row % 2) * 2 + 1, sticky="w", padx=4, pady=1)
            self.summary_labels[key] = lbl

    def _build_details_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Warnings/details", padding=8)
        frame.pack(fill="both", expand=True, pady=4)

        self.details_text = tk.Text(frame, height=10, wrap="word", state="disabled")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=scrollbar.set)
        self.details_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _choose_input_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Select input file",
            filetypes=[("BP files", "*.xlsx *.csv *.tsv"), ("All files", "*.*")],
        )
        if path:
            self.input_var.set(path)
            self.file_type_var.set(f"Detected type: {Path(path).suffix.lower()}")

    def _choose_output_file(self) -> None:
        ext = ".csv" if self.output_format_var.get() == "smartbp_csv" else ".xlsx"
        path = filedialog.asksaveasfilename(
            title="Select output file",
            defaultextension=ext,
            filetypes=[("CSV", "*.csv"), ("XLSX", "*.xlsx"), ("All files", "*.*")],
        )
        if path:
            self.output_var.set(path)

    def _sync_output_mode(self) -> None:
        is_xlsx = self.output_format_var.get() == "normalized_xlsx"
        state = "normal" if is_xlsx else "disabled"
        set_widget_state(self.column_checks, state)

    def _sync_pulse_state(self) -> None:
        if not self.pulse_entry:
            return
        state = "normal" if self.pulse_policy_var.get() in {"fixed", "user"} else "disabled"
        self.pulse_entry.configure(state=state)

    def _parse_datetime(self, value: str) -> Optional[datetime]:
        value = value.strip()
        if not value:
            return None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        raise ValueError(f"Invalid datetime '{value}', expected {DATETIME_HELP}")

    def _read_state(self) -> GuiState:
        source = int(self.source_var.get().strip() or "0")
        pulse_policy = self.pulse_policy_var.get()
        pulse_value = self.pulse_value_var.get().strip()
        selected_columns = [name for name, var in self.column_vars.items() if var.get()]

        if self.output_format_var.get() == "normalized_xlsx" and not selected_columns:
            raise ValueError("Select at least one XLSX column")

        return GuiState(
            input_path=self.input_var.get().strip(),
            output_path=self.output_var.get().strip(),
            output_format=self.output_format_var.get(),
            source=source,
            missing_pulse_policy=pulse_policy,
            pulse_value=int(pulse_value) if pulse_value else None,
            filter_start=self._parse_datetime(self.start_var.get()),
            filter_end=self._parse_datetime(self.end_var.get()),
            include_stats=self.include_stats_var.get(),
            stats_scope=self.stats_scope_var.get(),
            selected_columns=selected_columns,
        )

    def _to_options(self, state: GuiState) -> ConversionOptions:
        return ConversionOptions(
            source=state.source,
            missing_pulse_policy=state.missing_pulse_policy,
            fixed_pulse_value=state.pulse_value,
            output_format=state.output_format,
            selected_columns=state.selected_columns if state.output_format == "normalized_xlsx" else None,
            filter_start=state.filter_start,
            filter_end=state.filter_end,
            include_stats=state.include_stats,
            stats_scope=state.stats_scope,
        )

    def _set_busy(self, busy: bool) -> None:
        if self.convert_button:
            self.convert_button.configure(state="disabled" if busy else "normal")
        self.status_var.set("Converting..." if busy else "Ready")
        self.root.update_idletasks()

    def _render_summary(self, summary: ResultSummary) -> None:
        values = {
            "output_file": summary.output_file,
            "rows_read": summary.rows_read,
            "rows_selected": summary.rows_selected,
            "rows_exported": summary.rows_exported,
            "rows_skipped": summary.rows_skipped,
            "first_timestamp": summary.first_timestamp or "",
            "last_timestamp": summary.last_timestamp or "",
            "swapped_sys_dia_fixed": summary.swapped_sys_dia_fixed,
            "pp_mismatch_count": summary.pp_mismatch_count,
            "pulse_missing": summary.pulse_missing,
            "pulse_filled": summary.pulse_filled,
            "avg_sys": "" if summary.avg_sys is None else f"{summary.avg_sys:.2f}",
            "avg_dia": "" if summary.avg_dia is None else f"{summary.avg_dia:.2f}",
            "avg_pulse": "" if summary.avg_pulse is None else f"{summary.avg_pulse:.2f}",
        }
        for key, value in values.items():
            self.summary_labels[key].configure(text=str(value))

    def _run_conversion(self) -> None:
        if not self.details_text:
            return
        clear_text(self.details_text)
        try:
            state = self._read_state()
            if not state.input_path:
                raise ValueError("Input file is required")
            self._set_busy(True)
            options = self._to_options(state)
            result = convert_file(state.input_path, options, output_path=state.output_path or None)

            stats = result.stats
            summary = ResultSummary(
                output_file=result.output_file,
                rows_read=stats.rows_read,
                rows_selected=stats.rows_selected,
                rows_exported=stats.rows_exported,
                rows_skipped=stats.rows_skipped,
                first_timestamp=stats.first_timestamp,
                last_timestamp=stats.last_timestamp,
                swapped_sys_dia_fixed=stats.swapped_sys_dia_fixed,
                pp_mismatch_count=stats.pp_mismatch_count,
                pulse_missing=stats.pulse_missing,
                pulse_filled=stats.pulse_filled,
                avg_sys=stats.avg_sys,
                avg_dia=stats.avg_dia,
                avg_pulse=stats.avg_pulse,
            )
            self._render_summary(summary)

            if result.warnings:
                append_text(self.details_text, "Warnings:")
                for warning in result.warnings:
                    append_text(self.details_text, f"- {warning}")
            else:
                append_text(self.details_text, "No warnings reported.")
            self.status_var.set("Done")
        except Exception as exc:
            self.status_var.set("Error")
            append_text(self.details_text, f"Error: {exc}")
            messagebox.showerror("Conversion failed", str(exc))
        finally:
            self._set_busy(False)


def main() -> None:
    root = tk.Tk()
    app = ConverterApp(root)
    root.minsize(920, 760)
    root.mainloop()


if __name__ == "__main__":
    main()
