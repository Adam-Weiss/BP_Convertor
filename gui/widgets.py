from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def labeled_entry(parent: ttk.Frame, label: str, textvariable: tk.StringVar, row: int, column: int = 0, width: int = 50) -> ttk.Entry:
    ttk.Label(parent, text=label).grid(row=row, column=column, sticky="w", padx=4, pady=2)
    entry = ttk.Entry(parent, textvariable=textvariable, width=width)
    entry.grid(row=row, column=column + 1, sticky="ew", padx=4, pady=2)
    return entry


def set_widget_state(widgets: list[tk.Widget], state: str) -> None:
    for widget in widgets:
        widget.configure(state=state)


def append_text(text_widget: tk.Text, message: str) -> None:
    text_widget.configure(state="normal")
    text_widget.insert("end", message + "\n")
    text_widget.see("end")
    text_widget.configure(state="disabled")


def clear_text(text_widget: tk.Text) -> None:
    text_widget.configure(state="normal")
    text_widget.delete("1.0", "end")
    text_widget.configure(state="disabled")
