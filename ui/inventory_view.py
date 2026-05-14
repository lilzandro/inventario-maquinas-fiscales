import tkinter as tk
import customtkinter as ctk
import sqlite3
import os
from PIL import Image, ImageDraw, ImageFont, ImageTk
from database.db_manager import DB_PATH
from theme import AppTheme, UI_COLORS, FONT_SIZES, SIZES
from utils.logger import logger, log_error

# Fuentes 15% más grandes que la paleta global
_FS = {k: round(v * 1.15) for k, v in FONT_SIZES.items()}

_STATUS_STRIP = {
    "En Stock":         {"strip": "#1ea255", "icon": "📦"},
    "Instalada":        {"strip": "#2d83d8", "icon": "🏢"},
    "En Mantenimiento": {"strip": "#e09011", "icon": "🔧"},
    "En Reparación":    {"strip": "#7c5dd0", "icon": "🛠"},
    "Desincorporada":   {"strip": "#8a98ad", "icon": "⏻"},
}

# Paleta exacta de la Variante C
_VC_C = {
    "paper":   "#ffffff",
    "ink_900": "#14202e",
    "ink_700": "#38465c",
    "ink_500": "#6b7a92",
    "ink_300": "#b6bfcf",
    "ink_200": "#d7dde8",
    "ink_100": "#eaeef5",
    "ink_50":  "#f5f7fb",
}
_FONT_SANS = "Segoe UI"
_FONT_MONO = "Consolas"


def _confirm_dialog(title, serial, consequence, confirm_label, on_confirm, variant="danger"):
    _V = {
        "danger": {
            "icon": "🗑️",
            "icon_bg": UI_COLORS.BADGE_BG["danger"],
            "icon_fg": UI_COLORS.DANGER,
            "btn_bg": UI_COLORS.DANGER,
            "btn_hover": "#b91c1c",
        },
        "warning": {
            "icon": "⛔",
            "icon_bg": UI_COLORS.BADGE_BG["warning"],
            "icon_fg": UI_COLORS.BADGE_FG["warning"],
            "btn_bg": UI_COLORS.BADGE_FG["warning"],
            "btn_hover": "#b45309",
        },
    }
    v = _V.get(variant, _V["danger"])

    dlg = ctk.CTkToplevel()
    dlg.title("")
    dlg.resizable(False, False)
    dlg.attributes("-topmost", True)
    dlg.configure(fg_color=UI_COLORS.CARD)
    dlg.after(50, dlg.grab_set)

    w, h = 400, 280
    dlg.update_idletasks()
    sx, sy = dlg.winfo_screenwidth(), dlg.winfo_screenheight()
    dlg.geometry(f"{w}x{h}+{(sx - w) // 2}+{(sy - h) // 2}")

    hdr = ctk.CTkFrame(dlg, fg_color="#2A3550", corner_radius=0, height=52)
    hdr.pack(fill="x")
    hdr.pack_propagate(False)
    ctk.CTkLabel(
        hdr, text=title,
        font=ctk.CTkFont(size=_FS["medium"], weight="bold"),
        text_color="#ffffff",
    ).pack(side="left", padx=20)

    icon_wrap = ctk.CTkFrame(dlg, fg_color="transparent")
    icon_wrap.pack(pady=(18, 8))
    icon_box = ctk.CTkFrame(icon_wrap, width=52, height=52, fg_color=v["icon_bg"], corner_radius=26)
    icon_box.pack()
    icon_box.pack_propagate(False)
    ctk.CTkLabel(icon_box, text=v["icon"], font=ctk.CTkFont(size=22), text_color=v["icon_fg"]).place(
        relx=0.5, rely=0.5, anchor="center"
    )

    ctk.CTkLabel(
        dlg, text=serial,
        font=ctk.CTkFont(size=_FS["body"], weight="bold"),
        text_color=UI_COLORS.TEXT,
    ).pack()

    ctk.CTkLabel(
        dlg, text=consequence,
        font=ctk.CTkFont(size=_FS["small"]),
        text_color=UI_COLORS.TEXT_SECONDARY,
        wraplength=340,
    ).pack(pady=(4, 16))

    btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
    btn_row.pack(pady=(0, 4))

    def confirm():
        dlg.destroy()
        on_confirm()

    ctk.CTkButton(
        btn_row, text="Cancelar", width=130,
        fg_color=UI_COLORS.BORDER_SUBTLE, hover_color=UI_COLORS.BORDER,
        text_color=UI_COLORS.TEXT_SECONDARY,
        font=ctk.CTkFont(size=_FS["small"]),
        corner_radius=SIZES["button_radius"], height=SIZES["button_height"],
        command=dlg.destroy,
    ).pack(side="left", padx=(0, 10))

    ctk.CTkButton(
        btn_row, text=confirm_label, width=130,
        fg_color=v["btn_bg"], hover_color=v["btn_hover"],
        text_color="#ffffff",
        font=ctk.CTkFont(size=_FS["small"], weight="bold"),
        corner_radius=SIZES["button_radius"], height=SIZES["button_height"],
        command=confirm,
    ).pack(side="left")


def _stat_card(parent, col, label, value, bg, color, icon):
    card = ctk.CTkFrame(
        parent, fg_color=UI_COLORS.CARD,
        corner_radius=SIZES["card_radius"],
        border_width=1, border_color=UI_COLORS.BORDER,
    )
    card.grid(row=0, column=col, padx=(0 if col == 0 else SIZES["pad_small"], 0), sticky="ew")
    inner = ctk.CTkFrame(card, fg_color="transparent")
    inner.pack(fill="x", padx=SIZES["pad"], pady=SIZES["pad"])
    box = ctk.CTkFrame(inner, width=SIZES["icon_box"], height=SIZES["icon_box"], fg_color=bg, corner_radius=10)
    box.pack(anchor="w")
    box.pack_propagate(False)
    ctk.CTkLabel(box, text=icon, font=ctk.CTkFont(size=16), text_color=color).place(
        relx=0.5, rely=0.5, anchor="center"
    )
    ctk.CTkLabel(
        inner, text=str(value),
        font=ctk.CTkFont(size=_FS["xxlarge"], weight="bold"),
        text_color=UI_COLORS.TEXT,
    ).pack(anchor="w", pady=(6, 2))
    ctk.CTkLabel(
        inner, text=label,
        font=ctk.CTkFont(size=_FS["small"]),
        text_color=UI_COLORS.TEXT_MUTED,
    ).pack(anchor="w")


class InventoryView(ctk.CTkFrame):
    def __init__(self, master, user_info=None):
        super().__init__(master, fg_color=AppTheme.BACKGROUND)
        self.pack(fill="both", expand=True)
        self.is_admin = (user_info[3] == "admin") if user_info else True
        self.models_dict = {}
        self.distrib_dict = {}
        self.models_by_brand = {}
        self.load_reference_data()
        self.build_ui()

    def refresh(self):
        self.load_reference_data()
        self.load_machines()

    def build_ui(self):
        pad = SIZES["pad_large"]
        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.pack(fill="both", expand=True, padx=pad, pady=pad)
        self._show_normal_view()

    def _show_normal_view(self):
        for w in self._content.winfo_children():
            w.destroy()
        self._build_stat_cards(self._content)
        self._build_main_panel(self._content)

    def _show_full_table(self):
        for w in self._content.winfo_children():
            w.destroy()
        self._build_full_table_view(self._content)

    # ── Stat cards ────────────────────────────────────────────────────────────

    def _build_stat_cards(self, parent):
        stats = self._load_stats()
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, SIZES["pad"]))
        for i in range(5):
            row.grid_columnconfigure(i, weight=1)

        data = [
            ("Total Máquinas",    stats["total"],          "#EFF6FF", "#2563EB", "📦"),
            ("En Stock",          stats["en_stock"],        "#F0FDF4", "#16A34A", "✅"),
            ("Instaladas",        stats["instalada"],       "#EFF6FF", "#2563EB", "🔧"),
            ("En Servicio",       stats["en_servicio"],     "#FFFBEB", "#D97706", "🛠️"),
            ("Desincorporadas",   stats["desincorporada"],  "#FEF2F2", "#DC2626", "⛔"),
        ]
        for i, args in enumerate(data):
            _stat_card(row, i, *args)

    # ── Main panel ────────────────────────────────────────────────────────────

    def _build_main_panel(self, parent):
        main = ctk.CTkFrame(parent, fg_color="transparent")
        main.pack(fill="both", expand=True)
        main.grid_rowconfigure(0, weight=1)

        if self.is_admin:
            main.grid_columnconfigure(0, weight=1)
            main.grid_columnconfigure(1, weight=2)
            self._build_form(main)
            self._build_list(main)
        else:
            main.grid_columnconfigure(0, weight=1)
            self._build_list_only(main)

    # ── Form ──────────────────────────────────────────────────────────────────

    def _build_form(self, parent):
        card = ctk.CTkFrame(
            parent, fg_color=UI_COLORS.CARD,
            corner_radius=SIZES["card_radius"],
            border_width=1, border_color=UI_COLORS.BORDER,
        )
        card.grid(row=0, column=0, sticky="nsew", padx=(0, SIZES["pad"]))
        card.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            card, text="Registrar Máquinas Fiscales",
            font=ctk.CTkFont(size=_FS["large"], weight="bold"),
            text_color=UI_COLORS.TEXT,
        ).pack(anchor="w", padx=SIZES["pad_large"], pady=(SIZES["pad_large"], SIZES["pad_small"]))

        ctk.CTkFrame(card, height=1, fg_color=UI_COLORS.BORDER_SUBTLE).pack(
            fill="x", padx=SIZES["pad_large"], pady=(0, SIZES["pad_small"])
        )

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=SIZES["pad_large"], pady=(0, SIZES["pad_small"]))

        self._lbl(top, "Proveedor")
        proveedores = list(self.distrib_dict.keys())
        self.distrib_combo = self._combo(top, proveedores if proveedores else ["Sin proveedores"])
        self.distrib_combo.pack(fill="x", pady=(0, SIZES["pad_small"]))
        self.distrib_combo.configure(command=self._on_proveedor_change)

        self._lbl(top, "Modelo de Máquina Fiscal")
        self.model_combo = ctk.CTkComboBox(
            top, values=[""],
            height=SIZES["entry_height"],
            corner_radius=SIZES["button_radius"],
            state="normal",
            fg_color="#F8FAFC", text_color=UI_COLORS.TEXT,
            button_color=UI_COLORS.BORDER, button_hover_color=UI_COLORS.PRIMARY,
            dropdown_fg_color=UI_COLORS.CARD, dropdown_text_color=UI_COLORS.TEXT,
            border_color=UI_COLORS.BORDER,
        )
        self.model_combo.set("")
        self.model_combo.pack(fill="x", pady=(0, 0))
        self.model_combo.bind("<KeyRelease>", lambda e: self.model_combo.configure(border_color=UI_COLORS.BORDER))

        ctk.CTkFrame(card, height=1, fg_color=UI_COLORS.BORDER_SUBTLE).pack(
            fill="x", padx=SIZES["pad_large"], pady=SIZES["pad_small"]
        )

        units_hdr = ctk.CTkFrame(card, fg_color="transparent")
        units_hdr.pack(fill="x", padx=SIZES["pad_large"], pady=(0, SIZES["pad_small"]))

        ctk.CTkLabel(
            units_hdr, text="Unidades a Ingresar",
            font=ctk.CTkFont(size=_FS["small"], weight="bold"),
            text_color=UI_COLORS.TEXT_SECONDARY,
        ).pack(side="left")

        ctk.CTkButton(
            units_hdr, text="＋  Agregar unidad",
            command=self._add_unit_row,
            height=30, corner_radius=SIZES["button_radius"],
            fg_color=UI_COLORS.PRIMARY, hover_color=UI_COLORS.SECONDARY,
            text_color="#ffffff",
            font=ctk.CTkFont(size=_FS["small"], weight="bold"),
        ).pack(side="right")

        self._units_frame = ctk.CTkScrollableFrame(
            card, fg_color="transparent", scrollbar_button_color=UI_COLORS.BORDER
        )
        self._units_frame.pack(
            fill="both", expand=True,
            padx=SIZES["pad_large"], pady=(0, SIZES["pad_small"]),
        )
        self._units_frame.grid_columnconfigure(0, weight=1)

        self._unit_rows = []
        self._add_unit_row()

        ctk.CTkFrame(card, height=1, fg_color=UI_COLORS.BORDER_SUBTLE).pack(
            fill="x", padx=SIZES["pad_large"], pady=(0, SIZES["pad_small"])
        )

        ctk.CTkButton(
            card, text="✓  Registrar en Inventario",
            command=self.add_machine,
            fg_color=UI_COLORS.PRIMARY, hover_color=UI_COLORS.SECONDARY,
            text_color="#ffffff",
            font=ctk.CTkFont(size=_FS["body"], weight="bold"),
            corner_radius=SIZES["button_radius"], height=SIZES["button_height"],
        ).pack(fill="x", padx=SIZES["pad_large"], pady=(0, SIZES["pad_small"]))

        self.message = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=_FS["tiny"]))
        self.message.pack(padx=SIZES["pad_large"], pady=(0, SIZES["pad"]))

        if proveedores:
            self._on_proveedor_change(proveedores[0])

    def _on_proveedor_change(self, proveedor):
        modelos = list(self.models_by_brand.get(proveedor, {}).keys())
        self.model_combo.configure(values=modelos if modelos else [""])
        self.model_combo.set("")

    def _add_unit_row(self):
        idx = len(self._unit_rows)

        row = ctk.CTkFrame(
            self._units_frame,
            fg_color=UI_COLORS.BORDER_SUBTLE,
            corner_radius=SIZES["button_radius"],
            border_width=1, border_color=UI_COLORS.BORDER,
        )
        row.grid(row=idx, column=0, sticky="ew", pady=(0, SIZES["pad_small"]))
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)

        top_row = ctk.CTkFrame(row, fg_color="transparent")
        top_row.grid(
            row=0, column=0, columnspan=2, sticky="ew",
            padx=SIZES["pad_small"], pady=(SIZES["pad_small"], 2),
        )

        num_lbl = ctk.CTkLabel(
            top_row, text=f"  Unidad #{idx + 1}",
            font=ctk.CTkFont(size=_FS["tiny"], weight="bold"),
            text_color=UI_COLORS.PRIMARY,
        )
        num_lbl.pack(side="left")

        def remove(r=row):
            if len(self._unit_rows) <= 1:
                return
            self._unit_rows = [
                (s, re, fr, nl) for s, re, fr, nl in self._unit_rows if fr is not r
            ]
            r.destroy()
            for i, (_, _, _, nl) in enumerate(self._unit_rows):
                nl.configure(text=f"  Unidad #{i + 1}")

        ctk.CTkButton(
            top_row, text="✕", width=26, height=26, corner_radius=6,
            fg_color=UI_COLORS.CARD, hover_color=UI_COLORS.BADGE_BG["danger"],
            text_color=UI_COLORS.DANGER,
            border_width=1, border_color=UI_COLORS.BORDER,
            font=ctk.CTkFont(size=_FS["tiny"]),
            command=remove,
        ).pack(side="right")

        s_entry = self._entry(row, "Número de Serial")
        s_entry.bind("<KeyRelease>", lambda e: s_entry.configure(border_color=UI_COLORS.BORDER))
        s_entry.grid(
            row=1, column=0, sticky="ew",
            padx=(SIZES["pad_small"], 4), pady=(0, SIZES["pad_small"]),
        )

        r_entry = self._entry(row, "Nro. Registro SENIAT")
        r_entry.bind("<KeyRelease>", lambda e: r_entry.configure(border_color=UI_COLORS.BORDER))
        r_entry.grid(
            row=1, column=1, sticky="ew",
            padx=(4, SIZES["pad_small"]), pady=(0, SIZES["pad_small"]),
        )

        self._unit_rows.append((s_entry, r_entry, row, num_lbl))

    def _build_list_only(self, parent):
        self._build_list(parent, col=0)

    # ── List ──────────────────────────────────────────────────────────────────

    def _build_list(self, parent, col=1):
        card = ctk.CTkFrame(
            parent, fg_color=UI_COLORS.CARD,
            corner_radius=SIZES["card_radius"],
            border_width=1, border_color=UI_COLORS.BORDER,
        )
        card.grid(row=0, column=col, sticky="nsew", padx=(SIZES["pad"] if col == 1 else 0, 0))

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=SIZES["pad_large"], pady=(SIZES["pad_large"], SIZES["pad_small"]))

        ctk.CTkLabel(
            hdr, text="Inventario",
            font=ctk.CTkFont(size=_FS["large"], weight="bold"),
            text_color=UI_COLORS.TEXT,
        ).pack(side="left")

        self.count_label = ctk.CTkLabel(
            hdr, text="",
            font=ctk.CTkFont(size=_FS["small"]),
            text_color=UI_COLORS.TEXT_MUTED,
        )
        self.count_label.pack(side="left", padx=(SIZES["pad_small"], 0))

        ctk.CTkButton(
            hdr, text="☰  Ver Inventario Completo",
            command=self._show_full_table,
            height=30, corner_radius=SIZES["button_radius"],
            fg_color=UI_COLORS.BORDER_SUBTLE, hover_color=UI_COLORS.BORDER,
            text_color=UI_COLORS.TEXT_SECONDARY,
            font=ctk.CTkFont(size=_FS["small"]),
        ).pack(side="right")

        search_row = ctk.CTkFrame(card, fg_color="transparent")
        search_row.pack(fill="x", padx=SIZES["pad_large"], pady=(0, SIZES["pad_small"]))

        search_wrap = ctk.CTkFrame(
            search_row, fg_color="#F8FAFC",
            corner_radius=SIZES["button_radius"],
            border_width=1, border_color=UI_COLORS.BORDER,
        )
        search_wrap.pack(fill="x")

        ctk.CTkLabel(
            search_wrap, text="🔍",
            font=ctk.CTkFont(size=13), text_color=UI_COLORS.TEXT_MUTED,
        ).pack(side="left", padx=(10, 0))

        pill = ctk.CTkFrame(search_wrap, fg_color=UI_COLORS.BADGE_BG["default"], corner_radius=SIZES["badge_radius"])
        pill.pack(side="left", padx=(4, 0))
        ctk.CTkLabel(
            pill, text="Serial:",
            font=ctk.CTkFont(size=_FS["tiny"], weight="bold"),
            text_color=UI_COLORS.BADGE_FG["default"],
        ).pack(padx=7, pady=2)

        self.search_var = ctk.StringVar()

        def _on_search_change(*_):
            if self.search_var.get() == "":
                self.load_machines()

        self.search_var.trace("w", _on_search_change)

        search_entry = ctk.CTkEntry(
            search_wrap, textvariable=self.search_var,
            placeholder_text="Buscar por serial...  [Enter]",
            fg_color="transparent", border_width=0,
            text_color=UI_COLORS.TEXT,
            placeholder_text_color=UI_COLORS.TEXT_MUTED,
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=4, pady=6)
        search_entry.bind("<Return>", lambda _: self.load_machines())

        filters_row = ctk.CTkFrame(card, fg_color="transparent")
        filters_row.pack(fill="x", padx=SIZES["pad_large"], pady=(0, SIZES["pad_small"]))

        ctk.CTkLabel(
            filters_row, text="Proveedor:",
            font=ctk.CTkFont(size=_FS["small"]),
            text_color=UI_COLORS.TEXT_SECONDARY,
        ).pack(side="left", padx=(0, 4))

        proveedores = ["TODOS"] + list(self.distrib_dict.keys())
        self.prov_filter_var = ctk.StringVar(value="TODOS")
        self.prov_filter_var.trace("w", lambda *e: self.load_machines())
        ctk.CTkComboBox(
            filters_row, values=proveedores,
            variable=self.prov_filter_var,
            width=170, corner_radius=SIZES["button_radius"], state="readonly",
            fg_color="#F8FAFC", text_color=UI_COLORS.TEXT,
            button_color=UI_COLORS.BORDER, button_hover_color=UI_COLORS.PRIMARY,
            dropdown_fg_color=UI_COLORS.CARD, dropdown_text_color=UI_COLORS.TEXT,
            border_color=UI_COLORS.BORDER,
        ).pack(side="left")

        ctk.CTkLabel(
            filters_row, text="Estado:",
            font=ctk.CTkFont(size=_FS["small"]),
            text_color=UI_COLORS.TEXT_SECONDARY,
        ).pack(side="left", padx=(SIZES["pad"], 4))

        self.filter_var = ctk.StringVar(value="TODOS")
        self.filter_var.trace("w", lambda *e: self.load_machines())
        ctk.CTkComboBox(
            filters_row,
            values=["TODOS", "En Stock", "Instalada", "En Mantenimiento", "En Reparación", "Desincorporada"],
            variable=self.filter_var,
            width=160, corner_radius=SIZES["button_radius"], state="readonly",
            fg_color="#F8FAFC", text_color=UI_COLORS.TEXT,
            button_color=UI_COLORS.BORDER, button_hover_color=UI_COLORS.PRIMARY,
            dropdown_fg_color=UI_COLORS.CARD, dropdown_text_color=UI_COLORS.TEXT,
            border_color=UI_COLORS.BORDER,
        ).pack(side="left")

        ctk.CTkFrame(card, height=1, fg_color=UI_COLORS.BORDER_SUBTLE).pack(
            fill="x", padx=SIZES["pad_large"], pady=(0, SIZES["pad_small"])
        )

        self.scroll_frame = ctk.CTkScrollableFrame(
            card, fg_color="transparent", scrollbar_button_color=UI_COLORS.BORDER
        )
        self.scroll_frame.pack(
            fill="both", expand=True,
            padx=SIZES["pad_large"], pady=(0, SIZES["pad_large"]),
        )
        self.load_machines()

    # ── Data ops ──────────────────────────────────────────────────────────────

    def load_reference_data(self):
        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)
        self.models_by_brand = {}
        for mid, brand, model_name in conn.execute(
            "SELECT id, brand, model_name FROM machine_models ORDER BY brand, model_name"
        ):
            self.models_by_brand.setdefault(brand, {})[model_name] = mid
            self.models_dict[f"{brand} - {model_name}"] = mid
        for r in conn.execute("SELECT id, name FROM distributors ORDER BY name"):
            self.distrib_dict[r[1]] = r[0]
        conn.close()

    @staticmethod
    def _load_stats():
        s = {"total": 0, "en_stock": 0, "instalada": 0, "en_servicio": 0, "desincorporada": 0}
        if not os.path.exists(DB_PATH):
            return s
        try:
            conn = sqlite3.connect(DB_PATH)
            s["total"]          = conn.execute("SELECT COUNT(*) FROM machines").fetchone()[0]
            s["en_stock"]       = conn.execute("SELECT COUNT(*) FROM machines WHERE status='En Stock'").fetchone()[0]
            s["instalada"]      = conn.execute("SELECT COUNT(*) FROM machines WHERE status='Instalada'").fetchone()[0]
            s["en_servicio"]    = conn.execute(
                "SELECT COUNT(*) FROM machines WHERE status IN ('En Mantenimiento','En Reparación')"
            ).fetchone()[0]
            s["desincorporada"] = conn.execute("SELECT COUNT(*) FROM machines WHERE status='Desincorporada'").fetchone()[0]
            conn.close()
        except Exception as e:
            log_error("inventory_view", "_load_stats", e)
        return s

    def add_machine(self):
        self.model_combo.configure(border_color=UI_COLORS.BORDER)
        for s_entry, r_entry, fr, *_ in self._unit_rows:
            s_entry.configure(border_color=UI_COLORS.BORDER)
            r_entry.configure(border_color=UI_COLORS.BORDER)
        self.message.configure(text="")

        proveedor = self.distrib_combo.get()
        modelo    = self.model_combo.get().strip()

        if not modelo:
            self.model_combo.configure(border_color=UI_COLORS.DANGER)
            self.message.configure(text="⚠  Ingrese el modelo", text_color=UI_COLORS.DANGER)
            return

        unidades = []
        filas_incompletas = False
        for s_entry, r_entry, *_ in self._unit_rows:
            serial   = s_entry.get().strip()
            registro = r_entry.get().strip()
            if not serial and not registro:
                continue
            if not serial:
                s_entry.configure(border_color=UI_COLORS.DANGER)
                filas_incompletas = True
            if not registro:
                r_entry.configure(border_color=UI_COLORS.DANGER)
                filas_incompletas = True
            if serial and registro:
                unidades.append(f"{serial} | Reg.SENIAT:{registro}")

        if filas_incompletas:
            self.message.configure(
                text="⚠  Serial y Reg. SENIAT son obligatorios en cada unidad",
                text_color=UI_COLORS.DANGER,
            )
            return

        if not unidades:
            for s_entry, r_entry, *_ in self._unit_rows:
                s_entry.configure(border_color=UI_COLORS.DANGER)
                r_entry.configure(border_color=UI_COLORS.DANGER)
            self.message.configure(text="⚠  Ingrese al menos una unidad", text_color=UI_COLORS.DANGER)
            return

        distrib_id = self.distrib_dict.get(proveedor)

        try:
            conn = sqlite3.connect(DB_PATH)
            existing = conn.execute(
                "SELECT id FROM machine_models WHERE brand=? AND model_name=?",
                (proveedor, modelo),
            ).fetchone()
            if existing:
                model_id = existing[0]
            else:
                cur = conn.execute(
                    "INSERT INTO machine_models (brand, model_name) VALUES (?,?)",
                    (proveedor, modelo),
                )
                model_id = cur.lastrowid
                self.models_by_brand.setdefault(proveedor, {})[modelo] = model_id
                self.models_dict[f"{proveedor} - {modelo}"] = model_id

            duplicados = []
            registradas = 0
            for serial_full in unidades:
                try:
                    conn.execute(
                        "INSERT INTO machines (serial_number, model_id, distributor_id, status) "
                        "VALUES (?, ?, ?, 'En Stock')",
                        (serial_full, model_id, distrib_id),
                    )
                    registradas += 1
                except sqlite3.IntegrityError:
                    duplicados.append(serial_full.split(" |")[0])

            conn.commit()
            conn.close()

            for _, _, fr, *_ in self._unit_rows:
                fr.destroy()
            self._unit_rows.clear()
            self._add_unit_row()

            if duplicados:
                self.message.configure(
                    text=f"✓ {registradas} registradas · ⚠ {len(duplicados)} serial(es) duplicado(s)",
                    text_color="#D97706" if registradas else UI_COLORS.DANGER,
                )
            else:
                self.message.configure(
                    text=f"✓  {registradas} máquina(s) registrada(s) en inventario",
                    text_color=UI_COLORS.GREEN,
                )
            logger.info(f"Ingreso inventario: {registradas} máquinas - {proveedor} {modelo}")
            self.load_machines()
        except Exception as e:
            log_error("inventory_view", "add_machine", e)
            self.message.configure(text="⚠  Error interno", text_color=UI_COLORS.DANGER)

    def load_machines(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        if not os.path.exists(DB_PATH):
            return

        conn = sqlite3.connect(DB_PATH)
        where_parts, params = [], []

        busq = self.search_var.get().strip().lower()
        if busq:
            where_parts.append("LOWER(m.serial_number) LIKE ?")
            params.append(f"%{busq}%")

        prov = self.prov_filter_var.get()
        if prov != "TODOS":
            where_parts.append("d.name = ?")
            params.append(prov)

        estado = self.filter_var.get()
        if estado != "TODOS":
            where_parts.append("m.status = ?")
            params.append(estado)

        _LIMIT = 10
        wc = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""
        base_q = f"""
            FROM machines m
            LEFT JOIN machine_models mo ON m.model_id = mo.id
            LEFT JOIN distributors d ON m.distributor_id = d.id
            LEFT JOIN clients c ON m.client_id = c.id
            {wc}
        """
        total = conn.execute(f"SELECT COUNT(*) {base_q}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT m.id, m.serial_number, mo.model_name, d.name, m.status, c.name, c.document_id "
            f"{base_q} ORDER BY m.id DESC LIMIT {_LIMIT}",
            params,
        ).fetchall()
        conn.close()

        shown = len(rows)
        if total > _LIMIT:
            self.count_label.configure(text=f"Mostrando {shown} de {total} máquinas")
        else:
            self.count_label.configure(text=f"{total} máquina{'s' if total != 1 else ''}")

        if not rows:
            ctk.CTkLabel(
                self.scroll_frame,
                text="No hay máquinas con ese criterio",
                font=ctk.CTkFont(size=_FS["body"]),
                text_color=UI_COLORS.TEXT_MUTED,
            ).pack(pady=30)
            return
        for r in rows:
            self._machine_card(r)

    def _machine_card(self, row):
        mid, serial_raw, modelo, distribuidor, estado, client_name, client_doc = row

        if " | Reg.SENIAT:" in (serial_raw or ""):
            serial_num, reg_seniat = serial_raw.split(" | Reg.SENIAT:", 1)
        else:
            serial_num = serial_raw or "—"
            reg_seniat = "—"

        s = _STATUS_STRIP.get(estado, {"strip": "#8a98ad", "icon": "?"})
        CARD_H = 220
        BAND_W = 58
        r = 10

        # ── Tarjeta base (altura fija)
        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=_VC_C["paper"],
            corner_radius=10,
            border_width=1,
            border_color=_VC_C["ink_200"],
            height=CARD_H,
        )
        card.pack(fill="x", pady=4)
        card.grid_propagate(False)
        card.grid_columnconfigure(1, weight=1)
        card.grid_rowconfigure(0, weight=1)

        # ── Banda lateral izquierda — bordes redondeados solo lado izquierdo
        band = tk.Canvas(card, width=BAND_W, highlightthickness=0, bg=_VC_C["paper"])
        band.grid(row=0, column=0, sticky="nsew")

        c = s["strip"]
        band.create_rectangle(r, 0, BAND_W, CARD_H, fill=c, outline="", width=0)
        band.create_rectangle(0, r, r, CARD_H - r, fill=c, outline="", width=0)
        band.create_arc(0, 0, 2 * r, 2 * r, start=90, extent=90, fill=c, outline="", width=0)
        band.create_arc(0, CARD_H - 2 * r, 2 * r, CARD_H, start=180, extent=90, fill=c, outline="", width=0)

        # Icono de estado
        band.create_text(29, 22, text=s["icon"], fill="white", font=("", 16), anchor="center")

        # Texto rotado 90° con Pillow
        label_str = estado.upper()
        try:
            _pil_font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10
            )
        except (IOError, OSError):
            _pil_font = ImageFont.load_default()
        bbox = _pil_font.getbbox(label_str)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        img = Image.new("RGBA", (tw + 8, th + 8), c)
        ImageDraw.Draw(img).text((4, 4), label_str, fill="white", font=_pil_font)
        rotated = img.rotate(90, expand=True)
        photo = ImageTk.PhotoImage(rotated)
        band.create_image(29, 115, image=photo, anchor="center")
        band.image = photo  # mantener referencia — evita GC

        # ── Contenido derecho
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.grid(row=0, column=1, sticky="nsew", padx=18, pady=14)
        content.grid_columnconfigure(0, weight=1)

        # ── Fila superior: título + acciones
        top = ctk.CTkFrame(content, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        title_block = ctk.CTkFrame(top, fg_color="transparent")
        title_block.grid(row=0, column=0, sticky="w")

        # Brand · Model (18 px)
        title_row = ctk.CTkFrame(title_block, fg_color="transparent")
        title_row.pack(anchor="w")
        ctk.CTkLabel(
            title_row, text=distribuidor or "—",
            font=(_FONT_SANS, 18, "bold"), text_color=_VC_C["ink_900"],
        ).pack(side="left")
        ctk.CTkLabel(
            title_row, text="·",
            font=(_FONT_SANS, 18), text_color=_VC_C["ink_300"],
        ).pack(side="left", padx=8)
        ctk.CTkLabel(
            title_row, text=modelo or "—",
            font=(_FONT_SANS, 18), text_color=_VC_C["ink_700"],
        ).pack(side="left")

        # Empresa · RIF (15 px) — cliente asignado si existe
        _needs_client = estado in ("Instalada", "En Mantenimiento", "En Reparación")
        if client_name:
            subtitle = f"{client_name}   ·   RIF {client_doc}" if client_doc else client_name
            subtitle_color = _VC_C["ink_500"]
        elif _needs_client:
            subtitle = "Sin cliente asignado"
            subtitle_color = _VC_C["ink_300"]
        else:
            subtitle = None

        if subtitle:
            ctk.CTkLabel(
                title_block, text=subtitle,
                font=(_FONT_SANS, 15), text_color=subtitle_color,
            ).pack(anchor="w", pady=(2, 0))

        # Acciones — TextButton para edit/decomm/completar, IconButton para delete
        actions = ctk.CTkFrame(top, fg_color="transparent")
        actions.grid(row=0, column=1, sticky="e")

        _btn_kw = dict(
            height=32, corner_radius=7,
            fg_color=_VC_C["paper"], text_color=_VC_C["ink_700"],
            border_width=1, border_color=_VC_C["ink_200"],
            font=(_FONT_SANS, 15),
        )

        if self.is_admin and estado in ("En Mantenimiento", "En Reparación"):
            ctk.CTkButton(
                actions, text="✓  Completar",
                hover_color="#bbf7d0",
                command=lambda m=mid: self.completar_servicio(m),
                **_btn_kw,
            ).pack(side="left", padx=3)

        if self.is_admin:
            ctk.CTkButton(
                actions, text="✎  Editar",
                hover_color="#e0eefb",
                command=lambda m=mid: self._open_edit_machine_dlg(m, on_save=None),
                **_btn_kw,
            ).pack(side="left", padx=3)

        if self.is_admin and estado != "Desincorporada":
            ctk.CTkButton(
                actions, text="⊘  Desincorporar",
                hover_color="#fcecd0",
                command=lambda m=mid, s=serial_num: _confirm_dialog(
                    "Desincorporar máquina", s,
                    "La máquina pasará al estado 'Desincorporada' y\nno aparecerá disponible para nuevos servicios.",
                    "Desincorporar", lambda: self.desincorporar_maquina(m), variant="warning",
                ),
                **_btn_kw,
            ).pack(side="left", padx=3)

        if self.is_admin:
            ctk.CTkButton(
                actions, text="🗑",
                width=34, height=34, corner_radius=7,
                fg_color=_VC_C["paper"], text_color=_VC_C["ink_500"],
                hover_color="#fbdcdb", border_width=1, border_color=_VC_C["ink_200"],
                font=(_FONT_SANS, 14),
                command=lambda m=mid, s=serial_num: _confirm_dialog(
                    "Eliminar máquina", s,
                    "Se eliminará permanentemente del inventario.\nEsta acción no se puede deshacer.",
                    "Eliminar", lambda: self.eliminar_maquina(m), variant="danger",
                ),
            ).pack(side="left", padx=3)

        # ── Divisor
        ctk.CTkFrame(content, fg_color=_VC_C["ink_100"], height=1).grid(
            row=1, column=0, sticky="ew", pady=(10, 12)
        )

        # ── Meta: N° Serial + Reg. SENIAT
        meta = ctk.CTkFrame(content, fg_color="transparent")
        meta.grid(row=2, column=0, sticky="ew")
        meta.grid_columnconfigure(0, weight=1, minsize=120)
        meta.grid_columnconfigure(1, weight=1)

        def _mk_meta(parent, col, label, value):
            f = ctk.CTkFrame(parent, fg_color=_VC_C["ink_50"], corner_radius=8)
            f.grid(row=0, column=col, sticky="ew", padx=(0, 10) if col == 0 else 0)
            ctk.CTkLabel(f, text=label,
                font=(_FONT_SANS, 15, "bold"), text_color=_VC_C["ink_500"],
            ).pack(anchor="w", padx=12, pady=(8, 0))
            ctk.CTkLabel(f, text=value,
                font=(_FONT_MONO, 17, "bold"), text_color=_VC_C["ink_900"],
            ).pack(anchor="w", padx=12, pady=(0, 8))

        _mk_meta(meta, 0, "N° Serial", serial_num)
        _mk_meta(meta, 1, "Reg. SENIAT", reg_seniat)

    def _build_full_table_view(self, parent):
        _COLS = [
            ("#", 36, "center"),
            ("N° Serial", 190, "w"),
            ("Reg. SENIAT", 150, "w"),
            ("Modelo", 170, "w"),
            ("Proveedor", 155, "w"),
            ("Estado", 140, "center"),
            ("Acciones", 105, "center"),
        ]

        topbar = ctk.CTkFrame(
            parent, fg_color=UI_COLORS.CARD,
            corner_radius=SIZES["card_radius"],
            border_width=1, border_color=UI_COLORS.BORDER,
        )
        topbar.pack(fill="x", pady=(0, SIZES["pad_small"]))

        inner = ctk.CTkFrame(topbar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=SIZES["pad"], pady=SIZES["pad_small"])

        ctk.CTkButton(
            inner, text="← Volver",
            command=self._show_normal_view,
            height=30, corner_radius=SIZES["button_radius"],
            fg_color=UI_COLORS.BORDER_SUBTLE, hover_color=UI_COLORS.BORDER,
            text_color=UI_COLORS.TEXT_SECONDARY,
            font=ctk.CTkFont(size=_FS["small"]),
        ).pack(side="left", padx=(0, SIZES["pad"]))

        ctk.CTkLabel(
            inner, text="📦  Inventario Completo",
            font=ctk.CTkFont(size=_FS["large"], weight="bold"),
            text_color=UI_COLORS.TEXT,
        ).pack(side="left")

        count_lbl = ctk.CTkLabel(
            inner, text="",
            font=ctk.CTkFont(size=_FS["small"]),
            text_color=UI_COLORS.TEXT_MUTED,
        )
        count_lbl.pack(side="left", padx=(SIZES["pad_small"], 0))

        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, SIZES["pad_small"]))

        search_var = ctk.StringVar()
        sw = ctk.CTkFrame(
            toolbar, fg_color="#F8FAFC",
            corner_radius=SIZES["button_radius"],
            border_width=1, border_color=UI_COLORS.BORDER,
        )
        sw.pack(side="left", fill="x", expand=True, padx=(0, SIZES["pad_small"]))
        ctk.CTkLabel(sw, text="🔍", font=ctk.CTkFont(size=13), text_color=UI_COLORS.TEXT_MUTED).pack(
            side="left", padx=(8, 0)
        )
        pill = ctk.CTkFrame(sw, fg_color=UI_COLORS.BADGE_BG["default"], corner_radius=SIZES["badge_radius"])
        pill.pack(side="left", padx=(4, 0))
        ctk.CTkLabel(
            pill, text="Serial",
            font=ctk.CTkFont(size=_FS["tiny"], weight="bold"),
            text_color=UI_COLORS.BADGE_FG["default"],
        ).pack(padx=7, pady=2)
        search_e = ctk.CTkEntry(
            sw, textvariable=search_var,
            placeholder_text="Buscar serial...  [Enter]",
            fg_color="transparent", border_width=0,
            text_color=UI_COLORS.TEXT, placeholder_text_color=UI_COLORS.TEXT_MUTED,
        )
        search_e.pack(side="left", fill="x", expand=True, padx=4, pady=6)

        estado_var = ctk.StringVar(value="TODOS")
        ctk.CTkComboBox(
            toolbar,
            values=["TODOS", "En Stock", "Instalada", "En Mantenimiento", "En Reparación", "Desincorporada"],
            variable=estado_var,
            width=170, corner_radius=SIZES["button_radius"], state="readonly",
            fg_color="#F8FAFC", text_color=UI_COLORS.TEXT,
            button_color=UI_COLORS.BORDER, button_hover_color=UI_COLORS.PRIMARY,
            dropdown_fg_color=UI_COLORS.CARD, dropdown_text_color=UI_COLORS.TEXT,
            border_color=UI_COLORS.BORDER,
        ).pack(side="left")

        table_card = ctk.CTkFrame(
            parent, fg_color=UI_COLORS.CARD,
            corner_radius=SIZES["card_radius"],
            border_width=1, border_color=UI_COLORS.BORDER,
        )
        table_card.pack(fill="both", expand=True)

        col_hdr = ctk.CTkFrame(table_card, fg_color="#2A3550", corner_radius=0, height=38)
        col_hdr.pack(fill="x")
        col_hdr.pack_propagate(False)
        for lbl, width, anchor in _COLS:
            side = "right" if lbl == "Acciones" else "left"
            px = (0, 10) if lbl == "Acciones" else (10, 0)
            ctk.CTkLabel(
                col_hdr, text=lbl, width=width, anchor=anchor,
                font=ctk.CTkFont(size=_FS["small"], weight="bold"),
                text_color="#ffffff",
            ).pack(side=side, padx=px)
        ctk.CTkFrame(table_card, height=1, fg_color=UI_COLORS.BORDER_SUBTLE).pack(fill="x")

        rows_sf = ctk.CTkScrollableFrame(
            table_card, fg_color="transparent", scrollbar_button_color=UI_COLORS.BORDER
        )
        rows_sf.pack(fill="both", expand=True)

        def load_table():
            for w in rows_sf.winfo_children():
                w.destroy()
            conn = sqlite3.connect(DB_PATH)
            where_parts, params = [], []
            busq = search_var.get().strip().lower()
            if busq:
                where_parts.append("LOWER(m.serial_number) LIKE ?")
                params.append(f"%{busq}%")
            est = estado_var.get()
            if est != "TODOS":
                where_parts.append("m.status = ?")
                params.append(est)
            wc = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""
            db_rows = conn.execute(
                f"""
                SELECT m.id, m.serial_number, mo.model_name, d.name, m.status
                FROM machines m
                LEFT JOIN machine_models mo ON m.model_id = mo.id
                LEFT JOIN distributors d    ON m.distributor_id = d.id
                {wc} ORDER BY m.id DESC
                """,
                params,
            ).fetchall()
            conn.close()

            n = len(db_rows)
            count_lbl.configure(text=f"{n} máquina{'s' if n != 1 else ''}")

            _ROW_BG = [UI_COLORS.CARD, "#F8FAFC"]
            for i, (mid, serial_raw, modelo, distribuidor, estado) in enumerate(db_rows):
                if " | Reg.SENIAT:" in (serial_raw or ""):
                    serial_num, reg_seniat = serial_raw.split(" | Reg.SENIAT:", 1)
                else:
                    serial_num, reg_seniat = serial_raw or "—", "—"
                sfg = UI_COLORS.STATUS_COLORS.get(estado, UI_COLORS.TEXT_MUTED)
                sbg = UI_COLORS.STATUS_BADGE_BG.get(estado, "#F8FAFC")

                row_fr = ctk.CTkFrame(rows_sf, fg_color=_ROW_BG[i % 2], corner_radius=0, height=40)
                row_fr.pack(fill="x")
                row_fr.pack_propagate(False)

                ctk.CTkLabel(row_fr, text=str(i + 1), width=36, anchor="center",
                    font=ctk.CTkFont(size=_FS["tiny"]), text_color=UI_COLORS.TEXT_MUTED,
                ).pack(side="left", padx=(10, 0))
                ctk.CTkLabel(row_fr, text=serial_num, width=190, anchor="w",
                    font=ctk.CTkFont(size=_FS["small"], weight="bold"), text_color=UI_COLORS.TEXT,
                ).pack(side="left", padx=(10, 0))
                ctk.CTkLabel(row_fr, text=reg_seniat, width=150, anchor="w",
                    font=ctk.CTkFont(size=_FS["small"]), text_color=UI_COLORS.TEXT_SECONDARY,
                ).pack(side="left", padx=(10, 0))
                ctk.CTkLabel(row_fr, text=modelo or "—", width=170, anchor="w",
                    font=ctk.CTkFont(size=_FS["small"]), text_color=UI_COLORS.TEXT_SECONDARY,
                ).pack(side="left", padx=(10, 0))
                ctk.CTkLabel(row_fr, text=distribuidor or "—", width=155, anchor="w",
                    font=ctk.CTkFont(size=_FS["small"]), text_color=UI_COLORS.TEXT_SECONDARY,
                ).pack(side="left", padx=(10, 0))

                badge_wrap = ctk.CTkFrame(row_fr, width=140, fg_color="transparent")
                badge_wrap.pack(side="left", padx=(10, 0))
                badge_wrap.pack_propagate(False)
                badge = ctk.CTkFrame(badge_wrap, fg_color=sbg, corner_radius=SIZES["badge_radius"])
                badge.place(relx=0.5, rely=0.5, anchor="center")
                ctk.CTkLabel(badge, text=estado,
                    font=ctk.CTkFont(size=_FS["tiny"], weight="bold"), text_color=sfg,
                ).pack(padx=8, pady=3)

                btns = ctk.CTkFrame(row_fr, fg_color="transparent")
                btns.pack(side="right", padx=(0, 8))

                if self.is_admin and estado in ("En Mantenimiento", "En Reparación"):
                    ctk.CTkButton(
                        btns, text="✓  Completar", height=30, corner_radius=6,
                        fg_color=UI_COLORS.BADGE_BG["success"], hover_color="#BBF7D0",
                        text_color=UI_COLORS.BADGE_FG["success"],
                        font=ctk.CTkFont(size=_FS["small"], weight="bold"),
                        command=lambda m=mid: [self.completar_servicio(m), load_table()],
                    ).pack(side="left", padx=(0, 4))

                if self.is_admin and estado != "Desincorporada":
                    ctk.CTkButton(
                        btns, text="⛔  Desincorporar", height=30, corner_radius=6,
                        fg_color=UI_COLORS.BADGE_BG["warning"], hover_color="#FDE68A",
                        text_color=UI_COLORS.BADGE_FG["warning"],
                        font=ctk.CTkFont(size=_FS["small"]),
                        command=lambda m=mid, s=serial_num: _confirm_dialog(
                            "Desincorporar máquina", s,
                            "La máquina pasará a 'Desincorporada'.",
                            "Desincorporar",
                            lambda: [self.desincorporar_maquina(m), load_table()],
                            variant="warning",
                        ),
                    ).pack(side="left", padx=(0, 4))

                if self.is_admin:
                    ctk.CTkButton(
                        btns, text="🗑️  Eliminar", height=30, corner_radius=6,
                        fg_color=UI_COLORS.BADGE_BG["danger"], hover_color="#FECACA",
                        text_color=UI_COLORS.DANGER,
                        font=ctk.CTkFont(size=_FS["body"]),
                        command=lambda m=mid, s=serial_num: _confirm_dialog(
                            "Eliminar máquina", s,
                            "Se eliminará permanentemente del inventario.",
                            "Eliminar",
                            lambda: [self.eliminar_maquina(m), load_table()],
                            variant="danger",
                        ),
                    ).pack(side="left", padx=(0, 4))

                    ctk.CTkButton(
                        btns, text="✏️  Editar", height=30, corner_radius=6,
                        fg_color=UI_COLORS.BADGE_BG["default"], hover_color="#BFDBFE",
                        text_color=UI_COLORS.PRIMARY,
                        font=ctk.CTkFont(size=_FS["body"]),
                        command=lambda m=mid: self._open_edit_machine_dlg(m, on_save=load_table),
                    ).pack(side="left")

                ctk.CTkFrame(rows_sf, fg_color=UI_COLORS.BORDER_SUBTLE, height=1).pack(fill="x")

        search_e.bind("<Return>", lambda _: load_table())
        search_var.trace("w", lambda *_: load_table() if search_var.get() == "" else None)
        estado_var.trace("w", lambda *_: load_table())
        load_table()

    def _open_edit_machine_dlg(self, mid, on_save=None):
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            """
            SELECT m.serial_number, m.model_id, m.distributor_id, m.status,
                   mo.model_name, d.name
            FROM machines m
            LEFT JOIN machine_models mo ON m.model_id = mo.id
            LEFT JOIN distributors d    ON m.distributor_id = d.id
            WHERE m.id = ?
            """,
            (mid,),
        ).fetchone()
        conn.close()
        if not row:
            return
        serial_raw, model_id, distrib_id, status, model_name, distrib_name = row

        if " | Reg.SENIAT:" in (serial_raw or ""):
            serial_num, reg_seniat = serial_raw.split(" | Reg.SENIAT:", 1)
        else:
            serial_num, reg_seniat = serial_raw or "", ""

        dlg = ctk.CTkToplevel()
        dlg.title("")
        dlg.resizable(False, False)
        dlg.attributes("-topmost", True)
        dlg.configure(fg_color=UI_COLORS.CARD)
        dlg.after(50, dlg.grab_set)
        w, h = 680, 520
        dlg.update_idletasks()
        sx, sy = dlg.winfo_screenwidth(), dlg.winfo_screenheight()
        dlg.geometry(f"{w}x{h}+{(sx - w) // 2}+{(sy - h) // 2}")

        hdr = ctk.CTkFrame(dlg, fg_color="#2A3550", corner_radius=0, height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        hdr_row = ctk.CTkFrame(hdr, fg_color="transparent")
        hdr_row.pack(fill="both", expand=True, padx=SIZES["pad"])
        ctk.CTkLabel(hdr_row, text="✏️", font=ctk.CTkFont(size=20)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            hdr_row, text="Editar Máquina Fiscal",
            font=ctk.CTkFont(size=_FS["medium"], weight="bold"),
            text_color="#ffffff",
        ).pack(side="left")

        body = ctk.CTkScrollableFrame(
            dlg, fg_color="transparent", scrollbar_button_color=UI_COLORS.BORDER
        )
        body.pack(fill="both", expand=True, padx=SIZES["pad_large"], pady=SIZES["pad"])

        def _lbl(text):
            ctk.CTkLabel(
                body, text=text,
                font=ctk.CTkFont(size=_FS["small"], weight="bold"),
                text_color=UI_COLORS.TEXT_SECONDARY,
            ).pack(anchor="w", pady=(0, 4))

        def _entry(placeholder, value=""):
            e = ctk.CTkEntry(
                body, placeholder_text=placeholder,
                height=SIZES["entry_height"],
                corner_radius=SIZES["button_radius"],
                border_width=SIZES["border_width"],
                border_color=UI_COLORS.BORDER,
                fg_color="#F8FAFC", text_color=UI_COLORS.TEXT,
                placeholder_text_color=UI_COLORS.TEXT_MUTED,
            )
            e.pack(fill="x", pady=(0, SIZES["pad"]))
            if value:
                e.insert(0, value)
            return e

        _lbl("N° Serial")
        serial_e = _entry("Número de serial", serial_num)
        serial_e.bind("<KeyRelease>", lambda e: serial_e.configure(border_color=UI_COLORS.BORDER))

        _lbl("Reg. SENIAT")
        reg_e = _entry("Nro. Registro SENIAT", reg_seniat)
        reg_e.bind("<KeyRelease>", lambda e: reg_e.configure(border_color=UI_COLORS.BORDER))

        _lbl("Proveedor")
        prov_list = list(self.distrib_dict.keys()) or ["Sin proveedores"]
        prov_combo = ctk.CTkComboBox(
            body, values=prov_list,
            height=SIZES["entry_height"], corner_radius=SIZES["button_radius"], state="readonly",
            fg_color="#F8FAFC", text_color=UI_COLORS.TEXT,
            button_color=UI_COLORS.BORDER, button_hover_color=UI_COLORS.PRIMARY,
            dropdown_fg_color="white", dropdown_text_color=UI_COLORS.TEXT,
            border_color=UI_COLORS.BORDER,
        )
        prov_combo.pack(fill="x", pady=(0, SIZES["pad"]))
        prov_combo.set(distrib_name or (prov_list[0] if prov_list else ""))

        _lbl("Modelo")
        all_models = [mn for brand_dict in self.models_by_brand.values() for mn in brand_dict.keys()]
        model_combo = ctk.CTkComboBox(
            body, values=all_models or [""],
            height=SIZES["entry_height"], corner_radius=SIZES["button_radius"], state="normal",
            fg_color="#F8FAFC", text_color=UI_COLORS.TEXT,
            button_color=UI_COLORS.BORDER, button_hover_color=UI_COLORS.PRIMARY,
            dropdown_fg_color="white", dropdown_text_color=UI_COLORS.TEXT,
            border_color=UI_COLORS.BORDER,
        )
        model_combo.pack(fill="x", pady=(0, SIZES["pad"]))
        model_combo.set(model_name or "")
        model_combo.bind("<KeyRelease>", lambda e: model_combo.configure(border_color=UI_COLORS.BORDER))

        _lbl("Estado")
        status_combo = ctk.CTkComboBox(
            body,
            values=["En Stock", "Instalada", "En Mantenimiento", "En Reparación", "Desincorporada"],
            height=SIZES["entry_height"], corner_radius=SIZES["button_radius"], state="readonly",
            fg_color="#F8FAFC", text_color=UI_COLORS.TEXT,
            button_color=UI_COLORS.BORDER, button_hover_color=UI_COLORS.PRIMARY,
            dropdown_fg_color="white", dropdown_text_color=UI_COLORS.TEXT,
            border_color=UI_COLORS.BORDER,
        )
        status_combo.pack(fill="x", pady=(0, SIZES["pad"]))
        status_combo.set(status)

        msg_lbl = ctk.CTkLabel(
            dlg, text="",
            font=ctk.CTkFont(size=_FS["small"]),
            wraplength=560, justify="center",
        )
        msg_lbl.pack(padx=SIZES["pad_large"], pady=(SIZES["pad_small"], 0))

        def save():
            for w in (serial_e, reg_e, prov_combo, model_combo, status_combo):
                w.configure(border_color=UI_COLORS.BORDER)
            msg_lbl.configure(text="")

            new_serial = serial_e.get().strip()
            new_reg    = reg_e.get().strip()
            new_prov   = prov_combo.get().strip()
            new_model  = model_combo.get().strip()
            new_status = status_combo.get()

            errors = []
            if not new_serial:
                serial_e.configure(border_color=UI_COLORS.DANGER)
                errors.append("Serial")
            if not new_reg:
                reg_e.configure(border_color=UI_COLORS.DANGER)
                errors.append("Reg. SENIAT")
            if not new_prov or new_prov == "Sin proveedores":
                prov_combo.configure(border_color=UI_COLORS.DANGER)
                errors.append("Proveedor")
            if not new_model:
                model_combo.configure(border_color=UI_COLORS.DANGER)
                errors.append("Modelo")
            if errors:
                msg_lbl.configure(
                    text=f"⚠  Campos obligatorios: {', '.join(errors)}",
                    text_color=UI_COLORS.DANGER,
                )
                return

            serial_full = f"{new_serial} | Reg.SENIAT:{new_reg}" if new_reg else new_serial
            new_distrib_id = self.distrib_dict.get(new_prov)

            conn2 = None
            try:
                conn2 = sqlite3.connect(DB_PATH)
                existing_model = conn2.execute(
                    "SELECT id FROM machine_models WHERE model_name=?", (new_model,)
                ).fetchone()
                if existing_model:
                    new_model_id = existing_model[0]
                else:
                    new_model_id = conn2.execute(
                        "INSERT INTO machine_models (brand, model_name) VALUES (?,?)",
                        (new_prov, new_model),
                    ).lastrowid
                    self.models_by_brand.setdefault(new_prov, {})[new_model] = new_model_id

                conn2.execute(
                    "UPDATE machines SET serial_number=?, model_id=?, distributor_id=?, status=? WHERE id=?",
                    (serial_full, new_model_id, new_distrib_id, new_status, mid),
                )
                conn2.commit()
                msg_lbl.configure(text="✓  Cambios guardados", text_color=UI_COLORS.GREEN)
                logger.info(f"Máquina {mid} editada: {serial_full}")
                if on_save:
                    on_save()
                else:
                    self.load_machines()
            except sqlite3.IntegrityError:
                serial_e.configure(border_color=UI_COLORS.DANGER)
                msg_lbl.configure(text="⚠  Serial ya existe en inventario", text_color=UI_COLORS.DANGER)
            except Exception as e:
                log_error("inventory_view", "_open_edit_machine_dlg", e)
                msg_lbl.configure(text="⚠  Error interno", text_color=UI_COLORS.DANGER)
            finally:
                if conn2:
                    conn2.close()

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(fill="x", padx=SIZES["pad_large"], pady=(SIZES["pad_small"], SIZES["pad"]))
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            btn_row, text="Cancelar", command=dlg.destroy,
            fg_color=UI_COLORS.BORDER_SUBTLE, hover_color=UI_COLORS.BORDER,
            text_color=UI_COLORS.TEXT_SECONDARY,
            font=ctk.CTkFont(size=_FS["small"]),
            corner_radius=SIZES["button_radius"], height=SIZES["button_height"],
        ).grid(row=0, column=0, sticky="ew", padx=(0, SIZES["pad_small"]))

        ctk.CTkButton(
            btn_row, text="✓  Guardar Cambios", command=save,
            fg_color=UI_COLORS.PRIMARY, hover_color=UI_COLORS.SECONDARY,
            text_color="#ffffff",
            font=ctk.CTkFont(size=_FS["body"], weight="bold"),
            corner_radius=SIZES["button_radius"], height=SIZES["button_height"],
        ).grid(row=0, column=1, sticky="ew")

    def completar_servicio(self, mid):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE machines SET status='Instalada' WHERE id=?", (mid,))
            conn.commit()
            conn.close()
            logger.info(f"Máquina {mid} → Instalada (servicio completado)")
            self.load_machines()
        except Exception as e:
            log_error("inventory_view", "completar_servicio", e)
            self.message.configure(text="⚠  Error al completar servicio", text_color=UI_COLORS.DANGER)

    def desincorporar_maquina(self, mid):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE machines SET status='Desincorporada' WHERE id=?", (mid,))
            conn.commit()
            conn.close()
            logger.info(f"Máquina desincorporada: {mid}")
            self.load_machines()
        except Exception as e:
            log_error("inventory_view", "desincorporar_maquina", e)
            self.message.configure(text="⚠  Error al desincorporar", text_color=UI_COLORS.DANGER)

    def eliminar_maquina(self, mid):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("DELETE FROM machines WHERE id = ?", (mid,))
            conn.commit()
            conn.close()
            logger.info(f"Máquina eliminada: {mid}")
            self.load_machines()
        except Exception as e:
            log_error("inventory_view", "eliminar_maquina", e)
            self.message.configure(text="⚠  Error al eliminar", text_color=UI_COLORS.DANGER)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _lbl(parent, text):
        ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(size=_FS["small"], weight="bold"),
            text_color=UI_COLORS.TEXT_SECONDARY,
        ).pack(anchor="w", pady=(0, 4))

    @staticmethod
    def _entry(parent, placeholder):
        return ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            height=SIZES["entry_height"],
            corner_radius=SIZES["button_radius"],
            border_width=SIZES["border_width"],
            border_color=UI_COLORS.BORDER,
            fg_color="#F8FAFC", text_color=UI_COLORS.TEXT,
            placeholder_text_color=UI_COLORS.TEXT_MUTED,
        )

    @staticmethod
    def _combo(parent, values):
        return ctk.CTkComboBox(
            parent, values=values,
            height=SIZES["entry_height"],
            corner_radius=SIZES["button_radius"],
            state="readonly",
            fg_color="#F8FAFC", text_color=UI_COLORS.TEXT,
            button_color=UI_COLORS.BORDER, button_hover_color=UI_COLORS.PRIMARY,
            dropdown_fg_color="white", dropdown_text_color=UI_COLORS.TEXT,
            border_color=UI_COLORS.BORDER,
        )
