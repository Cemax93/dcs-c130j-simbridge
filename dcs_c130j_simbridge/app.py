"""Tkinter application controller."""

import json
import os
import re
import sqlite3
import threading
import urllib.error
import urllib.request
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .config import load_theaters
from .data import THEATER_CENTERS
from .dialogs import WaypointDialog
from .flightplan import load_flight_plan, save_flight_plan
from .geo import (
    calculate_distance_nm,
    dec_to_c130_coord,
    format_c130_waypoint,
    generate_approach_fix,
)

try:
    from tkintermapview import TkinterMapView
except ImportError:
    TkinterMapView = None

HAS_MAPVIEW = TkinterMapView is not None

class SimBridgeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DCS C-130J SimBridge")
        self.root.geometry("1240x800")
        self.root.minsize(1050, 680)

        # Load theater configurations
        self.theaters = load_theaters()

        # State variables
        self.simbrief_user = tk.StringVar()
        self.simbrief_prefill_opened = False
        self.custom_route_name = tk.StringVar()
        self.create_faf_var = tk.BooleanVar(value=True)
        self.click_to_add_var = tk.BooleanVar(value=True)

        self.theater_var = tk.StringVar(value="Caucasus" if "Caucasus" in self.theaters else list(self.theaters.keys())[0])
        self.dep_override_var = tk.StringVar()
        self.dep_rwy_var = tk.StringVar()
        self.arr_override_var = tk.StringVar()
        self.arr_rwy_var = tk.StringVar()

        self.map_layer_var = tk.StringVar(value="Google Hybrid")

        # In-memory waypoints list: list of dicts
        self.waypoints = []

        # Default DCS saved games user_data.db path
        self.db_path = tk.StringVar(value=self._detect_dcs_database_path())

        self._setup_ui()
        self._update_theater_airports()
        self.center_map_on_theater()

    def _detect_dcs_database_path(self):
        """Attempts to locate the DCS C-130J user_data.db file."""
        saved_games = os.path.join(os.path.expanduser("~"), "Saved Games")
        candidates = [
            os.path.join(saved_games, "DCS.C130J", "user_data.db"),
            os.path.join(saved_games, "DCS.openbeta", "user_data.db"),
            os.path.join(saved_games, "DCS", "user_data.db")
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                return os.path.normpath(candidate)
        return candidates[0]

    def _setup_ui(self):
        # Main split container: Left (Controls & Table), Right (Interactive Map)
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        left_pane = ttk.Frame(paned, padding="8")
        right_pane = ttk.Frame(paned, padding="8")

        paned.add(left_pane, weight=1)
        paned.add(right_pane, weight=2)

        # =====================================================================
        # LEFT PANE: FLIGHT SETUP, WAYPOINTS TABLE, DATABASE COMMIT, LOGS
        # =====================================================================

        # --- Top Section: SimBrief & Theater ---
        top_frame = ttk.LabelFrame(left_pane, text=" DCS C-130J SimBridge Setup ", padding="8")
        top_frame.pack(fill=tk.X, pady=(0, 8))

        row1 = ttk.Frame(top_frame)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="Theater / Map:").pack(side=tk.LEFT, padx=(0, 4))
        self.theater_cb = ttk.Combobox(
            row1,
            textvariable=self.theater_var,
            values=list(self.theaters.keys()),
            state="readonly",
            width=16
        )
        self.theater_cb.pack(side=tk.LEFT, padx=(0, 8))
        self.theater_cb.bind("<<ComboboxSelected>>", self._on_theater_changed)

        # Overrides row
        row2 = ttk.Frame(top_frame)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Departure:").pack(side=tk.LEFT, padx=(0, 4))
        self.dep_cb = ttk.Combobox(row2, textvariable=self.dep_override_var, state="readonly", width=18)
        self.dep_cb.pack(side=tk.LEFT, padx=(0, 4))
        self.dep_cb.bind("<<ComboboxSelected>>", lambda _: self._on_airport_selected(
            self.dep_override_var, self.dep_rwy_cb
        ))

        ttk.Label(row2, text="Rwy:").pack(side=tk.LEFT, padx=(2, 2))
        self.dep_rwy_cb = ttk.Combobox(row2, textvariable=self.dep_rwy_var, state="readonly", width=5)
        self.dep_rwy_cb.pack(side=tk.LEFT)

        row3 = ttk.Frame(top_frame)
        row3.pack(fill=tk.X, pady=2)
        ttk.Label(row3, text="Arrival:").pack(side=tk.LEFT, padx=(0, 20))
        self.arr_cb = ttk.Combobox(row3, textvariable=self.arr_override_var, state="readonly", width=18)
        self.arr_cb.pack(side=tk.LEFT, padx=(0, 4))
        self.arr_cb.bind("<<ComboboxSelected>>", lambda _: self._on_airport_selected(
            self.arr_override_var, self.arr_rwy_cb
        ))

        ttk.Label(row3, text="Rwy:").pack(side=tk.LEFT, padx=(2, 2))
        self.arr_rwy_cb = ttk.Combobox(row3, textvariable=self.arr_rwy_var, state="readonly", width=5)
        self.arr_rwy_cb.pack(side=tk.LEFT)

        ttk.Button(
            top_frame,
            text="Open SimBrief Prefill",
            command=self.open_simbrief_dispatch
        ).pack(anchor="w", pady=(6, 0))

        ttk.Label(
            top_frame,
            text="Set departure and arrival before opening SimBrief or fetching a plan.",
        ).pack(anchor="w", pady=(2, 0))

        row0 = ttk.Frame(top_frame)
        row0.pack(fill=tk.X, pady=(6, 0))
        ttk.Label(row0, text="SimBrief User / Pilot ID:").pack(side=tk.LEFT, padx=(0, 4))
        ttk.Entry(row0, textvariable=self.simbrief_user, width=16).pack(side=tk.LEFT, padx=(0, 8))
        self.fetch_btn = ttk.Button(row0, text="Fetch Generated Plan", command=self.start_fetch_thread)
        self.fetch_btn.pack(side=tk.LEFT)
        self.fetch_btn.config(state="disabled")
        self.simbrief_user.trace_add("write", lambda *_: self._update_fetch_state())

        ttk.Checkbutton(
            top_frame,
            text="Generate 10 NM FAF for arrival runway",
            variable=self.create_faf_var
        ).pack(anchor="w", pady=(4, 0))

        share_frame = ttk.Frame(top_frame)
        share_frame.pack(fill=tk.X, pady=(6, 0))
        ttk.Button(
            share_frame,
            text="Import Flight Plan",
            command=self.import_flight_plan
        ).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(
            share_frame,
            text="Export Flight Plan",
            command=self.export_flight_plan
        ).pack(side=tk.LEFT)

        # --- Middle Section: Waypoints Table ---
        table_frame = ttk.LabelFrame(left_pane, text=" Flight Plan Waypoints ", padding="8")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        columns = ("seq", "name", "type", "c130", "rwy", "elev")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse", height=9)

        self.tree.heading("seq", text="#")
        self.tree.heading("name", text="Ident")
        self.tree.heading("type", text="Type")
        self.tree.heading("c130", text="CNI Coordinates")
        self.tree.heading("rwy", text="Rwy")
        self.tree.heading("elev", text="Elev")

        self.tree.column("seq", width=30, anchor="center")
        self.tree.column("name", width=85, anchor="w")
        self.tree.column("type", width=50, anchor="center")
        self.tree.column("c130", width=160, anchor="center")
        self.tree.column("rwy", width=45, anchor="center")
        self.tree.column("elev", width=50, anchor="e")

        tree_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        tree_scroll.place(in_=self.tree, relx=1.0, rely=0.0, relheight=1.0, anchor="ne")

        self.tree.bind("<Double-1>", lambda _: self.edit_selected_waypoint())
        self.tree.bind("<Delete>", lambda _: self.delete_selected_waypoint())
        self.tree.bind("<Return>", lambda _: self.edit_selected_waypoint())
        self.tree.bind("<<TreeviewSelect>>", self._on_table_row_selected)

        # Table Control Buttons
        btn_bar = ttk.Frame(table_frame)
        btn_bar.pack(fill=tk.X, pady=(6, 0))

        ttk.Button(btn_bar, text="Add", width=6, command=self.add_waypoint).pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_bar, text="Edit", width=6, command=self.edit_selected_waypoint).pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_bar, text="Delete", width=7, command=self.delete_selected_waypoint).pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_bar, text="▲", width=3, command=lambda: self.shift_waypoint(-1)).pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_bar, text="▼", width=3, command=lambda: self.shift_waypoint(1)).pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_bar, text="+FAF", width=6, command=self.add_or_refresh_faf).pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_bar, text="Clear", width=6, command=self.clear_waypoints).pack(side=tk.RIGHT, padx=1)

        # --- Bottom Section: Database Commit ---
        bottom_frame = ttk.LabelFrame(left_pane, text=" DCS C-130J SimBridge Export ", padding="8")
        bottom_frame.pack(fill=tk.X, pady=(0, 6))

        db_box = ttk.Frame(bottom_frame)
        db_box.pack(fill=tk.X, pady=2)
        ttk.Label(db_box, text="DCS Database:").pack(side=tk.LEFT, padx=(0, 4))
        ttk.Entry(db_box, textvariable=self.db_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Button(db_box, text="...", width=3, command=self.browse_database).pack(side=tk.RIGHT)

        commit_box = ttk.Frame(bottom_frame)
        commit_box.pack(fill=tk.X, pady=4)
        ttk.Label(commit_box, text="Route Name:").pack(side=tk.LEFT, padx=(0, 4))
        ttk.Entry(commit_box, textvariable=self.custom_route_name, width=14).pack(side=tk.LEFT, padx=(0, 6))
        self.commit_btn = ttk.Button(
            commit_box,
            text="Insert Route to DCS",
            command=self.commit_route_to_database
        )
        self.commit_btn.pack(side=tk.RIGHT)

        # Log Area
        self.log_area = tk.Text(left_pane, height=4, state="disabled", bg="#f4f4f4", font=("Consolas", 8))
        self.log_area.pack(fill=tk.X)

        # =====================================================================
        # RIGHT PANE: INTERACTIVE MAP VIEW & CONTROLS
        # =====================================================================

        map_controls = ttk.Frame(right_pane)
        map_controls.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(map_controls, text="Map Layer:").pack(side=tk.LEFT, padx=(0, 4))
        layer_cb = ttk.Combobox(
            map_controls,
            textvariable=self.map_layer_var,
            values=["Google Hybrid", "Google Satellite", "OpenStreetMap", "OpenTopoMap"],
            state="readonly",
            width=15
        )
        layer_cb.pack(side=tk.LEFT, padx=(0, 10))
        layer_cb.bind("<<ComboboxSelected>>", self._on_map_layer_changed)

        ttk.Checkbutton(
            map_controls,
            text="Click Map to Add Waypoint",
            variable=self.click_to_add_var
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(map_controls, text="Center on Route", command=self.center_map_on_route).pack(side=tk.LEFT, padx=3)
        ttk.Button(map_controls, text="Center on Theater", command=self.center_map_on_theater).pack(side=tk.LEFT, padx=3)
        ttk.Button(map_controls, text="Export theaters.json", command=self.export_theaters_template).pack(side=tk.RIGHT)

        # Map Canvas / Widget container
        map_container = ttk.Frame(right_pane)
        map_container.pack(fill=tk.BOTH, expand=True)

        if HAS_MAPVIEW:
            self.map_widget = TkinterMapView(map_container, corner_radius=0)
            self.map_widget.pack(fill=tk.BOTH, expand=True)

            # Set initial tile server (Google Hybrid)
            self._apply_tile_server(self.map_layer_var.get())

            # Bind left click and right click commands
            self.map_widget.add_left_click_map_command(self.on_map_left_click)
            self.map_widget.add_right_click_menu_command("Add Custom Waypoint Here", self.on_map_right_click_add, pass_coords=True)
            self.map_widget.add_right_click_menu_command("Set as Departure Airport", self.on_map_set_dep, pass_coords=True)
            self.map_widget.add_right_click_menu_command("Set as Arrival Airport", self.on_map_set_arr, pass_coords=True)
        else:
            # Fallback simple coordinate canvas if TkinterMapView is not installed
            fallback_label = ttk.Label(
                map_container,
                text="Interactive map requires 'tkintermapview'. Run: pip install tkintermapview",
                font=("Segoe UI", 10, "italic")
            )
            fallback_label.pack(pady=40)

        # Status note at bottom of map
        ttk.Label(
            right_pane,
            text="Tip: Click anywhere on the map to place a waypoint. Drag to pan, scroll to zoom.",
            font=("Segoe UI", 8, "italic")
        ).pack(anchor="w", pady=(4, 0))

        self.log("Ready. Click on the map to add waypoints or fetch a plan from SimBrief.")

    # -------------------------------------------------------------------------
    # MAP INTERACTION & RENDERING
    # -------------------------------------------------------------------------

    def _apply_tile_server(self, layer_name):
        if not HAS_MAPVIEW or not hasattr(self, "map_widget"):
            return
        if layer_name == "Google Satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif layer_name == "Google Hybrid":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif layer_name == "OpenTopoMap":
            self.map_widget.set_tile_server("https://a.tile.opentopomap.org/{z}/{x}/{y}.png", max_zoom=17)
        else:
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png", max_zoom=19)

    def _on_map_layer_changed(self, _event=None):
        self._apply_tile_server(self.map_layer_var.get())

    def center_map_on_theater(self):
        if not HAS_MAPVIEW or not hasattr(self, "map_widget"):
            return
        theater_name = self.theater_var.get()
        center = THEATER_CENTERS.get(theater_name, (43.0, 42.0, 7))
        self.map_widget.set_position(center[0], center[1])
        self.map_widget.set_zoom(center[2])

    def center_map_on_route(self):
        if not HAS_MAPVIEW or not hasattr(self, "map_widget"):
            return
        valid_pts = [wp for wp in self.waypoints if wp.get("wp_type") != 7]
        if not valid_pts:
            return self.center_map_on_theater()

        lats = [wp["lat"] for wp in valid_pts]
        lons = [wp["lon"] for wp in valid_pts]
        center_lat = (min(lats) + max(lats)) / 2.0
        center_lon = (min(lons) + max(lons)) / 2.0

        lat_span = max(lats) - min(lats)
        lon_span = max(lons) - min(lons)
        max_span = max(lat_span, lon_span)

        if max_span < 0.5:
            zoom = 10
        elif max_span < 1.5:
            zoom = 9
        elif max_span < 3.0:
            zoom = 8
        elif max_span < 6.0:
            zoom = 7
        elif max_span < 12.0:
            zoom = 6
        else:
            zoom = 5

        self.map_widget.set_position(center_lat, center_lon)
        self.map_widget.set_zoom(zoom)

    def on_map_left_click(self, coords):
        """Handler for left-clicking on the map canvas."""
        if not self.click_to_add_var.get():
            return
        lat, lon = coords
        self.add_waypoint_at_coords(lat, lon)

    def on_map_right_click_add(self, coords):
        lat, lon = coords
        self.add_waypoint_at_coords(lat, lon)

    def on_map_set_dep(self, coords):
        lat, lon = coords
        dlg = WaypointDialog(self.root, title="Departure Airport", initial={
            "name": "ORIGIN",
            "type_label": "DEP",
            "wp_type": 2,
            "lat": round(lat, 5),
            "lon": round(lon, 5),
            "rwy": "",
            "elev": "0"
        })
        if dlg.result:
            if self.waypoints and self.waypoints[0].get("wp_type") == 2:
                self.waypoints[0] = dlg.result
            else:
                self.waypoints.insert(0, dlg.result)
            self.refresh_waypoints_table()
            self.refresh_map_display()

    def on_map_set_arr(self, coords):
        lat, lon = coords
        dlg = WaypointDialog(self.root, title="Arrival Airport", initial={
            "name": "DEST",
            "type_label": "ARR",
            "wp_type": 1,
            "lat": round(lat, 5),
            "lon": round(lon, 5),
            "rwy": "",
            "elev": "0"
        })
        if dlg.result:
            if self.waypoints and self.waypoints[-1].get("wp_type") == 1:
                self.waypoints[-1] = dlg.result
            else:
                self.waypoints.append(dlg.result)
            self.refresh_waypoints_table()
            self.refresh_map_display()

    def add_waypoint_at_coords(self, lat, lon):
        """Opens Add Waypoint dialog pre-filled with map click coordinates."""
        default_name = f"WP{len(self.waypoints) + 1}"
        initial_data = {
            "name": default_name,
            "type_label": "WPT",
            "wp_type": 0,
            "lat": round(lat, 5),
            "lon": round(lon, 5),
            "rwy": "",
            "elev": "-999"
        }
        dlg = WaypointDialog(self.root, title="Add Waypoint from Map", initial=initial_data)
        if dlg.result:
            # Insert before destination if arrival exists, else append
            dest_idx = -1
            for idx in range(len(self.waypoints) - 1, -1, -1):
                if self.waypoints[idx].get("wp_type") == 1:
                    dest_idx = idx
                    break

            insert_idx = dest_idx if dest_idx != -1 else len(self.waypoints)
            self.waypoints.insert(insert_idx, dlg.result)
            self.refresh_waypoints_table()
            self.refresh_map_display()
            self.log(f"Added waypoint '{dlg.result['name']}' at {dlg.result['lat']:.5f}, {dlg.result['lon']:.5f}")

    def on_marker_clicked(self, marker):
        """Highlights the clicked marker's corresponding row in the table."""
        idx = getattr(marker, "data", None)
        if idx is not None and 0 <= idx < len(self.waypoints):
            self.tree.selection_set(str(idx))
            self.tree.see(str(idx))

    def _on_table_row_selected(self, _event=None):
        selected = self.tree.selection()
        if not selected or not HAS_MAPVIEW or not hasattr(self, "map_widget"):
            return
        idx = int(selected[0])
        wp = self.waypoints[idx]
        if wp.get("wp_type") != 7:
            self.map_widget.set_position(wp["lat"], wp["lon"])

    def refresh_map_display(self):
        """Redraws route path and markers on the map widget."""
        if not HAS_MAPVIEW or not hasattr(self, "map_widget"):
            return

        self.map_widget.delete_all_marker()
        self.map_widget.delete_all_path()

        coords_path = []
        for idx, wp in enumerate(self.waypoints):
            if wp.get("wp_type") == 7:  # skip discontinuity
                continue

            coords_path.append((wp["lat"], wp["lon"]))

            wp_type = wp.get("wp_type", 0)
            type_lbl = wp.get("type_label", "WPT")

            if wp_type == 2:  # Departure
                circle_col = "#28A745"
                out_col = "#1E7E34"
            elif wp_type == 1:  # Arrival
                circle_col = "#DC3545"
                out_col = "#BD2130"
            elif type_lbl == "FAF":
                circle_col = "#FD7E14"
                out_col = "#D35400"
            else:  # Enroute
                circle_col = "#007BFF"
                out_col = "#0056B3"

            marker = self.map_widget.set_marker(
                wp["lat"], wp["lon"],
                text=wp["name"],
                marker_color_circle=circle_col,
                marker_color_outside=out_col,
                command=self.on_marker_clicked
            )
            marker.data = idx

        if len(coords_path) >= 2:
            self.map_widget.set_path(coords_path, color="#007BFF", width=3)

    # -------------------------------------------------------------------------
    # THEATER & RUNWAY HELPERS
    # -------------------------------------------------------------------------

    def _get_current_theater_airports(self):
        theater_name = self.theater_var.get()
        if theater_name in self.theaters:
            return self.theaters[theater_name].get("airports", {})
        return {}

    def _update_theater_airports(self):
        airports = self._get_current_theater_airports()
        airport_list = [""] + [f"{icao} - {data['name']}" for icao, data in airports.items()]

        self.dep_cb.config(values=airport_list)
        self.arr_cb.config(values=airport_list)

        self.dep_override_var.set("")
        self.arr_override_var.set("")
        self.dep_rwy_cb.config(values=[])
        self.arr_rwy_cb.config(values=[])

    def _on_theater_changed(self, _event=None):
        self.simbrief_prefill_opened = False
        self._update_theater_airports()
        self.center_map_on_theater()

    def _update_runways(self, override_var, cb_widget):
        val = override_var.get()
        if val:
            icao = val.split(" - ")[0]
            airports = self._get_current_theater_airports()
            if icao in airports:
                rwys = airports[icao].get("runways", [])
                cb_widget.config(values=rwys)
                if rwys:
                    cb_widget.current(0)
                return
        cb_widget.set("")
        cb_widget.config(values=[])

    def _on_airport_selected(self, airport_var, runway_widget):
        self.simbrief_prefill_opened = False
        self._update_runways(airport_var, runway_widget)
        self._update_fetch_state()

    def _update_fetch_state(self):
        """Enable SimBrief fetching only after its required inputs are ready."""
        has_airports = bool(self.dep_override_var.get() and self.arr_override_var.get())
        has_user = bool(self.simbrief_user.get().strip())
        has_prefill = self.simbrief_prefill_opened
        if hasattr(self, "fetch_btn"):
            self.fetch_btn.config(
                state="normal" if has_airports and has_user and has_prefill else "disabled"
            )

    def _clean_rwy(self, icao, raw_rwy):
        if not raw_rwy:
            return ""
        clean = re.sub(r"[A-Za-z]", "", str(raw_rwy)).strip()
        theater_data = self.theaters.get(self.theater_var.get(), {})
        mapping = theater_data.get("runway_mappings", {}).get(icao, {})
        if clean in mapping:
            clean = mapping[clean]
        return clean

    # -------------------------------------------------------------------------
    # LOGGING & UI THREADING
    # -------------------------------------------------------------------------

    def log(self, message):
        def _append():
            self.log_area.config(state="normal")
            self.log_area.insert(tk.END, message + "\n")
            self.log_area.see(tk.END)
            self.log_area.config(state="disabled")

        if threading.current_thread() is threading.main_thread():
            _append()
        else:
            self.root.after(0, _append)

    def browse_database(self):
        initial_dir = os.path.dirname(self.db_path.get()) if self.db_path.get() else os.path.expanduser("~")
        if not os.path.exists(initial_dir):
            initial_dir = os.path.expanduser("~")
        selected = filedialog.askopenfilename(
            title="Select user_data.db",
            initialdir=initial_dir,
            filetypes=(("SQLite Database", "*.db"), ("All Files", "*.*"))
        )
        if selected:
            self.db_path.set(os.path.normpath(selected))

    def open_simbrief_dispatch(self):
        dep_sel = self.dep_override_var.get()
        arr_sel = self.arr_override_var.get()
        if not dep_sel or not arr_sel:
            messagebox.showwarning(
                "Airports Required",
                "Select both departure and arrival airports before opening SimBrief.",
            )
            return

        airports = self._get_current_theater_airports()

        orig_proxy = airports.get(dep_sel.split(" - ")[0], {}).get("proxy", "") if dep_sel else ""
        dest_proxy = airports.get(arr_sel.split(" - ")[0], {}).get("proxy", "") if arr_sel else ""

        url = "https://www.simbrief.com/system/dispatch.php"
        url += f"?orig={orig_proxy}&dest={dest_proxy}"
        webbrowser.open(url)
        self.simbrief_prefill_opened = True
        self._update_fetch_state()

    # -------------------------------------------------------------------------
    # WAYPOINTS TABLE MANAGEMENT
    # -------------------------------------------------------------------------

    def refresh_waypoints_table(self):
        """Refreshes the Treeview display from the in-memory waypoints list."""
        self.tree.delete(*self.tree.get_children())
        for idx, wp in enumerate(self.waypoints, 1):
            c130_coord = dec_to_c130_coord(wp["lat"], wp["lon"]) if wp["wp_type"] != 7 else "--"
            self.tree.insert(
                "",
                tk.END,
                iid=str(idx - 1),
                values=(
                    idx,
                    wp["name"],
                    wp.get("type_label", "WPT"),
                    c130_coord,
                    wp.get("rwy", ""),
                    wp.get("elev", "-999")
                )
            )

    def add_waypoint(self):
        selected = self.tree.selection()
        dlg = WaypointDialog(self.root, title="Add Waypoint")
        if dlg.result:
            insert_idx = int(selected[0]) + 1 if selected else len(self.waypoints)
            self.waypoints.insert(insert_idx, dlg.result)
            self.refresh_waypoints_table()
            self.refresh_map_display()
            self.tree.selection_set(str(insert_idx))

    def edit_selected_waypoint(self):
        selected = self.tree.selection()
        if not selected:
            return
        idx = int(selected[0])
        current = self.waypoints[idx]
        dlg = WaypointDialog(self.root, title="Edit Waypoint", initial=current)
        if dlg.result:
            self.waypoints[idx] = dlg.result
            self.refresh_waypoints_table()
            self.refresh_map_display()
            self.tree.selection_set(str(idx))

    def delete_selected_waypoint(self):
        selected = self.tree.selection()
        if not selected:
            return
        idx = int(selected[0])
        del self.waypoints[idx]
        self.refresh_waypoints_table()
        self.refresh_map_display()
        if self.waypoints:
            new_sel = min(idx, len(self.waypoints) - 1)
            self.tree.selection_set(str(new_sel))

    def shift_waypoint(self, delta):
        selected = self.tree.selection()
        if not selected:
            return
        idx = int(selected[0])
        new_idx = idx + delta
        if 0 <= new_idx < len(self.waypoints):
            self.waypoints[idx], self.waypoints[new_idx] = self.waypoints[new_idx], self.waypoints[idx]
            self.refresh_waypoints_table()
            self.refresh_map_display()
            self.tree.selection_set(str(new_idx))

    def clear_waypoints(self):
        if not self.waypoints:
            return
        if messagebox.askyesno("Clear Waypoints", "Clear all waypoints from the flight plan?"):
            self.waypoints = []
            self.refresh_waypoints_table()
            self.refresh_map_display()
            self.log("Flight plan cleared.")

    def export_flight_plan(self):
        """Save the current route as a portable file for another operator."""
        if not self.waypoints:
            messagebox.showwarning("Export Flight Plan", "Add at least one waypoint before exporting.")
            return

        route_name = self.custom_route_name.get().strip()
        initial_name = f"{route_name or 'flight-plan'}.simbridge.json"
        target_path = filedialog.asksaveasfilename(
            title="Export Flight Plan",
            initialfile=initial_name,
            defaultextension=".simbridge.json",
            filetypes=(
                ("SimBridge Flight Plan", "*.simbridge.json"),
                ("JSON files", "*.json"),
                ("All Files", "*.*"),
            ),
        )
        if not target_path:
            return

        try:
            save_flight_plan(
                target_path,
                self.waypoints,
                route_name,
                self.theater_var.get(),
            )
        except (OSError, ValueError) as error:
            self.log(f"Flight-plan export failed: {error}")
            messagebox.showerror("Export Error", f"Could not export the flight plan:\n{error}")
            return

        self.log(f"Exported flight plan to: {target_path}")
        messagebox.showinfo(
            "Export Successful",
            f"Flight plan saved to:\n{target_path}\n\n"
            "Share this .simbridge.json file with other SimBridge operators.",
        )

    def import_flight_plan(self):
        """Load a route shared by another SimBridge operator."""
        source_path = filedialog.askopenfilename(
            title="Import Flight Plan",
            filetypes=(
                ("SimBridge Flight Plan", "*.simbridge.json"),
                ("JSON files", "*.json"),
                ("All Files", "*.*"),
            ),
        )
        if not source_path:
            return

        try:
            document = load_flight_plan(source_path)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            self.log(f"Flight-plan import failed: {error}")
            messagebox.showerror("Import Error", f"Could not import the flight plan:\n{error}")
            return

        if self.waypoints and not messagebox.askyesno(
            "Replace Flight Plan",
            "Importing this file will replace the current flight plan. Continue?",
        ):
            return

        self.waypoints = document["waypoints"]
        self.custom_route_name.set(document["route_name"])
        if document["theater"] in self.theaters:
            self.theater_var.set(document["theater"])
            self._update_theater_airports()
        self.refresh_waypoints_table()
        self.refresh_map_display()
        self.center_map_on_route()
        self.log(f"Imported {len(self.waypoints)} waypoints from: {source_path}")
        messagebox.showinfo(
            "Import Successful",
            f"Loaded flight plan '{document['route_name'] or 'Unnamed'}'.",
        )

    def export_theaters_template(self):
        """Exports the built-in theater database to theaters.json for customization."""
        script_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
        target_path = os.path.join(script_dir, "theaters.json")
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(self.theaters, f, indent=4, ensure_ascii=False)
            self.log(f"Exported theater database to: {target_path}")
            messagebox.showinfo("Export Successful", f"Saved theater database to:\n{target_path}\n\nYou can edit this file to add new maps or airbases.")
        except Exception as e:
            self.log(f"Error exporting theaters: {e}")
            messagebox.showerror("Export Error", f"Failed to export theaters.json:\n{e}")

    def add_or_refresh_faf(self):
        """Computes and inserts or updates a 10 NM FAF before the destination."""
        dest_wp = None
        dest_idx = -1
        for idx in range(len(self.waypoints) - 1, -1, -1):
            if self.waypoints[idx].get("wp_type") == 1:
                dest_wp = self.waypoints[idx]
                dest_idx = idx
                break

        if not dest_wp or not dest_wp.get("rwy"):
            messagebox.showwarning("FAF Generation", "Destination airport or runway is not specified.")
            return

        coords = generate_approach_fix(dest_wp["lat"], dest_wp["lon"], dest_wp["rwy"], dist_nm=10.0)
        if not coords:
            messagebox.showerror("FAF Generation", f"Could not compute FAF for runway '{dest_wp['rwy']}'.")
            return

        faf_lat, faf_lon = coords
        faf_name = f"RX{self._clean_rwy(dest_wp['name'], dest_wp['rwy'])}"[:6]
        faf_wp = {
            "name": faf_name,
            "type_label": "FAF",
            "wp_type": 0,
            "lat": faf_lat,
            "lon": faf_lon,
            "rwy": "",
            "elev": "-999"
        }

        if dest_idx > 0 and self.waypoints[dest_idx - 1].get("type_label") == "FAF":
            self.waypoints[dest_idx - 1] = faf_wp
        else:
            self.waypoints.insert(dest_idx, faf_wp)

        self.refresh_waypoints_table()
        self.refresh_map_display()
        self.log(f"Generated FAF '{faf_name}' at 10 NM on extended runway {dest_wp['rwy']} centerline.")

    # -------------------------------------------------------------------------
    # SIMBRIEF FETCHING
    # -------------------------------------------------------------------------

    def start_fetch_thread(self):
        username = self.simbrief_user.get().strip()
        if not username:
            messagebox.showwarning("Input Required", "Please enter a SimBrief username or Pilot ID.")
            return
        if not self.dep_override_var.get() or not self.arr_override_var.get():
            messagebox.showwarning(
                "Airports Required",
                "Select both departure and arrival airports before fetching a flight plan.",
            )
            return
        if not self.simbrief_prefill_opened:
            messagebox.showwarning(
                "SimBrief Prefill Required",
                "Open SimBrief Prefill before fetching the flight plan.",
            )
            return
        self.fetch_btn.config(state="disabled")
        threading.Thread(target=self._run_simbrief_fetch, args=(username,), daemon=True).start()

    def _run_simbrief_fetch(self, username):
        try:
            self.log("-" * 40)
            self.log(f"Fetching SimBrief flight plan for '{username}'...")

            param = "userid" if username.isdigit() else "username"
            url = f"https://www.simbrief.com/api/xml.fetcher.php?{param}={username}&json=1"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
            except Exception as e:
                self.log(f"SimBrief connection error: {e}")
                return

            if data.get("fetch", {}).get("status") != "Success":
                self.log("Error: No valid flight plan found on SimBrief.")
                return

            origin_data = data["origin"]
            dest_data = data["destination"]

            origin_icao = origin_data["icao_code"]
            origin_lat = float(origin_data["pos_lat"])
            origin_lon = float(origin_data["pos_long"])
            origin_elev = str(origin_data.get("elevation", "-999"))
            rwy_dep = self._clean_rwy(origin_icao, origin_data.get("plan_rwy", ""))

            dest_icao = dest_data["icao_code"]
            dest_lat = float(dest_data["pos_lat"])
            dest_lon = float(dest_data["pos_long"])
            dest_elev = str(dest_data.get("elevation", "-999"))
            rwy_arr = self._clean_rwy(dest_icao, dest_data.get("plan_rwy", ""))

            # Apply DCS airport overrides if chosen
            airports = self._get_current_theater_airports()
            dep_override = self.dep_override_var.get()
            if dep_override:
                dep_icao_sel = dep_override.split(" - ")[0]
                if dep_icao_sel in airports:
                    origin_icao = dep_icao_sel
                    origin_lat = airports[dep_icao_sel]["lat"]
                    origin_lon = airports[dep_icao_sel]["lon"]
                    origin_elev = str(airports[dep_icao_sel]["elev"])
                    rwy_dep = self.dep_rwy_var.get() or rwy_dep

            arr_override = self.arr_override_var.get()
            if arr_override:
                arr_icao_sel = arr_override.split(" - ")[0]
                if arr_icao_sel in airports:
                    dest_icao = arr_icao_sel
                    dest_lat = airports[arr_icao_sel]["lat"]
                    dest_lon = airports[arr_icao_sel]["lon"]
                    dest_elev = str(airports[arr_icao_sel]["elev"])
                    rwy_arr = self.arr_rwy_var.get() or rwy_arr

            # Extract enroute fixes
            raw_fixes = []
            if "navlog" in data and "fix" in data["navlog"]:
                fixes = data["navlog"]["fix"]
                if isinstance(fixes, dict):
                    fixes = [fixes]
                for fix in fixes:
                    ident = fix.get("ident", "")
                    if not ident or ident in (origin_data["icao_code"], dest_data["icao_code"]):
                        continue
                    if ident in ("TOC", "TOD", "BOD") or ident.startswith("DER") or ident.startswith("SS"):
                        continue
                    if re.match(r"^[A-Z]{2}\d{3}$", ident):
                        continue
                    via = str(fix.get("via", "")).upper()
                    if via in ("SID", "STAR") or "DEPARTURE" in via or "ARRIVAL" in via:
                        continue
                    if str(fix.get("is_sid", "0")) == "1" or str(fix.get("is_star", "0")) == "1":
                        continue
                    raw_fixes.append({
                        "name": ident[:10],
                        "type_label": "WPT",
                        "wp_type": 0,
                        "lat": float(fix["pos_lat"]),
                        "lon": float(fix["pos_long"]),
                        "rwy": "",
                        "elev": "-999"
                    })

            # Filter out overshoot waypoints (> direct distance + 15 NM)
            direct_dist = calculate_distance_nm(origin_lat, origin_lon, dest_lat, dest_lon)
            enroute_fixes = []
            for fix in raw_fixes:
                d = calculate_distance_nm(origin_lat, origin_lon, fix["lat"], fix["lon"])
                if d > (direct_dist + 15.0):
                    self.log(f"Excluded overshoot fix '{fix['name']}' ({d:.1f} NM).")
                    continue
                enroute_fixes.append(fix)

            # Assemble full flight plan list
            plan = [
                {
                    "name": origin_icao,
                    "type_label": "DEP",
                    "wp_type": 2,
                    "lat": origin_lat,
                    "lon": origin_lon,
                    "rwy": rwy_dep,
                    "elev": origin_elev
                },
                {
                    "name": ">> DISCONTINUITY <<",
                    "type_label": "DISC",
                    "wp_type": 7,
                    "lat": 0.0,
                    "lon": 0.0,
                    "rwy": "",
                    "elev": "-999"
                }
            ]
            plan.extend(enroute_fixes)

            # Generate FAF if requested and runway is available
            if self.create_faf_var.get() and rwy_arr:
                faf_coords = generate_approach_fix(dest_lat, dest_lon, rwy_arr, dist_nm=10.0)
                if faf_coords:
                    faf_name = f"RX{self._clean_rwy(dest_icao, rwy_arr)}"[:6]
                    plan.append({
                        "name": faf_name,
                        "type_label": "FAF",
                        "wp_type": 0,
                        "lat": faf_coords[0],
                        "lon": faf_coords[1],
                        "rwy": "",
                        "elev": "-999"
                    })
                    self.log(f"FAF '{faf_name}' computed (10 NM on runway {rwy_arr} axis).")

            plan.append({
                "name": dest_icao,
                "type_label": "ARR",
                "wp_type": 1,
                "lat": dest_lat,
                "lon": dest_lon,
                "rwy": rwy_arr,
                "elev": dest_elev
            })

            self.waypoints = plan
            default_route_name = f"{origin_icao}{dest_icao}"[:12]
            if not self.custom_route_name.get().strip():
                self.custom_route_name.set(default_route_name)

            self.root.after(0, self.refresh_waypoints_table)
            self.root.after(0, self.refresh_map_display)
            self.root.after(0, self.center_map_on_route)
            self.log(f"Loaded {len(self.waypoints)} waypoints for {origin_icao} -> {dest_icao} from SimBrief.")
            self.log("Review, edit, or click on the map to add custom waypoints before inserting.")

        finally:
            self.root.after(0, lambda: self.fetch_btn.config(state="normal"))

    # -------------------------------------------------------------------------
    # DATABASE COMMIT
    # -------------------------------------------------------------------------

    def commit_route_to_database(self):
        """Writes the flight plan into the CNI SQLite database."""
        db_path = self.db_path.get().strip()
        if not db_path:
            messagebox.showerror("Error", "Please specify a database path.")
            return

        if not os.path.exists(db_path):
            messagebox.showerror("Error", f"Database file not found at:\n{db_path}")
            return

        if len(self.waypoints) < 2:
            messagebox.showwarning("Warning", "Flight plan must contain at least departure and arrival waypoints.")
            return

        # Determine origin and destination
        dep_wp = None
        arr_wp = None
        for wp in self.waypoints:
            if wp["wp_type"] == 2 and not dep_wp:
                dep_wp = wp
            elif wp["wp_type"] == 1:
                arr_wp = wp

        origin_name = dep_wp["name"] if dep_wp else self.waypoints[0]["name"]
        dest_name = arr_wp["name"] if arr_wp else self.waypoints[-1]["name"]
        rwy_dep = dep_wp.get("rwy", "") if dep_wp else ""
        rwy_arr = arr_wp.get("rwy", "") if arr_wp else ""

        route_name = self.custom_route_name.get().strip()[:12]
        if not route_name:
            route_name = f"{origin_name}{dest_name}"[:12]

        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()

            c.execute("""
                CREATE TABLE IF NOT EXISTS custom_data (
                    name TEXT PRIMARY KEY,
                    entry_pos TEXT,
                    lat REAL,
                    lon REAL
                )
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS routes (
                    name TEXT PRIMARY KEY,
                    wpt_trans INTEGER,
                    main_pts TEXT,
                    alt_pts TEXT,
                    origin TEXT,
                    dest TEXT,
                    alt TEXT,
                    rwy_dep TEXT,
                    rwy_arr TEXT,
                    rwy_dep_return TEXT,
                    rwy_alt TEXT,
                    rwy_dep_sid TEXT,
                    rwy_arr_star TEXT,
                    rwy_alt_star TEXT,
                    rwy_dep_return_star TEXT,
                    rwy_dep_trans TEXT,
                    rwy_arr_trans TEXT
                )
            """)

            for wp in self.waypoints:
                if wp["wp_type"] != 7:
                    c.execute(
                        "INSERT OR REPLACE INTO custom_data (name, entry_pos, lat, lon) VALUES (?, ?, ?, ?)",
                        (wp["name"], dec_to_c130_coord(wp["lat"], wp["lon"]), wp["lat"], wp["lon"])
                    )

            pts_list = [
                format_c130_waypoint(
                    wp["name"],
                    wp["wp_type"],
                    wp["lat"],
                    wp["lon"],
                    rwy=wp.get("rwy", ""),
                    elev=wp.get("elev", "-999")
                )
                for wp in self.waypoints
            ]

            c.execute("""
                INSERT OR REPLACE INTO routes 
                (name, wpt_trans, main_pts, alt_pts, origin, dest, alt, rwy_dep, rwy_arr,
                 rwy_dep_return, rwy_alt, rwy_dep_sid, rwy_arr_star, rwy_alt_star,
                 rwy_dep_return_star, rwy_dep_trans, rwy_arr_trans) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                route_name,
                0,
                ",".join(pts_list),
                "",
                origin_name,
                dest_name,
                "XX",
                rwy_dep,
                rwy_arr,
                "", "", "", "", "", "", "", ""
            ))

            conn.commit()
            conn.close()

            self.log(f"Successfully inserted route '{route_name}' ({len(self.waypoints)} waypoints) into {os.path.basename(db_path)}.")
            messagebox.showinfo("Success", f"Flight plan '{route_name}' successfully committed to CNI database.")

        except Exception as e:
            self.log(f"Database error: {e}")
            messagebox.showerror("Database Error", f"Failed to write to database:\n{e}")


# -----------------------------------------------------------------------------
# ENTRY POINT
# -----------------------------------------------------------------------------
