import customtkinter as ctk
import sqlite3
import os
from database.db_manager import DB_PATH
from theme import AppTheme, UI_COLORS, FONT_SIZES, SIZES
from utils.logger import logger, log_error

_FS = {k: round(v * 1.15) for k, v in FONT_SIZES.items()}



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


class ClientsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=AppTheme.BACKGROUND)
        self.pack(fill="both", expand=True)
        self.build_ui()

    def refresh(self):
        self.load_clients()

    def build_ui(self):
        pad = SIZES["pad_large"]
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=pad, pady=pad)

        self._build_stat_cards(content)
        self._build_main_panel(content)

    # ── Stat cards ────────────────────────────────────────────────────────────

    def _build_stat_cards(self, parent):
        stats = self._load_stats()
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, SIZES["pad"]))
        for i in range(3):
            row.grid_columnconfigure(i, weight=1)

        data = [
            ("Total Clientes",  stats["total"],         "#EFF6FF", "#2563EB", "👥"),
            ("Con Máquinas",    stats["con_maquinas"],  "#F0FDF4", "#16A34A", "🔧"),
            ("Sin Máquinas",    stats["sin_maquinas"],  "#FFFBEB", "#D97706", "📋"),
        ]
        for i, args in enumerate(data):
            _stat_card(row, i, *args)

    # ── Main panel ────────────────────────────────────────────────────────────

    def _build_main_panel(self, parent):
        main = ctk.CTkFrame(parent, fg_color="transparent")
        main.pack(fill="both", expand=True)
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=2)

        self._build_form(main)
        self._build_list(main)

    # ── Form ──────────────────────────────────────────────────────────────────

    def _build_form(self, parent):
        card = ctk.CTkFrame(parent, fg_color=UI_COLORS.CARD,
                            corner_radius=SIZES["card_radius"],
                            border_width=1, border_color=UI_COLORS.BORDER)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, SIZES["pad"]))

        ctk.CTkLabel(card, text="Nuevo Cliente",
                     font=ctk.CTkFont(size=_FS["large"], weight="bold"),
                     text_color=UI_COLORS.TEXT).pack(
            anchor="w", padx=SIZES["pad_large"],
            pady=(SIZES["pad_large"], SIZES["pad_small"]))

        ctk.CTkFrame(card, height=1, fg_color=UI_COLORS.BORDER_SUBTLE).pack(
            fill="x", padx=SIZES["pad_large"], pady=(0, SIZES["pad_small"]))

        fields = ctk.CTkFrame(card, fg_color="transparent")
        fields.pack(fill="x", padx=SIZES["pad_large"])

        self._lbl(fields, "Documento (RIF/RUT)")
        doc_row = ctk.CTkFrame(fields, fg_color="transparent")
        doc_row.pack(fill="x", pady=(0, SIZES["pad"]))
        doc_row.grid_columnconfigure(1, weight=1)

        self.doc_prefix_var = ctk.StringVar(value="J-")
        ctk.CTkSegmentedButton(
            doc_row,
            values=["J-", "C-"],
            variable=self.doc_prefix_var,
            width=80,
            height=SIZES["entry_height"],
            corner_radius=SIZES["button_radius"],
            fg_color=UI_COLORS.BORDER_SUBTLE,
            selected_color=UI_COLORS.PRIMARY,
            selected_hover_color=UI_COLORS.SECONDARY,
            unselected_color=UI_COLORS.BORDER_SUBTLE,
            unselected_hover_color=UI_COLORS.BORDER,
            text_color=UI_COLORS.TEXT,
        ).grid(row=0, column=0, sticky="w", padx=(0, SIZES["pad_small"]))

        _vcmd = (self.register(lambda P: P == "" or P.isdigit()), "%P")
        self.doc_entry = self._entry(doc_row, "12345678-9")
        self.doc_entry.configure(validate="key", validatecommand=_vcmd)
        self.doc_entry.grid(row=0, column=1, sticky="ew")
        self.doc_entry.bind("<KeyRelease>", lambda e: self.doc_entry.configure(border_color=UI_COLORS.BORDER))

        self._lbl(fields, "Nombre / Razón Social")
        self.name_entry = self._entry(fields, "Empresa SA")
        self.name_entry.pack(fill="x", pady=(0, SIZES["pad"]))
        self.name_entry.bind("<KeyRelease>", lambda e: self.name_entry.configure(border_color=UI_COLORS.BORDER))

        self._lbl(fields, "Teléfono")
        self.phone_entry = self._entry(fields, "04140000000")
        self.phone_entry.configure(validate="key", validatecommand=_vcmd)
        self.phone_entry.pack(fill="x", pady=(0, SIZES["pad"]))

        self._lbl(fields, "Dirección")
        self.address_entry = self._entry(fields, "Dirección completa")
        self.address_entry.pack(fill="x", pady=(0, SIZES["pad_large"]))

        ctk.CTkButton(
            card, text="✓  Registrar Cliente",
            command=self.add_client,
            fg_color=UI_COLORS.PRIMARY, hover_color=UI_COLORS.SECONDARY,
            text_color="#ffffff",
            font=ctk.CTkFont(size=_FS["body"], weight="bold"),
            corner_radius=SIZES["button_radius"],
            height=SIZES["button_height"],
        ).pack(fill="x", padx=SIZES["pad_large"], pady=(0, SIZES["pad_small"]))

        self.message = ctk.CTkLabel(card, text="",
                                    font=ctk.CTkFont(size=_FS["tiny"]))
        self.message.pack(padx=SIZES["pad_large"], pady=(0, SIZES["pad"]))

    # ── List ──────────────────────────────────────────────────────────────────

    def _build_list(self, parent):
        card = ctk.CTkFrame(parent, fg_color=UI_COLORS.CARD,
                            corner_radius=SIZES["card_radius"],
                            border_width=1, border_color=UI_COLORS.BORDER)
        card.grid(row=0, column=1, sticky="nsew", padx=(SIZES["pad"], 0))

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=SIZES["pad_large"],
                 pady=(SIZES["pad_large"], SIZES["pad_small"]))

        ctk.CTkLabel(hdr, text="Clientes",
                     font=ctk.CTkFont(size=_FS["large"], weight="bold"),
                     text_color=UI_COLORS.TEXT).pack(side="left")

        self.count_label = ctk.CTkLabel(hdr, text="",
                                        font=ctk.CTkFont(size=_FS["small"]),
                                        text_color=UI_COLORS.TEXT_MUTED)
        self.count_label.pack(side="right", padx=(0, SIZES["pad_small"]))

        sw = ctk.CTkFrame(hdr, fg_color="#F8FAFC",
                          corner_radius=SIZES["button_radius"],
                          border_width=1, border_color=UI_COLORS.BORDER)
        sw.pack(side="right", padx=(0, SIZES["pad_small"]))
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *e: self.load_clients())
        ctk.CTkEntry(sw, textvariable=self.search_var,
                     placeholder_text="🔍  Buscar...",
                     fg_color="transparent", border_width=0,
                     text_color=UI_COLORS.TEXT,
                     placeholder_text_color=UI_COLORS.TEXT_MUTED,
                     width=180).pack(padx=SIZES["pad_small"], pady=4)

        ctk.CTkFrame(card, height=1, fg_color=UI_COLORS.BORDER_SUBTLE).pack(
            fill="x", padx=SIZES["pad_large"], pady=(0, SIZES["pad_small"]))

        self.scroll_frame = ctk.CTkScrollableFrame(
            card, fg_color="transparent",
            scrollbar_button_color=UI_COLORS.BORDER)
        self.scroll_frame.pack(fill="both", expand=True,
                               padx=SIZES["pad_large"],
                               pady=(0, SIZES["pad_large"]))
        self.load_clients()

    # ── Data ops ──────────────────────────────────────────────────────────────

    @staticmethod
    def _load_stats():
        s = {"total": 0, "con_maquinas": 0, "sin_maquinas": 0}
        if not os.path.exists(DB_PATH):
            return s
        try:
            conn = sqlite3.connect(DB_PATH)
            s["total"]        = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
            s["con_maquinas"] = conn.execute(
                "SELECT COUNT(DISTINCT client_id) FROM machines WHERE client_id IS NOT NULL"
            ).fetchone()[0]
            s["sin_maquinas"] = s["total"] - s["con_maquinas"]
            conn.close()
        except Exception as e:
            log_error("clients_view", "_load_stats", e)
        return s

    def add_client(self):
        self.doc_entry.configure(border_color=UI_COLORS.BORDER)
        self.name_entry.configure(border_color=UI_COLORS.BORDER)
        self.message.configure(text="")

        raw_doc = self.doc_entry.get().strip()
        doc     = self.doc_prefix_var.get() + raw_doc
        name    = self.name_entry.get().strip()
        phone   = self.phone_entry.get().strip()
        address = self.address_entry.get().strip()

        errors = []
        if not raw_doc:
            self.doc_entry.configure(border_color=UI_COLORS.DANGER)
            errors.append("Documento")
        if not name:
            self.name_entry.configure(border_color=UI_COLORS.DANGER)
            errors.append("Nombre")
        if errors:
            self.message.configure(
                text=f"⚠  Obligatorio: {', '.join(errors)}",
                text_color=UI_COLORS.DANGER,
            )
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "INSERT INTO clients (document_id, name, address, phone) VALUES (?, ?, ?, ?)",
                (doc, name, address, phone),
            )
            conn.commit()
            conn.close()
            self.doc_entry.delete(0, "end")
            self.name_entry.delete(0, "end")
            self.phone_entry.delete(0, "end")
            self.address_entry.delete(0, "end")
            self.doc_prefix_var.set("J-")
            self.message.configure(text="✓  Cliente registrado",
                                   text_color=UI_COLORS.GREEN)
            logger.info(f"Cliente registrado: {doc}")
            self.load_clients()
        except sqlite3.IntegrityError:
            self.doc_entry.configure(border_color=UI_COLORS.DANGER)
            self.message.configure(text="⚠  El documento ya existe",
                                   text_color=UI_COLORS.DANGER)
        except Exception as e:
            log_error("clients_view", "add_client", e)
            self.message.configure(text="⚠  Error interno",
                                   text_color=UI_COLORS.DANGER)

    def load_clients(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        if not os.path.exists(DB_PATH):
            self.count_label.configure(text="0 clientes")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            busq = self.search_var.get().strip().lower()
            wc, params = "", []
            if busq:
                wc = "WHERE LOWER(name) LIKE ? OR LOWER(document_id) LIKE ?"
                lk = f"%{busq}%"
                params = [lk, lk]

            rows = conn.execute(
                f"SELECT id, document_id, name, phone, address FROM clients {wc} ORDER BY id DESC",
                params,
            ).fetchall()
            conn.close()

            self.count_label.configure(
                text=f"{len(rows)} cliente{'s' if len(rows) != 1 else ''}")

            if not rows:
                ctk.CTkLabel(self.scroll_frame, text="No hay clientes",
                             font=ctk.CTkFont(size=_FS["body"]),
                             text_color=UI_COLORS.TEXT_MUTED).pack(pady=30)
                return
            for r in rows:
                self._client_card(r)
        except Exception as e:
            log_error("clients_view", "load_clients", e)
            ctk.CTkLabel(self.scroll_frame, text="⚠  Error al cargar clientes",
                         font=ctk.CTkFont(size=_FS["body"]),
                         text_color=UI_COLORS.DANGER).pack(pady=30)

    def _client_card(self, row):
        cid, doc, name, phone, addr = row

        card = ctk.CTkFrame(self.scroll_frame, fg_color=UI_COLORS.CARD,
                            corner_radius=SIZES["card_radius"],
                            border_width=1, border_color=UI_COLORS.BORDER)
        card.pack(fill="x", pady=5)

        c = ctk.CTkFrame(card, fg_color="transparent")
        c.pack(fill="both", expand=True, padx=SIZES["pad"], pady=SIZES["pad_small"])

        left = ctk.CTkFrame(c, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        avatar = ctk.CTkFrame(left, width=36, height=36,
                              fg_color="#EFF6FF", corner_radius=18)
        avatar.pack(side="left")
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text=name[0].upper() if name else "?",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#2563EB").place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(left, fg_color="transparent")
        info.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(info, text=name,
                     font=ctk.CTkFont(size=_FS["body"], weight="bold"),
                     text_color=UI_COLORS.TEXT).pack(anchor="w")
        ctk.CTkLabel(info, text=doc,
                     font=ctk.CTkFont(size=_FS["small"]),
                     text_color=UI_COLORS.TEXT_SECONDARY).pack(anchor="w", pady=(2, 0))
        if phone:
            ctk.CTkLabel(info, text=f"📞 {phone}",
                         font=ctk.CTkFont(size=_FS["tiny"]),
                         text_color=UI_COLORS.TEXT_MUTED).pack(anchor="w", pady=(2, 0))

        del_btn = ctk.CTkButton(c, text="🗑️",
                      command=lambda ci=cid: self.eliminar_cliente(ci),
                      width=32, height=32, corner_radius=6,
                      fg_color="#FEF2F2", hover_color="#FECACA",
                      text_color=UI_COLORS.DANGER,
                      font=ctk.CTkFont(size=_FS["body"]))
        del_btn.pack(side="right", pady=4)

    def eliminar_cliente(self, cid):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("DELETE FROM clients WHERE id = ?", (cid,))
            conn.commit()
            conn.close()
            logger.info(f"Cliente eliminado: {cid}")
            self.load_clients()
        except Exception as e:
            log_error("clients_view", "eliminar_cliente", e)
            self.message.configure(text="⚠  Error al eliminar",
                                   text_color=UI_COLORS.DANGER)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _lbl(parent, text):
        ctk.CTkLabel(parent, text=text,
                     font=ctk.CTkFont(size=_FS["small"], weight="bold"),
                     text_color=UI_COLORS.TEXT_SECONDARY).pack(anchor="w", pady=(0, 4))

    @staticmethod
    def _entry(parent, placeholder):
        return ctk.CTkEntry(parent, placeholder_text=placeholder,
                            height=SIZES["entry_height"],
                            corner_radius=SIZES["button_radius"],
                            border_width=SIZES["border_width"],
                            border_color=UI_COLORS.BORDER,
                            fg_color="#F8FAFC",
                            text_color=UI_COLORS.TEXT,
                            placeholder_text_color=UI_COLORS.TEXT_MUTED)
