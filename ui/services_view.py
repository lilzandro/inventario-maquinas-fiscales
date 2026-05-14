import customtkinter as ctk
import sqlite3
import os
from datetime import date, datetime
from database.db_manager import DB_PATH
from theme import AppTheme, UI_COLORS, FONT_SIZES, SIZES

_FS = {k: round(v * 1.10) for k, v in FONT_SIZES.items()}
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


_SVC_STYLE = {
    "Instalación":              ("#EFF6FF", "#2563EB", "🔧"),
    "Mantenimiento Preventivo": ("#F0FDF4", "#16A34A", "🛠️"),
    "Reparación":               ("#FFFBEB", "#D97706", "⚙️"),
}


class ServicesView(ctk.CTkFrame):
    def __init__(self, master, user_info=None):
        super().__init__(master, fg_color=AppTheme.BACKGROUND)
        self.pack(fill="both", expand=True)
        self.username = user_info[1] if user_info else "sistema"
        self.machines_dict = {}
        self.clients_dict = {}
        self.load_reference_data()
        self.build_ui()

    def refresh(self):
        self.load_reference_data()
        self.load_services()

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
        for i in range(4):
            row.grid_columnconfigure(i, weight=1)

        data = [
            ("Total Servicios",   stats["total"],          "#EFF6FF", "#2563EB", "📋"),
            ("Instalaciones",     stats["instalacion"],    "#F0FDF4", "#16A34A", "🔧"),
            ("Mantenimientos",    stats["mantenimiento"],  "#FFFBEB", "#D97706", "🛠️"),
            ("Reparaciones",      stats["reparacion"],     "#FEF2F2", "#DC2626", "⚙️"),
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

        ctk.CTkLabel(card, text="Nuevo Servicio",
                     font=ctk.CTkFont(size=_FS["large"], weight="bold"),
                     text_color=UI_COLORS.TEXT).pack(
            anchor="w", padx=SIZES["pad_large"],
            pady=(SIZES["pad_large"], SIZES["pad_small"]))

        ctk.CTkFrame(card, height=1, fg_color=UI_COLORS.BORDER_SUBTLE).pack(
            fill="x", padx=SIZES["pad_large"], pady=(0, SIZES["pad_small"]))

        fields = ctk.CTkFrame(card, fg_color="transparent")
        fields.pack(fill="x", padx=SIZES["pad_large"])

        self._lbl(fields, "Tipo de Servicio")
        self.type_combo = self._combo(
            fields, ["Instalación", "Mantenimiento Preventivo", "Reparación"])
        self.type_combo.pack(fill="x", pady=(0, SIZES["pad"]))
        self.type_combo.configure(command=self._on_type_change)

        self._lbl(fields, "Máquina")
        self.machine_combo = self._combo(fields, list(self.machines_dict.keys()))
        self.machine_combo.pack(fill="x", pady=(0, SIZES["pad"]))

        # Cliente — visible solo para Instalación
        self._client_lbl = ctk.CTkLabel(fields, text="Cliente",
                                        font=ctk.CTkFont(size=_FS["small"], weight="bold"),
                                        text_color=UI_COLORS.TEXT_SECONDARY)
        self.client_combo = self._combo(fields, list(self.clients_dict.keys()) or [""])
        # oculto por defecto
        self._client_lbl.pack_forget()
        self.client_combo.pack_forget()

        self._lbl(fields, "Fecha Servicio")
        self.svc_date = self._entry(fields, "YYYY-MM-DD")
        self.svc_date.insert(0, date.today().strftime("%Y-%m-%d"))
        self.svc_date.pack(fill="x", pady=(0, SIZES["pad"]))

        self._lbl(fields, "Próximo Mantenimiento")
        self.next_maint = self._entry(fields, "YYYY-MM-DD (opcional)")
        self.next_maint.pack(fill="x", pady=(0, SIZES["pad"]))

        self._lbl(fields, "Observaciones")
        self.remarks = ctk.CTkTextbox(
            fields, height=80,
            corner_radius=SIZES["button_radius"],
            fg_color="#F8FAFC",
            text_color=UI_COLORS.TEXT,
            border_width=SIZES["border_width"],
            border_color=UI_COLORS.BORDER,
        )
        self.remarks.pack(fill="x", pady=(0, SIZES["pad_large"]))

        ctk.CTkButton(
            card, text="✓  Registrar Servicio",
            command=self.add_service,
            fg_color=UI_COLORS.PRIMARY, hover_color=UI_COLORS.SECONDARY,
            text_color="#ffffff",
            font=ctk.CTkFont(size=_FS["body"], weight="bold"),
            corner_radius=SIZES["button_radius"],
            height=SIZES["button_height"],
        ).pack(fill="x", padx=SIZES["pad_large"], pady=(0, SIZES["pad_small"]))

        self.message = ctk.CTkLabel(card, text="",
                                    font=ctk.CTkFont(size=_FS["tiny"]))
        self.message.pack(padx=SIZES["pad_large"], pady=(0, SIZES["pad"]))

    def _on_type_change(self, value):
        try:
            svc_dt = datetime.strptime(self.svc_date.get().strip(), "%Y-%m-%d").date()
        except ValueError:
            svc_dt = date.today()
        nxt_auto = svc_dt.replace(year=svc_dt.year + 1).strftime("%Y-%m-%d")

        if value == "Instalación":
            machines = [k for k, v in self.machines_dict.items() if v[2] == "En Stock"]
            clients = list(self.clients_dict.keys())
            self.client_combo.configure(values=clients if clients else [""])
            self.client_combo.set("")
            self._client_lbl.pack(anchor="w", pady=(0, 4))
            self.client_combo.pack(fill="x", pady=(0, SIZES["pad"]))
            # auto-sugerir próximo mantenimiento, editable
            self.next_maint.configure(state="normal")
            self.next_maint.delete(0, "end")
            self.next_maint.insert(0, nxt_auto)
        elif value == "Mantenimiento Preventivo":
            machines = [k for k, v in self.machines_dict.items() if v[2] == "Instalada"]
            self._client_lbl.pack_forget()
            self.client_combo.pack_forget()
            self.client_combo.set("")
            # auto-calcular próximo mantenimiento: fecha_servicio + 1 año
            self.next_maint.configure(state="normal")
            self.next_maint.delete(0, "end")
            self.next_maint.insert(0, nxt_auto)
        else:
            machines = [k for k, v in self.machines_dict.items() if v[2] == "Instalada"]
            self._client_lbl.pack_forget()
            self.client_combo.pack_forget()
            self.client_combo.set("")
            self.next_maint.configure(state="normal")
            self.next_maint.delete(0, "end")

        self.machine_combo.configure(values=machines if machines else [""])
        self.machine_combo.set("")

    # ── List ──────────────────────────────────────────────────────────────────

    def _build_list(self, parent):
        card = ctk.CTkFrame(parent, fg_color=UI_COLORS.CARD,
                            corner_radius=SIZES["card_radius"],
                            border_width=1, border_color=UI_COLORS.BORDER)
        card.grid(row=0, column=1, sticky="nsew", padx=(SIZES["pad"], 0))

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=SIZES["pad_large"],
                 pady=(SIZES["pad_large"], SIZES["pad_small"]))

        ctk.CTkLabel(hdr, text="Historial de Servicios",
                     font=ctk.CTkFont(size=_FS["large"], weight="bold"),
                     text_color=UI_COLORS.TEXT).pack(side="left")

        sw = ctk.CTkFrame(hdr, fg_color="#F8FAFC",
                          corner_radius=SIZES["button_radius"],
                          border_width=1, border_color=UI_COLORS.BORDER)
        sw.pack(side="right")
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *e: self.load_services())
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
        self.load_services()

    # ── Data ops ──────────────────────────────────────────────────────────────

    def load_reference_data(self):
        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)
        self.clients_dict.clear()
        for r in conn.execute("SELECT id, name FROM clients ORDER BY name"):
            self.clients_dict[r[1]] = r[0]
        # Carga máquinas reales (no desincorporadas) con serial + modelo + client_id + status
        for mid, serial, model_name, client_id, status in conn.execute("""
            SELECT m.id, m.serial_number, COALESCE(mo.model_name, '?'), m.client_id, m.status
            FROM machines m
            LEFT JOIN machine_models mo ON m.model_id = mo.id
            WHERE m.status != 'Desincorporada'
            ORDER BY m.serial_number
        """):
            label = f"{serial}  ({model_name})"
            self.machines_dict[label] = (mid, client_id, status)
        conn.close()

    @staticmethod
    def _load_stats():
        s = {"total": 0, "instalacion": 0, "mantenimiento": 0, "reparacion": 0}
        if not os.path.exists(DB_PATH):
            return s
        conn = sqlite3.connect(DB_PATH)
        s["total"]         = conn.execute("SELECT COUNT(*) FROM services").fetchone()[0]
        s["instalacion"]   = conn.execute(
            "SELECT COUNT(*) FROM services WHERE service_type='Instalación'").fetchone()[0]
        s["mantenimiento"] = conn.execute(
            "SELECT COUNT(*) FROM services WHERE service_type='Mantenimiento Preventivo'").fetchone()[0]
        s["reparacion"]    = conn.execute(
            "SELECT COUNT(*) FROM services WHERE service_type='Reparación'").fetchone()[0]
        conn.close()
        return s

    def add_service(self):
        stype   = self.type_combo.get()
        machine = self.machine_combo.get()
        svc_dt  = self.svc_date.get().strip()
        nxt     = self.next_maint.get().strip()
        remarks = self.remarks.get("1.0", "end").strip()

        if not stype or not machine or machine not in self.machines_dict:
            self.message.configure(text="⚠  Complete tipo y máquina",
                                   text_color=UI_COLORS.DANGER)
            return

        machine_id, client_id, m_status = self.machines_dict[machine]

        # Validar fecha servicio
        try:
            datetime.strptime(svc_dt, "%Y-%m-%d")
        except ValueError:
            self.message.configure(text="⚠  Fecha inválida (use YYYY-MM-DD)",
                                   text_color=UI_COLORS.DANGER)
            return

        # Validar fecha próximo mantenimiento si se proporcionó
        if nxt:
            try:
                datetime.strptime(nxt, "%Y-%m-%d")
            except ValueError:
                self.message.configure(text="⚠  Fecha próximo mantenimiento inválida (use YYYY-MM-DD)",
                                       text_color=UI_COLORS.DANGER)
                return

        # Validaciones por tipo de servicio
        if stype == "Instalación":
            selected_client = self.client_combo.get().strip()
            if not selected_client or selected_client not in self.clients_dict:
                self.message.configure(
                    text="⚠  Instalación requiere seleccionar un cliente",
                    text_color=UI_COLORS.DANGER)
                return
            if m_status != "En Stock":
                self.message.configure(
                    text="⚠  Solo máquinas 'En Stock' pueden instalarse",
                    text_color=UI_COLORS.DANGER)
                return
            new_client_id = self.clients_dict[selected_client]

        elif stype in ("Mantenimiento Preventivo", "Reparación"):
            if m_status != "Instalada":
                self.message.configure(
                    text=f"⚠  {stype} solo aplica a máquinas instaladas",
                    text_color=UI_COLORS.DANGER)
                return
            new_client_id = None
            new_status = "En Mantenimiento" if stype == "Mantenimiento Preventivo" else "En Reparación"

        else:
            new_client_id = None
            new_status = None

        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "INSERT INTO services (machine_id, service_type, service_date, next_maintenance_date, remarks, applied_by) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (machine_id, stype, svc_dt, nxt or None, remarks or None, self.username),
            )
            if stype == "Instalación":
                conn.execute(
                    "UPDATE machines SET status='Instalada', client_id=? WHERE id=?",
                    (new_client_id, machine_id))
                logger.info(f"Máquina {machine_id} → Instalada, cliente {new_client_id}")
            elif new_status:
                conn.execute("UPDATE machines SET status=? WHERE id=?", (new_status, machine_id))
                logger.info(f"Máquina {machine_id} → {new_status}")

            conn.commit()
            conn.close()
            self.type_combo.set("")
            self.machine_combo.set("")
            self.client_combo.set("")
            self._client_lbl.pack_forget()
            self.client_combo.pack_forget()
            self.next_maint.configure(state="normal")
            self.next_maint.delete(0, "end")
            self.remarks.delete("1.0", "end")
            self.message.configure(text="✓  Servicio registrado",
                                   text_color=UI_COLORS.GREEN)
            logger.info(f"Servicio registrado: {stype} — máquina {machine_id}")
            # Refrescar lista (máquinas instaladas desaparecen del combo)
            self.machines_dict.clear()
            self.load_reference_data()
            self.machine_combo.configure(values=list(self.machines_dict.keys()))
            self.load_services()
        except Exception as e:
            log_error("services_view", "add_service", e)
            self.message.configure(text="⚠  Error al registrar",
                                   text_color=UI_COLORS.DANGER)

    def load_services(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        conn = sqlite3.connect(DB_PATH)
        busq = self.search_var.get().strip().lower()
        wh, params = "", []
        if busq:
            wh = ("WHERE LOWER(s.service_type) LIKE ? OR LOWER(m.serial_number) LIKE ? "
                  "OR LOWER(mo.model_name) LIKE ? OR LOWER(c.name) LIKE ?")
            lk = f"%{busq}%"
            params = [lk, lk, lk, lk]

        rows = conn.execute(f"""
            SELECT s.id, s.service_type,
                   m.serial_number || '  (' || COALESCE(mo.model_name, '?') || ')',
                   s.service_date, s.next_maintenance_date,
                   c.name, s.remarks, s.machine_id, m.status, s.completion_date,
                   COALESCE(u.first_name || ' ' || u.last_name, s.applied_by, 'desconocido')
            FROM services s
            LEFT JOIN machines m ON s.machine_id = m.id
            LEFT JOIN machine_models mo ON m.model_id = mo.id
            LEFT JOIN clients c ON m.client_id = c.id
            LEFT JOIN users u ON s.applied_by = u.username
            {wh} ORDER BY s.service_date DESC
        """, params).fetchall()
        conn.close()

        if not rows:
            ctk.CTkLabel(self.scroll_frame, text="No hay servicios registrados",
                         font=ctk.CTkFont(size=_FS["body"]),
                         text_color=UI_COLORS.TEXT_MUTED).pack(pady=30)
            return
        for r in rows:
            self._service_card(r)

    def _service_card(self, row):
        sid, stype, machine, fdate, nxt, client_name, remarks, machine_id, m_status, completion_date, applied_by = row
        bg, fg, icon = _SVC_STYLE.get(stype, ("#F8FAFC", "#64748B", "📋"))

        card = ctk.CTkFrame(self.scroll_frame, fg_color=UI_COLORS.CARD,
                            corner_radius=SIZES["card_radius"],
                            border_width=1, border_color=UI_COLORS.BORDER)
        card.pack(fill="x", pady=5)

        c = ctk.CTkFrame(card, fg_color="transparent")
        c.pack(fill="both", expand=True, padx=SIZES["pad"], pady=SIZES["pad_small"])

        left = ctk.CTkFrame(c, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        # Badge tipo + fecha + estado del servicio
        top_row = ctk.CTkFrame(left, fg_color="transparent")
        top_row.pack(anchor="w", fill="x")
        badge = ctk.CTkFrame(top_row, fg_color=bg, corner_radius=SIZES["badge_radius"])
        badge.pack(side="left")
        ctk.CTkLabel(badge, text=f"{icon} {stype}",
                     font=ctk.CTkFont(size=_FS["tiny"], weight="bold"),
                     text_color=fg).pack(padx=10, pady=3)
        ctk.CTkLabel(top_row, text=f"📅 {fdate}",
                     font=ctk.CTkFont(size=_FS["tiny"]),
                     text_color=UI_COLORS.TEXT_MUTED).pack(side="left", padx=(10, 0))

        # Estado del servicio (solo para Mant./Rep.)
        if stype in ("Mantenimiento Preventivo", "Reparación"):
            if m_status in ("En Mantenimiento", "En Reparación"):
                s_bg, s_fg = "#FFFBEB", "#D97706"
                s_txt = "⏳ Pendiente"
            else:
                s_bg, s_fg = "#F0FDF4", "#16A34A"
                s_txt = f"✓ Listo — {completion_date}" if completion_date else "✓ Completado"
            sb = ctk.CTkFrame(top_row, fg_color=s_bg, corner_radius=SIZES["badge_radius"])
            sb.pack(side="left", padx=(8, 0))
            ctk.CTkLabel(sb, text=s_txt,
                         font=ctk.CTkFont(size=_FS["tiny"], weight="bold"),
                         text_color=s_fg).pack(padx=8, pady=3)

        # Máquina
        ctk.CTkLabel(left, text=machine or "Sin máquina",
                     font=ctk.CTkFont(size=_FS["body"], weight="bold"),
                     text_color=UI_COLORS.TEXT).pack(anchor="w", pady=(4, 0))

        # Cliente — siempre visible
        ctk.CTkLabel(left,
                     text=f"Cliente: {client_name}" if client_name else "Cliente: Sin asignar",
                     font=ctk.CTkFont(size=_FS["tiny"]),
                     text_color=UI_COLORS.TEXT_SECONDARY if client_name else UI_COLORS.TEXT_MUTED
                     ).pack(anchor="w", pady=(2, 0))

        # Aplicado por
        ctk.CTkLabel(left,
                     text=f"Aplicado por: {applied_by or 'desconocido'}",
                     font=ctk.CTkFont(size=_FS["tiny"]),
                     text_color=UI_COLORS.TEXT_MUTED
                     ).pack(anchor="w", pady=(1, 0))

        # Info crítica por tipo
        if stype == "Instalación" and nxt:
            nb = ctk.CTkFrame(left, fg_color="#EFF6FF", corner_radius=6)
            nb.pack(anchor="w", pady=(6, 0))
            ctk.CTkLabel(nb, text=f"Próximo mantenimiento: {nxt}",
                         font=ctk.CTkFont(size=_FS["tiny"], weight="bold"),
                         text_color="#2563EB").pack(padx=8, pady=3)

        elif stype == "Mantenimiento Preventivo" and nxt:
            nb = ctk.CTkFrame(left, fg_color="#F0FDF4", corner_radius=6)
            nb.pack(anchor="w", pady=(6, 0))
            ctk.CTkLabel(nb, text=f"Próximo mantenimiento: {nxt}",
                         font=ctk.CTkFont(size=_FS["tiny"], weight="bold"),
                         text_color="#16A34A").pack(padx=8, pady=3)

        elif stype == "Reparación" and remarks:
            nb = ctk.CTkFrame(left, fg_color="#FFFBEB", corner_radius=6)
            nb.pack(anchor="w", pady=(6, 0))
            ctk.CTkLabel(nb, text=f"Observaciones: {remarks[:80]}{'…' if len(remarks) > 80 else ''}",
                         font=ctk.CTkFont(size=_FS["tiny"]),
                         text_color="#92400E",
                         wraplength=320, justify="left").pack(padx=8, pady=3)

        btn_col = ctk.CTkFrame(c, fg_color="transparent")
        btn_col.pack(side="right", fill="y", anchor="center")

        # Completar servicio — visible si máquina sigue en estado activo de servicio
        if stype in ("Mantenimiento Preventivo", "Reparación") and m_status in ("En Mantenimiento", "En Reparación"):
            ctk.CTkButton(btn_col, text="✓",
                          command=lambda m=machine_id, s=sid: self.completar_servicio(m, s),
                          width=32, height=32, corner_radius=6,
                          fg_color="#F0FDF4", hover_color="#BBF7D0",
                          text_color="#16A34A",
                          font=ctk.CTkFont(size=_FS["body"], weight="bold"),
                          ).pack(pady=(0, 4))

        ctk.CTkButton(btn_col, text="🗑️",
                      command=lambda s=sid: self.eliminar_servicio(s),
                      width=32, height=32, corner_radius=6,
                      fg_color="#FEF2F2", hover_color="#FECACA",
                      text_color=UI_COLORS.DANGER,
                      font=ctk.CTkFont(size=_FS["body"])
                      ).pack()

    def completar_servicio(self, machine_id, service_id):
        try:
            today = date.today().strftime("%Y-%m-%d")
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE machines SET status='Instalada' WHERE id=?", (machine_id,))
            conn.execute("UPDATE services SET completion_date=? WHERE id=?", (today, service_id))
            conn.commit()
            conn.close()
            logger.info(f"Máquina {machine_id} → Instalada, servicio {service_id} completado {today}")
            self.machines_dict.clear()
            self.load_reference_data()
            self.machine_combo.configure(values=list(self.machines_dict.keys()))
            self.load_services()
        except Exception as e:
            log_error("services_view", "completar_servicio", e)
            self.message.configure(text="⚠  Error al completar servicio",
                                   text_color=UI_COLORS.DANGER)

    def eliminar_servicio(self, sid):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("DELETE FROM services WHERE id = ?", (sid,))
            conn.commit()
            conn.close()
            logger.info(f"Servicio eliminado: {sid}")
            self.load_services()
        except Exception as e:
            log_error("services_view", "eliminar_servicio", e)
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

    @staticmethod
    def _combo(parent, values):
        return ctk.CTkComboBox(parent, values=values,
                               height=SIZES["entry_height"],
                               corner_radius=SIZES["button_radius"],
                               state="readonly",
                               fg_color="#F8FAFC",
                               text_color=UI_COLORS.TEXT,
                               button_color=UI_COLORS.BORDER,
                               button_hover_color=UI_COLORS.PRIMARY,
                               dropdown_fg_color="white",
                               dropdown_text_color=UI_COLORS.TEXT,
                               border_color=UI_COLORS.BORDER)
