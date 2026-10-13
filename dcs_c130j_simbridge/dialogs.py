"""Waypoint editing dialog."""

import tkinter as tk
from tkinter import messagebox, ttk

from .geo import parse_coordinate

class WaypointDialog(tk.Toplevel):
    """Modal dialog for creating or editing a route waypoint."""

    def __init__(self, parent, title="Waypoint", initial=None):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.resizable(False, False)
        self.grab_set()

        self.result = None
        self.initial = initial or {}

        self.name_var = tk.StringVar(value=self.initial.get("name", ""))
        self.type_var = tk.StringVar(value=self.initial.get("type_label", "WPT"))
        self.lat_var = tk.StringVar(value=str(self.initial.get("lat", "")))
        self.lon_var = tk.StringVar(value=str(self.initial.get("lon", "")))
        self.rwy_var = tk.StringVar(value=str(self.initial.get("rwy", "")))
        self.elev_var = tk.StringVar(value=str(self.initial.get("elev", "-999")))

        self._build_ui()
        self.geometry(f"+{parent.winfo_rootx() + 60}+{parent.winfo_rooty() + 60}")
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)

    def _build_ui(self):
        frame = ttk.Frame(self, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)

        row = 0
        ttk.Label(frame, text="Identifier:").grid(row=row, column=0, sticky="w", pady=4)
        name_entry = ttk.Entry(frame, textvariable=self.name_var, width=24)
        name_entry.grid(row=row, column=1, pady=4, padx=5)
        name_entry.focus_set()

        row += 1
        ttk.Label(frame, text="Type:").grid(row=row, column=0, sticky="w", pady=4)
        type_cb = ttk.Combobox(
            frame,
            textvariable=self.type_var,
            values=["WPT", "DEP", "ARR", "FAF", "DISC"],
            state="readonly",
            width=22
        )
        type_cb.grid(row=row, column=1, pady=4, padx=5)
        type_cb.bind("<<ComboboxSelected>>", self._on_type_change)

        row += 1
        ttk.Label(frame, text="Latitude:").grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.lat_var, width=24).grid(row=row, column=1, pady=4, padx=5)

        row += 1
        ttk.Label(frame, text="Longitude:").grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.lon_var, width=24).grid(row=row, column=1, pady=4, padx=5)

        row += 1
        ttk.Label(frame, text="Runway:").grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.rwy_var, width=24).grid(row=row, column=1, pady=4, padx=5)

        row += 1
        ttk.Label(frame, text="Elevation (ft):").grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.elev_var, width=24).grid(row=row, column=1, pady=4, padx=5)

        row += 1
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=(15, 0), sticky="e")
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_frame, text="Save", command=self._on_save).pack(side=tk.RIGHT, padx=4)

    def _on_type_change(self, _event=None):
        if self.type_var.get() == "DISC":
            if not self.name_var.get():
                self.name_var.set(">> DISCONTINUITY <<")
            self.lat_var.set("0.0")
            self.lon_var.set("0.0")
            self.rwy_var.set("")
            self.elev_var.set("-999")

    def _on_save(self):
        name = self.name_var.get().strip().upper()
        type_lbl = self.type_var.get()

        if not name:
            messagebox.showwarning("Validation Error", "Waypoint identifier cannot be empty.", parent=self)
            return

        if type_lbl == "DISC":
            lat, lon = 0.0, 0.0
            wp_type = 7
        else:
            try:
                lat = parse_coordinate(self.lat_var.get())
                lon = parse_coordinate(self.lon_var.get())
            except Exception as e:
                messagebox.showerror("Coordinate Error", f"Invalid coordinates:\n{e}", parent=self)
                return

            if type_lbl == "DEP":
                wp_type = 2
            elif type_lbl == "ARR":
                wp_type = 1
            else:
                wp_type = 0

        self.result = {
            "name": name[:10],
            "type_label": type_lbl,
            "wp_type": wp_type,
            "lat": lat,
            "lon": lon,
            "rwy": self.rwy_var.get().strip().upper()[:7],
            "elev": self.elev_var.get().strip() or "-999"
        }
        self.destroy()


# -----------------------------------------------------------------------------
# MAIN APPLICATION
# -----------------------------------------------------------------------------
