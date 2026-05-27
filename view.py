"""Ansichtskomponente für das Studien-Dashboard mit customtkinter."""

from datetime import date

import customtkinter as ctk
from tkinter import messagebox, Canvas
from controller import DashboardController
from domain import (
    Studiengang,
    Pruefungsleistung,
    Modul,
    WAHLPFLICHT_A_B,
    WAHLPFLICHT_C,
)

# Sortierte Listen für die Dropdown-Menüs
WAHLPFLICHTMODULE_A_B = ["Bitte wählen...", *sorted(WAHLPFLICHT_A_B)]
WAHLPFLICHTMODULE_C   = ["Bitte wählen...", *sorted(WAHLPFLICHT_C)]

# ---------------------------------------------------------------------------
# _SHARED_COLORS: Akzente und Status-Farben (beide Modi gleich)
# _THEMES:        Hintergründe, Texte, Badges (modusabhängig)
# ---------------------------------------------------------------------------
_SHARED_COLORS = {
    "accent":  "#6c8cff",
    "success": "#4ade80",
    "warning": "#fbbf24",
}

_THEMES = {
    "dark": {
        "bg":       "#1a1d23",
        "panel":    "#22262e",
        "border":   "#333842",
        "surface":  "#2a2e38",
        "text":     "#e4e6eb",
        "text_sec": "#8b8fa3",
        "text_dim": "#5c6070",
        "badge_ok": "#16291a",
        "badge_warn": "#2a2214",
        "badge_open": "#1e2130",
    },
    "light": {
        "bg":       "#f4f5f8",
        "panel":    "#ffffff",
        "border":   "#dcdde3",
        "surface":  "#e8eaef",
        "text":     "#1a1d23",
        "text_sec": "#5c6070",
        "text_dim": "#8b8fa3",
        "badge_ok": "#dcfce7",
        "badge_warn": "#fef3c7",
        "badge_open": "#e8eaef",
    },
}


# ---------------------------------------------------------------------------
# Custom ComboBox
# ---------------------------------------------------------------------------
class _CTkComboBox(ctk.CTkComboBox):
    """CTkComboBox mit korrekter Dropdown-Interaktion."""

    def _create_bindings(self, sequence=None):
        if not hasattr(self, "_canvas"):
            return
        self._canvas.tag_bind("right_parts", "<Enter>", self._on_enter)
        self._canvas.tag_bind("dropdown_arrow", "<Enter>", self._on_enter)
        self._canvas.tag_bind("right_parts", "<Leave>", self._on_leave)
        self._canvas.tag_bind("dropdown_arrow", "<Leave>", self._on_leave)
        self._canvas.tag_bind("right_parts", "<ButtonRelease-1>", self._clicked)
        self._canvas.tag_bind("dropdown_arrow", "<ButtonRelease-1>", self._clicked)


def _scroll_bind(widget, callback) -> None:
    """Bindet Mausrad-Scrolling rekursiv an ein Widget und alle Kinder."""
    widget.bind("<MouseWheel>", callback, add="+")
    widget.bind("<Button-4>", callback, add="+")
    widget.bind("<Button-5>", callback, add="+")
    for child in widget.winfo_children():
        if "combobox" not in type(child).__name__.lower():
            _scroll_bind(child, callback)


# ===========================================================================
class DashboardView:
    """
    Hauptansicht des Studien-Dashboards.

    Seitenstruktur:
        .header      - Titel | Hochschule + Buttons
        .kpis        - ECTS / Note / Zeit
        .bottom-grid - Semester links | Module + Noten + Wahlpflicht rechts
        .open-panel  - Offene Prüfungsleistungen (3×2-Grid)
    """

    def __init__(self, controller: DashboardController) -> None:
        self.controller = controller
        self.studiengang: Studiengang | None = None
        self._theme = "dark"
        self._theme_widgets: dict = {}  # widget -> {config_key: theme_key, ...}

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Studien-Dashboard")
        self.root.geometry("1240x900")
        self.root.minsize(1100, 800)
        self.root.configure(fg_color=self._t("bg"))
        self._reg(self.root, fg_color="bg")

        self._scroll = ctk.CTkScrollableFrame(
            self.root, fg_color=self._t("bg"),
            scrollbar_button_color=self._t("border"),
            scrollbar_button_hover_color=self._t("border"),
        )
        self._scroll.pack(fill="both", expand=True)
        self._scroll.grid_columnconfigure(0, weight=1)
        self._reg(self._scroll, fg_color="bg",
                  scrollbar_button_color="border",
                  scrollbar_button_hover_color="border")

        self._header_erstellen()
        self._kpis_erstellen()
        self._bottom_grid_erstellen()
        self._open_panel_erstellen()

        self._scroll_callback = self._on_mousewheel
        self.root.after(200, self._scroll_bindings_setzen)

    # -------------------------------------------------------------------
    # Theme-Hilfen
    # -------------------------------------------------------------------

    def _t(self, key: str) -> str:
        """Farbe aus der aktuellen Palette zurückgeben (mit Shared-Fallback)."""
        return _THEMES[self._theme].get(key, _SHARED_COLORS.get(key, ""))

    def _reg(self, widget, **mapping) -> None:
        """Widget für Theme-Wechsel registrieren.

        mapping: config_option -> theme_key, z.B. fg_color="panel"
        """
        self._theme_widgets[widget] = mapping

    def _apply_theme(self) -> None:
        """Alle registrierten Widgets auf die aktuelle Palette umstellen."""
        for widget, mapping in self._theme_widgets.items():
            try:
                for config_key, theme_key in mapping.items():
                    widget.configure(**{config_key: self._t(theme_key)})
            except Exception:
                pass  # Widget ggf. bereits zerstört
        # Canvas hat bg statt fg_color
        self.tl_canvas.configure(bg=self._t("panel"))

    def _theme_wechseln(self) -> None:
        """Zwischen Dark- und Light-Mode umschalten."""
        self._theme = "light" if self._theme == "dark" else "dark"
        ctk.set_appearance_mode(self._theme)
        self.btn_theme.configure(
            text="☀️" if self._theme == "dark" else "🌙")
        self._apply_theme()
        if self.studiengang:
            self._anzeige_aktualisieren()

    # -------------------------------------------------------------------
    # Widget-Helfer
    # -------------------------------------------------------------------

    def _panel(self, parent, **kw):
        """Dunkle Panel-Kachel mit Rand."""
        frame = ctk.CTkFrame(
            parent, fg_color=self._t("panel"),
            border_color=self._t("border"), border_width=1,
            corner_radius=12, **kw,
        )
        self._reg(frame, fg_color="panel", border_color="border")
        return frame

    def _label(self, parent, text="", size=12, color=None, weight="normal",
               anchor="w", **kw):
        """Label mit einheitlicher Schrift. color=None → theme 'text'."""
        if color is None:
            color = self._t("text")
        return ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(size=size, weight=weight),
            text_color=color, anchor=anchor, **kw,
        )

    def _progress(self, parent, color=None, height=6):
        """Fortschrittsbalken."""
        if color is None:
            color = self._t("accent")
        bar = ctk.CTkProgressBar(
            parent, orientation="horizontal",
            height=height, corner_radius=height // 2,
            fg_color=self._t("surface"), progress_color=color,
            border_width=0,
        )
        bar.set(0)
        self._reg(bar, fg_color="surface")
        return bar

    def _sep(self, parent):
        """1px-Trennlinie."""
        frame = ctk.CTkFrame(parent, height=1, fg_color=self._t("border"))
        self._reg(frame, fg_color="border")
        return frame

    # -------------------------------------------------------------------
    # Scroll-Handler
    # -------------------------------------------------------------------

    def _on_mousewheel(self, event) -> None:
        if str(event.num) in ("4", "Button-4"):
            self._scroll._parent_canvas.yview_scroll(-1, "units")
        elif str(event.num) in ("5", "Button-5"):
            self._scroll._parent_canvas.yview_scroll(1, "units")
        else:
            self._scroll._parent_canvas.yview_scroll(
                int(-event.delta / 120), "units")

    def _scroll_bindings_setzen(self) -> None:
        _scroll_bind(self._scroll, self._scroll_callback)

    # -----------------------------------------------------------------------
    # Header
    # -----------------------------------------------------------------------

    def _header_erstellen(self) -> None:
        header = ctk.CTkFrame(self._scroll, fg_color=self._t("bg"))
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 0))
        header.grid_columnconfigure(0, weight=1)
        self._reg(header, fg_color="bg")

        links = ctk.CTkFrame(header, fg_color=self._t("bg"))
        links.grid(row=0, column=0, sticky="w")
        self._reg(links, fg_color="bg")

        self.lbl_title = self._label(links, "Studien-Dashboard", size=20,
                                     color=self._t("text"), weight="bold")
        self.lbl_title.pack(anchor="w")
        self._reg(self.lbl_title, text_color="text")

        self.lbl_studiengang = self._label(links, "", size=13,
                                           color=self._t("text_sec"))
        self.lbl_studiengang.pack(anchor="w")
        self._reg(self.lbl_studiengang, text_color="text_sec")

        rechts = ctk.CTkFrame(header, fg_color=self._t("bg"))
        rechts.grid(row=0, column=1, sticky="e")
        self._reg(rechts, fg_color="bg")

        self.lbl_hochschule = self._label(rechts, "IU Internationale Hochschule",
                                          size=13, color=self._t("text_sec"))
        self.lbl_hochschule.grid(row=0, column=0, columnspan=3,
                                 sticky="e", pady=(0, 6))
        self._reg(self.lbl_hochschule, text_color="text_sec")

        self.btn_speichern = ctk.CTkButton(
            rechts, text="Speichern", command=self._speichern,
            width=100, height=28, corner_radius=8,
            fg_color=self._t("success"), hover_color=self._t("success"),
            text_color=self._t("bg"), font=ctk.CTkFont(size=12),
        )
        self.btn_speichern.grid(row=1, column=0, padx=(0, 6))
        self._reg(self.btn_speichern, fg_color="success",
                  hover_color="success", text_color="bg")

        self.btn_neu = ctk.CTkButton(
            rechts, text="Neu laden", command=self._neu_laden,
            width=100, height=28, corner_radius=8,
            fg_color=self._t("surface"), hover_color=self._t("border"),
            text_color=self._t("text"), font=ctk.CTkFont(size=12),
        )
        self.btn_neu.grid(row=1, column=1)
        self._reg(self.btn_neu, fg_color="surface",
                  hover_color="border", text_color="text")

        # Hell/Dark Toggle-Button
        self.btn_theme = ctk.CTkButton(
            rechts, text="☀️", width=34, height=28, corner_radius=8,
            fg_color=self._t("surface"), hover_color=self._t("border"),
            text_color=self._t("text"), font=ctk.CTkFont(size=13),
            command=self._theme_wechseln,
        )
        self.btn_theme.grid(row=1, column=2, padx=(6, 0))
        self._reg(self.btn_theme, fg_color="surface",
                  hover_color="border", text_color="text")

        sep = self._sep(self._scroll)
        sep.grid(row=0, column=0, sticky="sew", padx=16, pady=(68, 0))

    # -----------------------------------------------------------------------
    # KPI-Kacheln
    # -----------------------------------------------------------------------

    def _kpis_erstellen(self) -> None:
        wrap = ctk.CTkFrame(self._scroll, fg_color=self._t("bg"))
        wrap.grid(row=1, column=0, sticky="ew", padx=16, pady=(12, 0))
        wrap.grid_columnconfigure((0, 1, 2), weight=1)
        self._reg(wrap, fg_color="bg")

        # --- ECTS ---
        k = self._panel(wrap)
        k.grid(row=0, column=0, padx=(0, 6), sticky="nsew")
        lbl = self._label(k, "ECTS", size=11, color=self._t("text_dim"))
        lbl.pack(anchor="w", padx=14, pady=(14, 0))
        self._reg(lbl, text_color="text_dim")

        self.lbl_ects_val = self._label(k, "0 / 180", size=26,
                                        color=self._t("text"), weight="bold")
        self.lbl_ects_val.pack(anchor="w", padx=14, pady=(2, 0))
        self._reg(self.lbl_ects_val, text_color="text")

        self.bar_ects = self._progress(k, self._t("success"), 6)
        self.bar_ects.pack(fill="x", padx=14, pady=(6, 2))

        self.lbl_ects_pct = self._label(k, "0 % abgeschlossen", size=12,
                                        color=self._t("text_dim"))
        self.lbl_ects_pct.pack(anchor="w", padx=14, pady=(0, 14))
        self._reg(self.lbl_ects_pct, text_color="text_dim")

        # --- Notendurchschnitt ---
        k = self._panel(wrap)
        k.grid(row=0, column=1, padx=6, sticky="nsew")
        lbl = self._label(k, "Notendurchschnitt", size=11,
                          color=self._t("text_dim"))
        lbl.pack(anchor="w", padx=14, pady=(14, 0))
        self._reg(lbl, text_color="text_dim")

        self.lbl_note_val = self._label(k, "-", size=26,
                                        color=self._t("text"), weight="bold")
        self.lbl_note_val.pack(anchor="w", padx=14, pady=(2, 0))
        self._reg(self.lbl_note_val, text_color="text")

        ziel_note_row = ctk.CTkFrame(k, fg_color=self._t("panel"))
        ziel_note_row.pack(fill="x", padx=14)
        self._reg(ziel_note_row, fg_color="panel")
        lbl_ziel_note = self._label(ziel_note_row, "Ziel:", size=10,
                                    color=self._t("text_dim"))
        lbl_ziel_note.pack(side="left")
        self._reg(lbl_ziel_note, text_color="text_dim")
        self.entry_ziel_note = ctk.CTkEntry(
            ziel_note_row, width=50, height=22,
            fg_color=self._t("surface"), border_color=self._t("border"),
            text_color=self._t("warning"), corner_radius=4,
            font=ctk.CTkFont(size=11),
        )
        self.entry_ziel_note.pack(side="left", padx=(4, 0))
        self._reg(self.entry_ziel_note, fg_color="surface",
                  border_color="border", text_color="warning")
        self.entry_ziel_note.bind("<FocusOut>", self._ziel_note_aktualisieren)

        self.bar_note = self._progress(k, self._t("warning"), 6)
        self.bar_note.pack(fill="x", padx=14, pady=(6, 2))

        self.lbl_note_pct = self._label(k, "", size=12,
                                        color=self._t("text_dim"))
        self.lbl_note_pct.pack(anchor="w", padx=14, pady=(0, 14))
        self._reg(self.lbl_note_pct, text_color="text_dim")

        # --- Studienzeit ---
        k = self._panel(wrap)
        k.grid(row=0, column=2, padx=(6, 0), sticky="nsew")
        lbl = self._label(k, "Studienzeit", size=11,
                          color=self._t("text_dim"))
        lbl.pack(anchor="w", padx=14, pady=(14, 0))
        self._reg(lbl, text_color="text_dim")

        self.lbl_zeit_val = self._label(k, "0 Monate", size=26,
                                        color=self._t("text"), weight="bold")
        self.lbl_zeit_val.pack(anchor="w", padx=14, pady=(2, 0))
        self._reg(self.lbl_zeit_val, text_color="text")

        self.lbl_zeit_sub = self._label(k, "", size=12,
                                        color=self._t("text_dim"))
        self.lbl_zeit_sub.pack(anchor="w", padx=14)
        self._reg(self.lbl_zeit_sub, text_color="text_dim")

        self.tl_canvas = Canvas(k, height=10, bg=self._t("panel"),
                                highlightthickness=0, bd=0)
        self.tl_canvas.pack(fill="x", padx=14, pady=(6, 2))

        tl_labels = ctk.CTkFrame(k, fg_color=self._t("panel"))
        tl_labels.pack(fill="x", padx=14)
        self._reg(tl_labels, fg_color="panel")
        self.lbl_tl_start = self._label(tl_labels, "-", size=10,
                            color=self._t("text_dim"))
        self.lbl_tl_start.pack(side="left")
        self._reg(self.lbl_tl_start, text_color="text_dim")
        self.lbl_tl_end = self._label(tl_labels, "-", size=10,
                            color=self._t("text_dim"))
        self.lbl_tl_end.pack(side="right")
        self._reg(self.lbl_tl_end, text_color="text_dim")

        tl_sub = ctk.CTkFrame(k, fg_color=self._t("panel"))
        tl_sub.pack(fill="x", padx=14, pady=(2, 14))
        self._reg(tl_sub, fg_color="panel")

        self.lbl_tl_done = self._label(tl_sub, "", size=10,
                                       color=self._t("success"))
        self.lbl_tl_done.pack(side="left")
        self._reg(self.lbl_tl_done, text_color="success")

        lbl_today = self._label(tl_sub, "Heute", size=10,
                                color=self._t("accent"))
        lbl_today.pack(side="left", padx=6)
        self._reg(lbl_today, text_color="accent")

        self.lbl_tl_offen = self._label(tl_sub, "", size=10,
                                        color=self._t("text_dim"))
        self.lbl_tl_offen.pack(side="right")
        self._reg(self.lbl_tl_offen, text_color="text_dim")

        # --- Einstellungszeile: Startdatum + Zieldauer ---
        zeit_einst = ctk.CTkFrame(k, fg_color=self._t("panel"))
        zeit_einst.pack(fill="x", padx=14, pady=(6, 10))
        zeit_einst.grid_columnconfigure((0, 2), weight=0)
        self._reg(zeit_einst, fg_color="panel")

        lbl = self._label(zeit_einst, "Start:", size=10,
                          color=self._t("text_dim"))
        lbl.grid(row=0, column=0, sticky="e", padx=(0, 3), pady=2)
        self._reg(lbl, text_color="text_dim")

        self.entry_startdatum = ctk.CTkEntry(
            zeit_einst, width=100, height=22,
            fg_color=self._t("surface"), border_color=self._t("border"),
            text_color=self._t("text"), corner_radius=4,
            font=ctk.CTkFont(size=10), placeholder_text="YYYY-MM-DD",
        )
        self.entry_startdatum.grid(row=0, column=1, padx=(0, 8), pady=2)
        self._reg(self.entry_startdatum, fg_color="surface",
                  border_color="border", text_color="text")
        self.entry_startdatum.bind("<FocusOut>", self._startdatum_aktualisieren)

        lbl = self._label(zeit_einst, "Monate:", size=10,
                          color=self._t("text_dim"))
        lbl.grid(row=0, column=2, sticky="e", padx=(0, 3), pady=2)
        self._reg(lbl, text_color="text_dim")

        self.entry_ziel_monate = ctk.CTkEntry(
            zeit_einst, width=50, height=22,
            fg_color=self._t("surface"), border_color=self._t("border"),
            text_color=self._t("text"), corner_radius=4,
            font=ctk.CTkFont(size=10),
        )
        self.entry_ziel_monate.grid(row=0, column=3, padx=(0, 0), pady=2)
        self._reg(self.entry_ziel_monate, fg_color="surface",
                  border_color="border", text_color="text")
        self.entry_ziel_monate.bind("<FocusOut>", self._ziel_monate_aktualisieren)

    # -----------------------------------------------------------------------
    # Unteres Grid
    # -----------------------------------------------------------------------

    def _bottom_grid_erstellen(self) -> None:
        grid = ctk.CTkFrame(self._scroll, fg_color=self._t("bg"))
        grid.grid(row=2, column=0, sticky="ew", padx=16, pady=(12, 0))
        grid.grid_columnconfigure((0, 1), weight=1)
        self._reg(grid, fg_color="bg")

        self._semester_panel_erstellen(grid)
        self._modul_panel_erstellen(grid)

    def _semester_panel_erstellen(self, parent) -> None:
        panel = self._panel(parent)
        panel.grid(row=0, column=0, padx=(0, 6), sticky="nsew")

        lbl = self._label(panel, "ECTS pro Semester", size=11,
                          color=self._t("text_dim"))
        lbl.pack(anchor="w", padx=14, pady=(14, 10))
        self._reg(lbl, text_color="text_dim")

        self.sem_bars:  list[ctk.CTkProgressBar] = []
        self.sem_ects:  list[ctk.CTkLabel]        = []
        self.sem_icons: list[ctk.CTkLabel]        = []

        for i in range(1, 7):
            row = ctk.CTkFrame(panel, fg_color=self._t("panel"))
            row.pack(fill="x", padx=14, pady=2)
            self._reg(row, fg_color="panel")

            lbl = self._label(row, f"Sem {i}", size=12,
                              color=self._t("text_sec"), width=46)
            lbl.pack(side="left")
            self._reg(lbl, text_color="text_sec")

            bar_bg = ctk.CTkFrame(row, fg_color=self._t("surface"),
                                  height=8, corner_radius=4)
            bar_bg.pack(side="left", fill="x", expand=True, padx=8)
            bar_bg.pack_propagate(False)
            self._reg(bar_bg, fg_color="surface")

            bar = ctk.CTkProgressBar(
                bar_bg, height=8, corner_radius=4,
                fg_color=self._t("surface"),
                progress_color=self._t("success"),
                border_width=0,
            )
            bar.set(0)
            bar.pack(fill="x", expand=True)
            self._reg(bar, fg_color="surface")

            icon = self._label(row, "○", size=13,
                               color=self._t("text_dim"),
                               width=18, anchor="center")
            icon.pack(side="right")
            self._reg(icon, text_color="text_dim")

            ects = self._label(row, "0 / 30", size=11,
                               color=self._t("text_dim"),
                               width=56, anchor="e")
            ects.pack(side="right", padx=(0, 4))
            self._reg(ects, text_color="text_dim")

            self.sem_bars.append(bar)
            self.sem_ects.append(ects)
            self.sem_icons.append(icon)

        sep = self._sep(panel)
        sep.pack(fill="x", pady=(10, 0))

    def _modul_panel_erstellen(self, parent) -> None:
        self._modul_panel = self._panel(parent)
        self._modul_panel.grid(row=0, column=1, padx=(6, 0), sticky="nsew")

        lbl = self._label(self._modul_panel, "Module und Noten", size=11,
                          color=self._t("text_dim"))
        lbl.pack(anchor="w", padx=14, pady=(14, 6))
        self._reg(lbl, text_color="text_dim")

        kopf = ctk.CTkFrame(self._modul_panel, fg_color=self._t("panel"))
        kopf.pack(fill="x", padx=14)
        kopf.grid_columnconfigure(0, weight=1)
        self._reg(kopf, fg_color="panel")

        for col, (txt, w) in enumerate([
            ("Modul", 0), ("Note", 46), ("ECTS", 36),
            ("Datum", 96), ("Status", 90),
        ]):
            if col == 0:
                lbl = self._label(kopf, txt, size=11,
                                  color=self._t("text_dim"))
                lbl.grid(row=0, column=col, sticky="w", padx=(2, 0))
            else:
                lbl = self._label(kopf, txt, size=11,
                                  color=self._t("text_dim"),
                                  width=w, anchor="center")
                lbl.grid(row=0, column=col, padx=2)
            self._reg(lbl, text_color="text_dim")

        sep = self._sep(self._modul_panel)
        sep.pack(fill="x", padx=14, pady=(4, 2))

        self.modul_scroll = ctk.CTkScrollableFrame(
            self._modul_panel, fg_color=self._t("panel"), height=280,
        )
        self.modul_scroll.pack(fill="both", expand=True, padx=14, pady=(0, 4))
        self.modul_scroll.grid_columnconfigure(0, weight=1)
        self._reg(self.modul_scroll, fg_color="panel")

        self.modul_badges: list[ctk.CTkLabel] = []
        self.note_entries: list[ctk.CTkEntry] = []
        self.datum_entries: list[ctk.CTkEntry] = []

        sep = self._sep(self._modul_panel)
        sep.pack(fill="x", padx=14, pady=(4, 0))

        lbl = self._label(self._modul_panel, "Wahlpflichtmodule", size=11,
                          color=self._t("text_dim"))
        lbl.pack(anchor="w", padx=14, pady=(8, 4))
        self._reg(lbl, text_color="text_dim")

        for lbl_text, attr_name, values, cmd in [
            ("Wahlpflicht A (Sem 5):", "dropdown_wp_a",
             WAHLPFLICHTMODULE_A_B, self._wahlpflicht_a_geaendert),
            ("Wahlpflicht B (Sem 6):", "dropdown_wp_b",
             WAHLPFLICHTMODULE_A_B, self._wahlpflicht_b_geaendert),
            ("Wahlpflicht C (Sem 6):", "dropdown_wp_c",
             WAHLPFLICHTMODULE_C,   self._wahlpflicht_c_geaendert),
        ]:
            row = ctk.CTkFrame(self._modul_panel, fg_color=self._t("panel"))
            row.pack(fill="x", padx=14, pady=3)
            self._reg(row, fg_color="panel")

            lbl = self._label(row, lbl_text, size=11,
                              color=self._t("text_sec"), width=130)
            lbl.pack(side="left")
            self._reg(lbl, text_color="text_sec")

            cb = _CTkComboBox(
                row, values=values, width=280, command=cmd,
                fg_color=self._t("surface"), border_color=self._t("border"),
                button_color=self._t("border"),
                button_hover_color=self._t("text_sec"),
                text_color=self._t("text"),
                font=ctk.CTkFont(size=11),
            )
            cb.pack(side="left")
            self._reg(cb, fg_color="surface", border_color="border",
                      button_color="border",
                      button_hover_color="text_sec",
                      text_color="text")
            setattr(self, attr_name, cb)

    def _modul_tabelle_fuellen(self) -> None:
        """Bevölkert die Modul-Tabelle mit editierbaren Zeilen."""
        for w in self.modul_scroll.winfo_children():
            w.destroy()
        self.modul_badges.clear()
        self.note_entries.clear()
        self.datum_entries.clear()

        pruefungen = (
            pruefung
            for sem in self.studiengang.semester
            for modul in sem.module
            for pruefung in modul.pruefungsleistungen
        )

        for index, pruefung in enumerate(pruefungen):
            zeile = ctk.CTkFrame(self.modul_scroll, fg_color=self._t("panel"))
            zeile.pack(fill="x", pady=1)
            zeile.grid_columnconfigure(0, weight=1)
            self._reg(zeile, fg_color="panel")

            lbl = self._label(zeile, pruefung.name, size=12,
                              color=self._t("text_sec"))
            lbl.grid(row=0, column=0, sticky="w", padx=(4, 6))
            self._reg(lbl, text_color="text_sec")

            ne = ctk.CTkEntry(
                zeile, width=42, height=22,
                fg_color=self._t("surface"), border_color=self._t("border"),
                text_color=self._t("success"), corner_radius=4,
                font=ctk.CTkFont(size=12),
            )
            ne.grid(row=0, column=1, padx=2)
            if pruefung.note is not None:
                ne.insert(0, str(pruefung.note))
            ne.bind("<FocusOut>",
                    lambda e, idx=index: self._note_aktualisieren(idx, e))
            self._reg(ne, fg_color="surface", border_color="border",
                      text_color="success")
            self.note_entries.append(ne)

            lbl = self._label(zeile, str(pruefung.ects_punkte), size=12,
                              color=self._t("text_sec"), width=36,
                              anchor="center")
            lbl.grid(row=0, column=2, padx=2)
            self._reg(lbl, text_color="text_sec")

            de = ctk.CTkEntry(
                zeile, width=92, height=22,
                fg_color=self._t("surface"), border_color=self._t("border"),
                text_color=self._t("text"), corner_radius=4,
                font=ctk.CTkFont(size=11),
            )
            de.grid(row=0, column=3, padx=2)
            if pruefung.datum != "offen":
                de.insert(0, pruefung.datum)
            de.bind("<FocusOut>",
                    lambda e, idx=index: self._datum_aktualisieren(idx, e))
            self._reg(de, fg_color="surface", border_color="border",
                      text_color="text")
            self.datum_entries.append(de)

            badge = self._badge_erstellen(zeile, pruefung)
            badge.grid(row=0, column=4, padx=(2, 4))
            self.modul_badges.append(badge)

        self.root.after(50, self._scroll_bindings_setzen)

    def _badge_state(self, pruefung: Pruefungsleistung) -> dict:
        """Text und Farben für ein Status-Badge."""
        if pruefung.ist_bestanden:
            return {"text": "✓ bestanden",
                    "color": self._t("success"), "bg": self._t("badge_ok")}
        elif pruefung.datum != "offen" and pruefung.note is None:
            return {"text": "⏱ ausstehend",
                    "color": self._t("warning"), "bg": self._t("badge_warn")}
        else:
            return {"text": "○ offen",
                    "color": self._t("accent"),
                    "bg": self._t("badge_open")}

    def _badge_erstellen(self, parent,
                         pruefung: Pruefungsleistung) -> ctk.CTkLabel:
        state = self._badge_state(pruefung)
        badge = self._label(parent, state["text"], size=11,
                            color=state["color"], fg_color=state["bg"],
                            corner_radius=10, width=86, anchor="center")
        self._reg(badge, text_color=state["color"], fg_color=state["bg"])
        return badge

    # -----------------------------------------------------------------------
    # Offene Prüfungen
    # -----------------------------------------------------------------------

    def _open_panel_erstellen(self) -> None:
        outer = self._panel(self._scroll)
        outer.grid(row=3, column=0, sticky="ew", padx=16, pady=(12, 16))

        lbl = self._label(outer, "Offene Prüfungsleistungen", size=11,
                          color=self._t("text_dim"))
        lbl.pack(anchor="w", padx=14, pady=(14, 8))
        self._reg(lbl, text_color="text_dim")

        grid = ctk.CTkFrame(outer, fg_color=self._t("panel"))
        grid.pack(fill="x", padx=14, pady=(0, 14))
        grid.grid_columnconfigure((0, 1, 2), weight=1)
        self._reg(grid, fg_color="panel")

        self.open_items: list[dict] = []

        for col in range(3):
            for row in range(2):
                item = ctk.CTkFrame(
                    grid, fg_color=self._t("bg"),
                    border_color=self._t("border"), border_width=1,
                    corner_radius=8,
                )
                item.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                item.grid_columnconfigure(0, weight=1)
                self._reg(item, fg_color="bg", border_color="border")

                lbl_name = self._label(item, "", size=12,
                                       color=self._t("text_sec"),
                                       weight="bold")
                lbl_name.grid(row=0, column=0, sticky="w",
                              padx=10, pady=(10, 2))
                self._reg(lbl_name, text_color="text_sec")

                lbl_ects = self._label(item, "", size=11,
                                       color=self._t("text_dim"))
                lbl_ects.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 2))
                self._reg(lbl_ects, text_color="text_dim")

                lbl_status = self._label(item, "", size=11,
                                         color=self._t("accent"))
                lbl_status.grid(row=2, column=0, sticky="w",
                                padx=10, pady=(0, 10))
                self._reg(lbl_status, text_color="accent")

                self.open_items.append(
                    {"name": lbl_name, "ects": lbl_ects,
                     "status": lbl_status})

    # -----------------------------------------------------------------------
    # Datenbindung
    # -----------------------------------------------------------------------

    def anzeigen(self, studiengang: Studiengang) -> None:
        self.studiengang = studiengang
        self._modul_tabelle_fuellen()
        self._dropdowns_fuellen()
        self._einstellungen_fuellen()
        self._anzeige_aktualisieren()

    def _einstellungen_fuellen(self) -> None:
        """Bevölkert die Einstellungs-Eingabefelder."""
        # Startdatum
        self.entry_startdatum.delete(0, "end")
        if self.studiengang.start_datum is not None:
            self.entry_startdatum.insert(0,
                                         self.studiengang.start_datum.isoformat())

        # Ziel-Studienzeit
        self.entry_ziel_monate.delete(0, "end")
        self.entry_ziel_monate.insert(0,
                                      str(self.studiengang.ziel_studienzeit_monate))

        # Ziel-Notendurchschnitt
        self.entry_ziel_note.delete(0, "end")
        self.entry_ziel_note.insert(0,
                                    str(self.studiengang.ziel_notendurchschnitt))

    def _format_monat(self, datum_str: str) -> str:
        """Formatiert ein ISO-Datum (YYYY-MM-DD) als 'Mon YYYY'."""
        if not datum_str:
            return "-"
        monate = {"01": "Jan", "02": "Feb", "03": "Mär", "04": "Apr",
                  "05": "Mai", "06": "Jun", "07": "Jul", "08": "Aug",
                  "09": "Sep", "10": "Okt", "11": "Nov", "12": "Dez"}
        monat, jahr = datum_str[:7].split("-")
        return f"{monate.get(monat, monat)} {jahr}"

    def _anzeige_aktualisieren(self) -> None:
        daten = self.controller.get_dashboard_daten(self.studiengang)
        self._kpi_aktualisieren(daten)
        self._semester_aktualisieren(daten)
        self._badges_aktualisieren()
        self._open_panel_aktualisieren()

    def _kpi_aktualisieren(self, daten: dict) -> None:
        self.lbl_studiengang.configure(text=daten["studiengang_name"])
        self.lbl_ects_val.configure(
            text=f"{daten['erreichte_ects']} / {daten['gesamt_ects']}")
        pct = daten["ects_prozentsatz"]
        self.bar_ects.set(pct / 100)
        self.lbl_ects_pct.configure(text=f"{pct} % abgeschlossen")

        note = daten["durchschnittsnote"]
        self.lbl_note_val.configure(
            text=str(note) if note is not None else "-")
        # Ziel-Notendurchschnitt wird im Eingabefeld angezeigt
        if note is not None:
            if daten["ist_notenziel_erreichbar"]:
                err = daten["erreichte_ects"]
                rest = daten["verbleibende_ects"]
                ziel = daten["ziel_notendurchschnitt"]
                if rest > 0:
                    rs = (ziel * (err + rest) - note * err) / rest
                    self.lbl_note_pct.configure(
                        text=f"Rest-Schnitt {rs:.2f} erforderlich",
                        text_color=self._t("warning"))
                else:
                    ok = note <= ziel
                    self.lbl_note_pct.configure(
                        text="Ziel erreicht!" if ok else "Ziel verfehlt",
                        text_color=self._t("success") if ok
                        else self._t("warning"))
                self.bar_note.set(max(1.0 - (note - 1.0) / 4.0, 0.1))
            else:
                self.lbl_note_pct.configure(
                    text="Ziel nicht mehr erreichbar",
                    text_color=self._t("warning"))
                self.bar_note.set(0.2)
        else:
            self.lbl_note_pct.configure(
                text="Noch keine Noten", text_color=self._t("text_dim"))
            self.bar_note.set(0)

        verstr = daten["verstrichene_monate"]
        ziel_m = daten["ziel_monate"]
        verblib = max(ziel_m - verstr, 0)
        self.lbl_zeit_val.configure(text=f"{verblib:.0f} Monate")
        self.lbl_zeit_sub.configure(
            text=f"verbleibend bis {daten.get('zieldatum', '-')}")

        self.tl_canvas.update_idletasks()
        w = self.tl_canvas.winfo_width()
        if w > 1:
            self.tl_canvas.delete("all")
            ratio = min(verstr / ziel_m, 1.0) if ziel_m > 0 else 0
            done_w = int(w * ratio)
            self.tl_canvas.create_rectangle(
                0, 3, done_w, 7, fill=self._t("success"), outline="")
            self.tl_canvas.create_rectangle(
                done_w, 3, w, 7, fill=self._t("surface"), outline="")
            self.tl_canvas.create_oval(
                done_w - 5, 0, done_w + 5, 10,
                fill=self._t("accent"), outline=self._t("panel"), width=2)

        self.lbl_tl_done.configure(text=f"{verstr:.0f} Mon. absolviert")
        self.lbl_tl_offen.configure(text=f"{verblib:.0f} Mon. offen")
        self.lbl_tl_start.configure(text=daten.get("start_datum", "-"))
        self.lbl_tl_end.configure(text=daten.get("zieldatum", "-"))

    def _semester_aktualisieren(self, daten: dict) -> None:
        for i, sem in enumerate(daten["semester_fortschritt"]):
            errei  = sem["erreichte_ects"]
            gesamt = sem["gesamt_ects"]
            self.sem_ects[i].configure(text=f"{errei} / {gesamt}")
            self.sem_bars[i].set(errei / gesamt if gesamt > 0 else 0)

            if sem["ist_abgeschlossen"]:
                self.sem_bars[i].configure(
                    progress_color=self._t("success"))
                self.sem_icons[i].configure(
                    text="✓", text_color=self._t("success"))
            elif errei > 0:
                self.sem_bars[i].configure(
                    progress_color=self._t("warning"))
                self.sem_icons[i].configure(
                    text="◐", text_color=self._t("warning"))
            else:
                self.sem_bars[i].configure(
                    progress_color=self._t("surface"))
                self.sem_icons[i].configure(
                    text="○", text_color=self._t("text_dim"))

    def _badges_aktualisieren(self) -> None:
        index = 0
        for sem in self.studiengang.semester:
            for modul in sem.module:
                for pruefung in modul.pruefungsleistungen:
                    if index < len(self.modul_badges):
                        state = self._badge_state(pruefung)
                        self.modul_badges[index].configure(
                            text=state["text"],
                            text_color=state["color"],
                            fg_color=state["bg"])
                    index += 1

    def _open_panel_aktualisieren(self) -> None:
        offene = [
            (p, sem.nummer)
            for sem in self.studiengang.semester
            for modul in sem.module
            for p in modul.pruefungsleistungen
            if not p.ist_bestanden
        ]

        for i, item in enumerate(self.open_items):
            if i < len(offene):
                p, sem_nr = offene[i]
                item["name"].configure(text=p.name)
                item["ects"].configure(
                    text=f"{p.ects_punkte} ECTS · Sem {sem_nr}")
                state = self._badge_state(p)
                if p.datum != "offen" and p.note is None:
                    item["status"].configure(
                        text="⏱ Bewertung ausstehend",
                        text_color=state["color"])
                else:
                    item["status"].configure(
                        text="○ offen", text_color=state["color"])
            else:
                item["name"].configure(text="")
                item["ects"].configure(text="")
                item["status"].configure(text="")

    # -----------------------------------------------------------------------
    # Eingabe-Handler
    # -----------------------------------------------------------------------

    def _note_aktualisieren(self, index: int, event: object) -> None:
        entry = self.note_entries[index]
        text = entry.get().strip().replace(",", ".")
        pruefung = self._pruefung_by_index(index)

        if text == "":
            pruefung.note = None
            entry.delete(0, "end")
            self._anzeige_aktualisieren()
            return

        try:
            wert = float(text)
        except ValueError:
            messagebox.showerror(
                "Fehler",
                "Ungültige Eingabe. Bitte eine Zahl zwischen 1,0 und 5,0.")
            entry.delete(0, "end")
            return

        if not (1.0 <= wert <= 5.0):
            messagebox.showerror(
                "Fehler",
                "Die Note muss zwischen 1,0 und 5,0 liegen.")
            entry.delete(0, "end")
            return

        pruefung.note = wert
        entry.delete(0, "end")
        entry.insert(0, str(wert))
        self._anzeige_aktualisieren()

    def _datum_aktualisieren(self, index: int, event: object) -> None:
        entry = self.datum_entries[index]
        text = entry.get().strip()
        self._pruefung_by_index(index).datum = text or "offen"
        entry.delete(0, "end")
        entry.insert(0, text)
        self._anzeige_aktualisieren()

    # -----------------------------------------------------------------------
    # Einstellungs-Eingabefelder
    # -----------------------------------------------------------------------

    def _startdatum_aktualisieren(self, event: object) -> None:
        text = self.entry_startdatum.get().strip()
        if text == "":
            self.studiengang.start_datum = None
            self.entry_startdatum.delete(0, "end")
            self._anzeige_aktualisieren()
            return
        try:
            jahr, monat, tag = text.split("-")
            datum = date(int(jahr), int(monat), int(tag))
        except (ValueError, TypeError):
            messagebox.showerror(
                "Fehler",
                "Ungültiges Datum. Bitte im Format YYYY-MM-DD eingeben.")
            self._anzeige_aktualisieren()
            return
        self.studiengang.start_datum = datum
        self.entry_startdatum.delete(0, "end")
        self.entry_startdatum.insert(0, datum.isoformat())
        self._anzeige_aktualisieren()

    def _ziel_monate_aktualisieren(self, event: object) -> None:
        text = self.entry_ziel_monate.get().strip()
        if text == "":
            self.studiengang.ziel_studienzeit_monate = 36
            self._anzeige_aktualisieren()
            return
        try:
            wert = int(text)
        except ValueError:
            messagebox.showerror(
                "Fehler",
                "Ungültige Eingabe. Bitte eine ganze Zahl eingeben.")
            self._anzeige_aktualisieren()
            return
        if wert <= 0:
            messagebox.showerror(
                "Fehler",
                "Die Zieldauer muss größer als 0 sein.")
            self._anzeige_aktualisieren()
            return
        self.studiengang.ziel_studienzeit_monate = wert
        self.entry_ziel_monate.delete(0, "end")
        self.entry_ziel_monate.insert(0, str(wert))
        self._anzeige_aktualisieren()

    def _ziel_note_aktualisieren(self, event: object) -> None:
        text = self.entry_ziel_note.get().strip().replace(",", ".")
        if text == "":
            self.studiengang.ziel_notendurchschnitt = 2.0
            self._anzeige_aktualisieren()
            return
        try:
            wert = float(text)
        except ValueError:
            messagebox.showerror(
                "Fehler",
                "Ungültige Eingabe. Bitte eine Zahl zwischen 1,0 und 5,0.")
            self._anzeige_aktualisieren()
            return
        if not (1.0 <= wert <= 5.0):
            messagebox.showerror(
                "Fehler",
                "Der Ziel-Notendurchschnitt muss zwischen 1,0 und 5,0 liegen.")
            self._anzeige_aktualisieren()
            return
        self.studiengang.ziel_notendurchschnitt = wert
        self.entry_ziel_note.delete(0, "end")
        self.entry_ziel_note.insert(0, str(wert))
        self._anzeige_aktualisieren()

    def _pruefung_by_index(self, index: int) -> Pruefungsleistung:
        count = 0
        for sem in self.studiengang.semester:
            for modul in sem.module:
                for pruefung in modul.pruefungsleistungen:
                    if count == index:
                        return pruefung
                    count += 1
        raise IndexError(
            f"Prüfungsleistung an Index {index} nicht gefunden")

    # -----------------------------------------------------------------------
    # Wahlpflichtmodule
    # -----------------------------------------------------------------------

    def _wahlpflicht_a_geaendert(self, wert: str) -> None:
        self._wahlpflichtmodul_setzen(4, wert, "A", WAHLPFLICHT_A_B)
        self._modul_tabelle_fuellen()
        self._anzeige_aktualisieren()

    def _wahlpflicht_b_geaendert(self, wert: str) -> None:
        self._wahlpflichtmodul_setzen(5, wert, "B", WAHLPFLICHT_A_B)
        self._modul_tabelle_fuellen()
        self._anzeige_aktualisieren()

    def _wahlpflicht_c_geaendert(self, wert: str) -> None:
        self._wahlpflichtmodul_setzen(5, wert, "C", WAHLPFLICHT_C)
        self._modul_tabelle_fuellen()
        self._anzeige_aktualisieren()

    def _wahlpflichtmodul_setzen(self, sem_index: int, modulname: str,
                                  letter: str,
                                  katalog: dict[str, list[str]]) -> None:
        prefix = f"Wahlpflichtmodul {letter}"
        sem = self.studiengang.semester[sem_index]
        for modul in sem.module:
            if modul.modulart != "Wahlpflicht":
                continue
            if prefix in modul.name or modulname in modul.name:
                if modulname == "Bitte wählen...":
                    modul.name = f"{prefix} (noch nicht gewählt)"
                    for i, pruefung in enumerate(modul.pruefungsleistungen):
                        pruefung.name = f"{prefix} – Prüfung {i + 1}"
                else:
                    modul.name = f"{prefix}: {modulname}"
                    teilmodule = katalog.get(modulname, [])
                    while len(modul.pruefungsleistungen) > len(teilmodule):
                        modul.pruefungsleistungen[0].ects_punkte += \
                            modul.pruefungsleistungen.pop().ects_punkte
                    for i, pruefung in enumerate(modul.pruefungsleistungen):
                        pruefung.name = (
                            teilmodule[i] if i < len(teilmodule)
                            else f"{modulname} - Teil {i + 1}")

    def _dropdowns_fuellen(self) -> None:
        if len(self.studiengang.semester) < 6:
            return
        for sem_idx, dropdown, kennung, moegliche in [
            (4, self.dropdown_wp_a, "A", WAHLPFLICHTMODULE_A_B),
            (5, self.dropdown_wp_b, "B", WAHLPFLICHTMODULE_A_B),
            (5, self.dropdown_wp_c, "C", WAHLPFLICHTMODULE_C),
        ]:
            sem = self.studiengang.semester[sem_idx]
            gefunden = False
            for modul in sem.module:
                if (modul.modulart == "Wahlpflicht"
                        and f"Wahlpflichtmodul {kennung}" in modul.name):
                    teil = (modul.name.split(": ", 1)[-1]
                            if ": " in modul.name else modul.name)
                    if teil in moegliche:
                        dropdown.set(teil)
                        gefunden = True
                        break
            if not gefunden:
                dropdown.set("Bitte wählen...")

    # -----------------------------------------------------------------------
    # Datei-Operationen
    # -----------------------------------------------------------------------

    def _speichern(self) -> None:
        if self.studiengang is None:
            messagebox.showwarning("Warnung", "Keine Daten geladen.")
            return
        try:
            self.controller.speichere_daten(self.studiengang,
                                            self.dateipfad)
            messagebox.showinfo("Erfolg", "Daten gespeichert.")
        except Exception as fehler:
            messagebox.showerror(
                "Fehler",
                f"Das Speichern ist fehlgeschlagen: {fehler}")

    def _neu_laden(self) -> None:
        if not hasattr(self, "dateipfad"):
            messagebox.showwarning("Warnung", "Kein Dateipfad gespeichert.")
            return
        try:
            studiengang = self.controller.lade_daten(self.dateipfad)
            self.anzeigen(studiengang)
            messagebox.showinfo("Erfolg", "Daten neu geladen.")
        except Exception as fehler:
            messagebox.showerror(
                "Fehler",
                f"Das Laden ist fehlgeschlagen: {fehler}")

    def starten(self) -> None:
        self.root.mainloop()
