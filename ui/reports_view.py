import customtkinter as ctk
import sqlite3
import os
import openpyxl
from datetime import date
from tkinter import filedialog
from database.db_manager import DB_PATH
from theme import AppTheme, UI_COLORS, FONT_SIZES, SIZES

_FS = {k: round(v * 1.15) for k, v in FONT_SIZES.items()}
from utils.logger import logger, log_error


def _stat_card(parent, col, label, value, bg, color, icon):
    card = ctk.CTkFrame(parent, fg_color=UI_COLORS.CARD,
                        corner_radius=SIZES["card_radius"],
                        border_width=1, border_color=UI_COLORS.BORDER)
    card.grid(row=0, column=col,
              padx=(0 if col == 0 else SIZES["pad_small"], 0),
              sticky="ew")
    inner = ctk.CTkFrame(card, fg_color="transparent")
    inner.pack(fill="x", padx=SIZES["pad"], pady=SIZES["pad"])
    box = ctk.CTkFrame(inner, width=SIZES["icon_box"], height=SIZES["icon_box"],
                       fg_color=bg, corner_radius=10)
    box.pack(anchor="w")
    box.pack_propagate(False)
    ctk.CTkLabel(box, text=icon, font=ctk.CTkFont(size=16),
                 text_color=color).place(relx=0.5, rely=0.5, anchor="center")
    ctk.CTkLabel(inner, text=str(value),
                 font=ctk.CTkFont(size=_FS["xxlarge"], weight="bold"),
                 text_color=UI_COLORS.TEXT).pack(anchor="w", pady=(6, 2))
    ctk.CTkLabel(inner, text=label,
                 font=ctk.CTkFont(size=_FS["small"]),
                 text_color=UI_COLORS.TEXT_MUTED).pack(anchor="w")


class ReportsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=AppTheme.BACKGROUND)
        self.pack(fill="both", expand=True)
        self.build_ui()

    def refresh(self):
        self.load_summary()
        self.load_inventory()

    def build_ui(self):
        pad = SIZES["pad_large"]
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=pad, pady=pad)

        self._build_stat_cards(content)
        self._build_tabs(content)

    # ── Stat cards ────────────────────────────────────────────────────────────

    def _build_stat_cards(self, parent):
        conn = sqlite3.connect(DB_PATH)
        m = conn.execute("SELECT COUNT(*) FROM machines").fetchone()[0]
        c = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
        s = conn.execute("SELECT COUNT(*) FROM services").fetchone()[0]
        d = conn.execute("SELECT COUNT(*) FROM distributors").fetchone()[0]
        conn.close()

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, SIZES["pad"]))
        for i in range(4):
            row.grid_columnconfigure(i, weight=1)

        data = [
            ("Máquinas",       m, "#EFF6FF", "#2563EB", "📦"),
            ("Clientes",       c, "#F0FDF4", "#16A34A", "👥"),
            ("Servicios",      s, "#FFFBEB", "#D97706", "🔧"),
            ("Distribuidores", d, "#FAF5FF", "#7C3AED", "🏢"),
        ]
        for i, args in enumerate(data):
            _stat_card(row, i, *args)

    # ── Tabs ──────────────────────────────────────────────────────────────────

    def _build_tabs(self, parent):
        self.tabview = ctk.CTkTabview(
            parent,
            fg_color=UI_COLORS.CARD,
            segmented_button_fg_color=UI_COLORS.BORDER_SUBTLE,
            segmented_button_selected_color=UI_COLORS.PRIMARY,
            segmented_button_selected_hover_color=UI_COLORS.SECONDARY,
            segmented_button_unselected_color=UI_COLORS.BORDER_SUBTLE,
            segmented_button_unselected_hover_color=UI_COLORS.BORDER,
            text_color=UI_COLORS.TEXT,
            text_color_disabled=UI_COLORS.TEXT_MUTED,
            border_width=1,
            border_color=UI_COLORS.BORDER,
            corner_radius=SIZES["card_radius"],
        )
        self.tabview.pack(fill="both", expand=True)

        self.tab_inventory = self.tabview.add("📦  Inventario")
        self.tab_alerts    = self.tabview.add("⚠️  Alertas")
        self.tab_summary   = self.tabview.add("📈  Resumen")

        self._build_inventory()
        self._build_alerts()
        self._build_summary()

    # ── Tab: Inventario ───────────────────────────────────────────────────────

    def _build_inventory(self):
        main = ctk.CTkFrame(self.tab_inventory, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=SIZES["pad"], pady=SIZES["pad"])
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=2)
        main.grid_columnconfigure(1, weight=1)

        self._build_inv_table(main)
        self._build_inv_summary(main)

    def _build_inv_table(self, parent):
        card = ctk.CTkFrame(parent, fg_color=UI_COLORS.CARD,
                            corner_radius=SIZES["card_radius"],
                            border_width=1, border_color=UI_COLORS.BORDER)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, SIZES["pad"]))

        bar = ctk.CTkFrame(card, fg_color="transparent")
        bar.pack(fill="x", padx=SIZES["pad_large"],
                 pady=(SIZES["pad_large"], SIZES["pad_small"]))

        ctk.CTkLabel(bar, text="Inventario General",
                     font=ctk.CTkFont(size=_FS["large"], weight="bold"),
                     text_color=UI_COLORS.TEXT).pack(side="left")

        ctk.CTkButton(bar, text="📥  Exportar Excel",
                      command=self.export_inventory,
                      fg_color=UI_COLORS.PRIMARY, hover_color=UI_COLORS.SECONDARY,
                      text_color="#ffffff",
                      corner_radius=SIZES["button_radius"], height=32,
                      font=ctk.CTkFont(size=_FS["small"], weight="bold"),
                      ).pack(side="right")

        sw = ctk.CTkFrame(bar, fg_color="#F8FAFC",
                          corner_radius=SIZES["button_radius"],
                          border_width=1, border_color=UI_COLORS.BORDER)
        sw.pack(side="right", padx=(0, SIZES["pad_small"]))
        self.search_inv = ctk.StringVar()
        self.search_inv.trace("w", lambda *e: self.load_inventory())
        ctk.CTkEntry(sw, textvariable=self.search_inv,
                     placeholder_text="🔍  Buscar...",
                     fg_color="transparent", border_width=0,
                     text_color=UI_COLORS.TEXT,
                     placeholder_text_color=UI_COLORS.TEXT_MUTED,
                     width=160).pack(padx=SIZES["pad_small"], pady=4)

        ctk.CTkFrame(card, height=1, fg_color=UI_COLORS.BORDER_SUBTLE).pack(
            fill="x", padx=SIZES["pad_large"], pady=(0, SIZES["pad_small"]))

        self.inv_scroll = ctk.CTkScrollableFrame(
            card, fg_color="transparent",
            scrollbar_button_color=UI_COLORS.BORDER)
        self.inv_scroll.pack(fill="both", expand=True,
                             padx=SIZES["pad_large"],
                             pady=(0, SIZES["pad_large"]))
        self.load_inventory()

    def _build_inv_summary(self, parent):
        card = ctk.CTkFrame(parent, fg_color=UI_COLORS.CARD,
                            corner_radius=SIZES["card_radius"],
                            border_width=1, border_color=UI_COLORS.BORDER)
        card.grid(row=0, column=1, sticky="nsew", padx=(SIZES["pad"], 0))

        ctk.CTkLabel(card, text="Distribución",
                     font=ctk.CTkFont(size=_FS["large"], weight="bold"),
                     text_color=UI_COLORS.TEXT).pack(
            anchor="w", padx=SIZES["pad_large"],
            pady=(SIZES["pad_large"], SIZES["pad_small"]))

        ctk.CTkFrame(card, height=1, fg_color=UI_COLORS.BORDER_SUBTLE).pack(
            fill="x", padx=SIZES["pad_large"], pady=(0, SIZES["pad"]))

        self.sum_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.sum_frame.pack(fill="x", padx=SIZES["pad_large"],
                            pady=SIZES["pad_small"])
        self.load_summary()

    def load_summary(self):
        for w in self.sum_frame.winfo_children():
            w.destroy()

        conn = sqlite3.connect(DB_PATH)
        sc = {}
        for s, c in conn.execute("SELECT status, COUNT(*) FROM machines GROUP BY status"):
            sc[s] = c
        conn.close()

        total = sum(sc.values())
        cmap = {
            "En Stock":       ("#F0FDF4", "#16A34A"),
            "Instalada":      ("#EFF6FF", "#2563EB"),
            "Desincorporada": ("#FEF2F2", "#DC2626"),
        }

        for status, count in sc.items():
            pct = int(count / total * 100) if total else 0
            bg, fg = cmap.get(status, ("#F8FAFC", "#64748B"))

            f = ctk.CTkFrame(self.sum_frame, fg_color=UI_COLORS.BORDER_SUBTLE,
                             corner_radius=SIZES["button_radius"])
            f.pack(fill="x", pady=5)

            top = ctk.CTkFrame(f, fg_color="transparent")
            top.pack(fill="x", padx=SIZES["pad_small"], pady=(SIZES["pad_small"], 4))

            badge = ctk.CTkFrame(top, fg_color=bg, corner_radius=SIZES["badge_radius"])
            badge.pack(side="left")
            ctk.CTkLabel(badge, text=status,
                         font=ctk.CTkFont(size=_FS["tiny"], weight="bold"),
                         text_color=fg).pack(padx=10, pady=3)

            ctk.CTkLabel(top, text=f"{count}  ({pct}%)",
                         font=ctk.CTkFont(size=_FS["small"], weight="bold"),
                         text_color=UI_COLORS.TEXT).pack(side="right")

            pb = ctk.CTkFrame(f, fg_color=UI_COLORS.BORDER, corner_radius=4, height=8)
            pb.pack(fill="x", padx=SIZES["pad_small"], pady=(0, SIZES["pad_small"]))
            ctk.CTkFrame(pb, fg_color=fg, corner_radius=4).place(
                relwidth=pct / 100, relheight=1)

    def load_inventory(self):
        for w in self.inv_scroll.winfo_children():
            w.destroy()

        conn = sqlite3.connect(DB_PATH)
        busq = self.search_inv.get().strip().lower()
        query = """
            SELECT m.serial_number, mo.brand || ' ' || mo.model_name,
                   d.name, m.status, IFNULL(c.name, '—')
            FROM machines m
            LEFT JOIN machine_models mo ON m.model_id = mo.id
            LEFT JOIN distributors d ON m.distributor_id = d.id
            LEFT JOIN clients c ON m.client_id = c.id
        """
        params = []
        if busq:
            query += " WHERE LOWER(m.serial_number) LIKE ? OR LOWER(mo.brand) LIKE ? OR LOWER(mo.model_name) LIKE ?"
            lk = f"%{busq}%"
            params = [lk, lk, lk]
        query += " ORDER BY m.id DESC"
        rows = conn.execute(query, params).fetchall()
        conn.close()

        for r in rows:
            self._inv_row(r)

    def _inv_row(self, row):
        serial, modelo, dist, sta, cli = row
        sfg = UI_COLORS.STATUS_COLORS.get(sta, UI_COLORS.GRAY)
        sbg = UI_COLORS.STATUS_BADGE_BG.get(sta, "#F8FAFC")

        card = ctk.CTkFrame(self.inv_scroll, fg_color=UI_COLORS.CARD,
                            corner_radius=8, border_width=1,
                            border_color=UI_COLORS.BORDER)
        card.pack(fill="x", pady=4)

        c = ctk.CTkFrame(card, fg_color="transparent")
        c.pack(fill="both", expand=True, padx=SIZES["pad"], pady=SIZES["pad_small"])

        left = ctk.CTkFrame(c, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(left, text=serial,
                     font=ctk.CTkFont(size=_FS["body"], weight="bold"),
                     text_color=UI_COLORS.TEXT).pack(anchor="w")
        ctk.CTkLabel(left, text=modelo,
                     font=ctk.CTkFont(size=_FS["small"]),
                     text_color=UI_COLORS.TEXT_SECONDARY).pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(left, text=f"{dist or '—'}  •  {cli}",
                     font=ctk.CTkFont(size=_FS["tiny"]),
                     text_color=UI_COLORS.TEXT_MUTED).pack(anchor="w", pady=(2, 0))

        badge = ctk.CTkFrame(left, fg_color=sbg, corner_radius=SIZES["badge_radius"])
        badge.pack(anchor="w", pady=(6, 0))
        ctk.CTkLabel(badge, text=sta,
                     font=ctk.CTkFont(size=_FS["tiny"], weight="bold"),
                     text_color=sfg).pack(padx=10, pady=3)

    # ── Tab: Alertas ──────────────────────────────────────────────────────────

    def _build_alerts(self):
        card = ctk.CTkFrame(self.tab_alerts, fg_color=UI_COLORS.CARD,
                            corner_radius=SIZES["card_radius"],
                            border_width=1, border_color=UI_COLORS.BORDER)
        card.pack(fill="both", expand=True, padx=SIZES["pad"], pady=SIZES["pad"])

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=SIZES["pad_large"],
                 pady=(SIZES["pad_large"], SIZES["pad_small"]))
        ctk.CTkLabel(hdr, text="⚠️  Alertas de Mantenimiento (próximos 30 días)",
                     font=ctk.CTkFont(size=_FS["large"], weight="bold"),
                     text_color=UI_COLORS.TEXT).pack(side="left")

        ctk.CTkFrame(card, height=1, fg_color=UI_COLORS.BORDER_SUBTLE).pack(
            fill="x", padx=SIZES["pad_large"], pady=(0, SIZES["pad_small"]))

        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute("""
            SELECT m.serial_number, mo.brand || ' ' || mo.model_name, s.next_maintenance_date
            FROM services s
            JOIN machines m ON s.machine_id = m.id
            JOIN machine_models mo ON m.model_id = mo.id
            WHERE s.next_maintenance_date < date('now', '+30 days')
              AND s.next_maintenance_date >= date('now')
            ORDER BY s.next_maintenance_date
        """).fetchall()
        conn.close()

        sf = ctk.CTkScrollableFrame(card, fg_color="transparent",
                                    scrollbar_button_color=UI_COLORS.BORDER)
        sf.pack(fill="both", expand=True,
                padx=SIZES["pad"], pady=SIZES["pad_small"])

        if not rows:
            ctk.CTkLabel(sf, text="✅  Sin alertas próximas",
                         font=ctk.CTkFont(size=_FS["body"]),
                         text_color=UI_COLORS.GREEN).pack(pady=30)
            return

        for ser, mod, nxt in rows:
            item = ctk.CTkFrame(sf, fg_color="#FFFBEB", corner_radius=8,
                                border_width=1, border_color="#FDE68A")
            item.pack(fill="x", pady=4)
            r = ctk.CTkFrame(item, fg_color="transparent")
            r.pack(fill="x", padx=SIZES["pad"], pady=SIZES["pad_small"])
            ctk.CTkLabel(r, text=f"📅  {nxt}",
                         font=ctk.CTkFont(size=_FS["small"], weight="bold"),
                         text_color="#D97706").pack(side="left")
            ctk.CTkLabel(r, text=f"  {ser}  —  {mod}",
                         font=ctk.CTkFont(size=_FS["small"]),
                         text_color=UI_COLORS.TEXT_SECONDARY).pack(side="left")

    # ── Tab: Resumen ──────────────────────────────────────────────────────────

    def _build_summary(self):
        card = ctk.CTkFrame(self.tab_summary, fg_color=UI_COLORS.CARD,
                            corner_radius=SIZES["card_radius"],
                            border_width=1, border_color=UI_COLORS.BORDER)
        card.pack(fill="both", expand=True, padx=SIZES["pad"], pady=SIZES["pad"])

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=SIZES["pad_large"],
                 pady=(SIZES["pad_large"], SIZES["pad_small"]))
        ctk.CTkLabel(hdr, text="📈  Resumen General",
                     font=ctk.CTkFont(size=_FS["large"], weight="bold"),
                     text_color=UI_COLORS.TEXT).pack(side="left")

        ctk.CTkFrame(card, height=1, fg_color=UI_COLORS.BORDER_SUBTLE).pack(
            fill="x", padx=SIZES["pad_large"], pady=(0, SIZES["pad"]))

        conn = sqlite3.connect(DB_PATH)
        m  = conn.execute("SELECT COUNT(*) FROM machines").fetchone()[0]
        c  = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
        s  = conn.execute("SELECT COUNT(*) FROM services").fetchone()[0]
        d  = conn.execute("SELECT COUNT(*) FROM distributors").fetchone()[0]
        mm = conn.execute("SELECT COUNT(*) FROM machine_models").fetchone()[0]
        conn.close()

        data = [
            ("Máquinas registradas", m,  "#EFF6FF", "#2563EB"),
            ("Clientes activos",     c,  "#F0FDF4", "#16A34A"),
            ("Servicios realizados", s,  "#FFFBEB", "#D97706"),
            ("Distribuidores",       d,  "#FAF5FF", "#7C3AED"),
            ("Modelos de máquinas",  mm, "#F8FAFC",  "#64748B"),
        ]

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="both", expand=True,
                  padx=SIZES["pad_large"], pady=SIZES["pad_small"])
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        for idx, (label, val, bg, fg) in enumerate(data):
            cf = ctk.CTkFrame(grid, fg_color=bg,
                              corner_radius=SIZES["card_radius"])
            cf.grid(row=idx // 2, column=idx % 2,
                    padx=(0 if idx % 2 == 0 else SIZES["pad_small"], 0),
                    pady=(0 if idx < 2 else SIZES["pad_small"], 0),
                    sticky="ew")
            ci = ctk.CTkFrame(cf, fg_color="transparent")
            ci.pack(fill="both", padx=SIZES["pad"], pady=SIZES["pad"])
            ctk.CTkLabel(ci, text=str(val),
                         font=ctk.CTkFont(size=_FS["xxlarge"], weight="bold"),
                         text_color=fg).pack(anchor="w")
            ctk.CTkLabel(ci, text=label,
                         font=ctk.CTkFont(size=_FS["small"]),
                         text_color=UI_COLORS.TEXT_SECONDARY).pack(
                anchor="w", pady=(2, 0))

    # ── Export ────────────────────────────────────────────────────────────────

    def export_inventory(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=f"Inventario_{date.today().strftime('%Y%m%d')}.xlsx",
            filetypes=[("Excel", "*.xlsx")],
        )
        if not path:
            return

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Inventario"
        ws.append(["Serial", "Modelo", "Distribuidor", "Estado", "Cliente"])

        conn = sqlite3.connect(DB_PATH)
        for r in conn.execute("""
            SELECT m.serial_number, mo.brand || ' ' || mo.model_name,
                   d.name, m.status, IFNULL(c.name, '-')
            FROM machines m
            LEFT JOIN machine_models mo ON m.model_id = mo.id
            LEFT JOIN distributors d ON m.distributor_id = d.id
            LEFT JOIN clients c ON m.client_id = c.id
        """):
            ws.append(r)
        conn.close()

        wb.save(path)
        logger.info(f"Inventario exportado: {path}")
