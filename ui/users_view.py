import customtkinter as ctk
import sqlite3
import os
from database.db_manager import DB_PATH, hash_password
from theme import AppTheme, UI_COLORS, FONT_SIZES, SIZES
from utils.logger import logger, log_error

_FS = {k: round(v * 1.10) for k, v in FONT_SIZES.items()}

_ROLE_STYLE = {
    "admin": ("#EFF6FF", "#2563EB", "🔑 Admin"),
    "user":  ("#F0FDF4", "#16A34A", "👤 Usuario"),
}


class UsersView(ctk.CTkFrame):
    def __init__(self, master, user_info=None):
        super().__init__(master, fg_color=AppTheme.BACKGROUND)
        self.pack(fill="both", expand=True)
        self.current_uid = user_info[0] if user_info else None
        self.build_ui()

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
            ("Total Usuarios", stats["total"],  "#EFF6FF", "#2563EB", "👥"),
            ("Administradores", stats["admin"], "#FFFBEB", "#D97706", "🔑"),
            ("Usuarios",        stats["user"],  "#F0FDF4", "#16A34A", "👤"),
        ]
        for i, (label, value, bg, color, icon) in enumerate(data):
            card = ctk.CTkFrame(row, fg_color=UI_COLORS.CARD,
                                corner_radius=SIZES["card_radius"],
                                border_width=1, border_color=UI_COLORS.BORDER)
            card.grid(row=0, column=i,
                      padx=(0 if i == 0 else SIZES["pad_small"], 0), sticky="ew")
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

        ctk.CTkLabel(card, text="Nuevo Usuario",
                     font=ctk.CTkFont(size=_FS["large"], weight="bold"),
                     text_color=UI_COLORS.TEXT).pack(
            anchor="w", padx=SIZES["pad_large"],
            pady=(SIZES["pad_large"], SIZES["pad_small"]))

        ctk.CTkFrame(card, height=1, fg_color=UI_COLORS.BORDER_SUBTLE).pack(
            fill="x", padx=SIZES["pad_large"], pady=(0, SIZES["pad_small"]))

        fields = ctk.CTkScrollableFrame(card, fg_color="transparent",
                                        scrollbar_button_color=UI_COLORS.BORDER)
        fields.pack(fill="both", expand=True, padx=SIZES["pad_large"])

        self._lbl(fields, "Nombre *")
        self.first_name_entry = self._entry(fields, "Juan")
        self.first_name_entry.pack(fill="x", pady=(0, 2))
        self.err_first = self._err_lbl(fields)

        self._lbl(fields, "Apellido *")
        self.last_name_entry = self._entry(fields, "Pérez")
        self.last_name_entry.pack(fill="x", pady=(0, 2))
        self.err_last = self._err_lbl(fields)

        self._lbl(fields, "Nombre de usuario *")
        self.username_entry = self._entry(fields, "sin espacios ni símbolos")
        self.username_entry.pack(fill="x", pady=(0, 2))
        self.err_username = self._err_lbl(fields)

        self._lbl(fields, "Contraseña *")
        self.password_entry = self._entry(fields, "contraseña")
        self.password_entry.configure(show="•")
        self.password_entry.pack(fill="x", pady=(0, 2))
        self.err_password = self._err_lbl(fields)
        # Requisitos visibles siempre
        req = ctk.CTkFrame(fields, fg_color="#F8FAFC", corner_radius=6,
                           border_width=1, border_color=UI_COLORS.BORDER_SUBTLE)
        req.pack(fill="x", pady=(0, SIZES["pad"]))
        for txt in ("• Mínimo 6 caracteres",
                    "• Al menos 1 número"):
            ctk.CTkLabel(req, text=txt,
                         font=ctk.CTkFont(size=_FS["tiny"]),
                         text_color=UI_COLORS.TEXT_MUTED,
                         anchor="w").pack(anchor="w", padx=10, pady=1)
        ctk.CTkFrame(req, height=1).pack(pady=(0, 2))  # spacing

        self._lbl(fields, "Confirmar Contraseña *")
        self.confirm_entry = self._entry(fields, "repetir contraseña")
        self.confirm_entry.configure(show="•")
        self.confirm_entry.pack(fill="x", pady=(0, 2))
        self.err_confirm = self._err_lbl(fields)

        self._lbl(fields, "Rol")
        self.role_combo = ctk.CTkComboBox(
            fields, values=["user", "admin"],
            height=SIZES["entry_height"],
            corner_radius=SIZES["button_radius"],
            state="readonly",
            fg_color="#F8FAFC", text_color=UI_COLORS.TEXT,
            button_color=UI_COLORS.BORDER, button_hover_color=UI_COLORS.PRIMARY,
            dropdown_fg_color=UI_COLORS.CARD, dropdown_text_color=UI_COLORS.TEXT,
            border_color=UI_COLORS.BORDER)
        self.role_combo.set("user")
        self.role_combo.pack(fill="x", pady=(0, SIZES["pad_large"]))

        ctk.CTkButton(
            card, text="✓  Crear Usuario",
            command=self.add_user,
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

        ctk.CTkLabel(hdr, text="Usuarios del Sistema",
                     font=ctk.CTkFont(size=_FS["large"], weight="bold"),
                     text_color=UI_COLORS.TEXT).pack(side="left")

        self.count_label = ctk.CTkLabel(hdr, text="",
                                        font=ctk.CTkFont(size=_FS["small"]),
                                        text_color=UI_COLORS.TEXT_MUTED)
        self.count_label.pack(side="right")

        ctk.CTkFrame(card, height=1, fg_color=UI_COLORS.BORDER_SUBTLE).pack(
            fill="x", padx=SIZES["pad_large"], pady=(0, SIZES["pad_small"]))

        self.scroll_frame = ctk.CTkScrollableFrame(
            card, fg_color="transparent",
            scrollbar_button_color=UI_COLORS.BORDER)
        self.scroll_frame.pack(fill="both", expand=True,
                               padx=SIZES["pad_large"],
                               pady=(0, SIZES["pad_large"]))
        self.load_users()

    # ── Data ops ──────────────────────────────────────────────────────────────

    @staticmethod
    def _load_stats():
        s = {"total": 0, "admin": 0, "user": 0}
        if not os.path.exists(DB_PATH):
            return s
        conn = sqlite3.connect(DB_PATH)
        s["total"] = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        s["admin"] = conn.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0]
        s["user"]  = conn.execute("SELECT COUNT(*) FROM users WHERE role='user'").fetchone()[0]
        conn.close()
        return s

    def _field_err(self, entry, err_lbl, msg):
        entry.configure(border_color=UI_COLORS.DANGER)
        err_lbl.configure(text=f"⚠  {msg}")

    def _field_ok(self, entry, err_lbl):
        entry.configure(border_color=UI_COLORS.BORDER)
        err_lbl.configure(text="")

    def _clear_errors(self):
        for entry, lbl in [
            (self.first_name_entry, self.err_first),
            (self.last_name_entry,  self.err_last),
            (self.username_entry,   self.err_username),
            (self.password_entry,   self.err_password),
            (self.confirm_entry,    self.err_confirm),
        ]:
            self._field_ok(entry, lbl)
        self.message.configure(text="")

    def add_user(self):
        import re
        first_name = self.first_name_entry.get().strip()
        last_name  = self.last_name_entry.get().strip()
        username   = self.username_entry.get().strip()
        password   = self.password_entry.get()
        confirm    = self.confirm_entry.get()
        role       = self.role_combo.get()

        self._clear_errors()
        valid = True

        if not first_name:
            self._field_err(self.first_name_entry, self.err_first, "Obligatorio")
            valid = False
        elif not re.match(r"^[A-Za-záéíóúÁÉÍÓÚñÑ ]+$", first_name):
            self._field_err(self.first_name_entry, self.err_first, "Solo letras")
            valid = False

        if not last_name:
            self._field_err(self.last_name_entry, self.err_last, "Obligatorio")
            valid = False
        elif not re.match(r"^[A-Za-záéíóúÁÉÍÓÚñÑ ]+$", last_name):
            self._field_err(self.last_name_entry, self.err_last, "Solo letras")
            valid = False

        if not username:
            self._field_err(self.username_entry, self.err_username, "Obligatorio")
            valid = False
        elif not re.match(r"^[A-Za-z0-9_]+$", username):
            self._field_err(self.username_entry, self.err_username,
                            "Solo letras, números y _")
            valid = False

        pwd_errors = []
        if len(password) < 6:
            pwd_errors.append("mínimo 6 caracteres")
        if not re.search(r"[0-9]", password):
            pwd_errors.append("al menos 1 número")
        if pwd_errors:
            self._field_err(self.password_entry, self.err_password,
                            "Falta: " + ", ".join(pwd_errors))
            valid = False

        if password != confirm:
            self._field_err(self.confirm_entry, self.err_confirm,
                            "No coincide con la contraseña")
            valid = False

        if not valid:
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "INSERT INTO users (username, password, role, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
                (username, hash_password(password), role, first_name, last_name),
            )
            conn.commit()
            conn.close()
            for e in (self.first_name_entry, self.last_name_entry,
                      self.username_entry, self.password_entry, self.confirm_entry):
                e.delete(0, "end")
            self.role_combo.set("user")
            self._clear_errors()
            self.message.configure(text=f"✓  Usuario '{username}' creado",
                                   text_color=UI_COLORS.GREEN)
            logger.info(f"Usuario creado: {username} ({role})")
            self.load_users()
        except sqlite3.IntegrityError:
            self.message.configure(text="⚠  Nombre de usuario ya existe",
                                   text_color=UI_COLORS.DANGER)
        except Exception as e:
            log_error("users_view", "add_user", e)
            self.message.configure(text="⚠  Error interno",
                                   text_color=UI_COLORS.DANGER)

    def load_users(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT id, username, role, first_name, last_name FROM users ORDER BY role DESC, username"
        ).fetchall()
        conn.close()

        self.count_label.configure(
            text=f"{len(rows)} usuario{'s' if len(rows) != 1 else ''}")

        for r in rows:
            self._user_card(r)

    def _user_card(self, row):
        uid, username, role, first_name, last_name = row
        full_name = f"{first_name or ''} {last_name or ''}".strip() or username
        bg, fg, label = _ROLE_STYLE.get(role, ("#F8FAFC", "#64748B", f"👤 {role}"))
        is_self = (uid == self.current_uid)

        card = ctk.CTkFrame(self.scroll_frame, fg_color=UI_COLORS.CARD,
                            corner_radius=SIZES["card_radius"],
                            border_width=1, border_color=UI_COLORS.BORDER)
        card.pack(fill="x", pady=4)

        c = ctk.CTkFrame(card, fg_color="transparent")
        c.pack(fill="both", expand=True, padx=SIZES["pad"], pady=SIZES["pad_small"])

        # Avatar
        avatar = ctk.CTkFrame(c, width=40, height=40, fg_color=bg, corner_radius=20)
        avatar.pack(side="left")
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text=username[0].upper(),
                     font=ctk.CTkFont(size=_FS["medium"], weight="bold"),
                     text_color=fg).place(relx=0.5, rely=0.5, anchor="center")

        # Info
        info = ctk.CTkFrame(c, fg_color="transparent")
        info.pack(side="left", padx=(12, 0), fill="both", expand=True)

        top = ctk.CTkFrame(info, fg_color="transparent")
        top.pack(anchor="w", fill="x")
        ctk.CTkLabel(top, text=full_name,
                     font=ctk.CTkFont(size=_FS["body"], weight="bold"),
                     text_color=UI_COLORS.TEXT).pack(side="left")
        if is_self:
            ctk.CTkLabel(top, text="  (tú)",
                         font=ctk.CTkFont(size=_FS["tiny"]),
                         text_color=UI_COLORS.TEXT_MUTED).pack(side="left")

        ctk.CTkLabel(info, text=f"@{username}",
                     font=ctk.CTkFont(size=_FS["small"]),
                     text_color=UI_COLORS.TEXT_MUTED).pack(anchor="w", pady=(2, 0))

        role_badge = ctk.CTkFrame(info, fg_color=bg, corner_radius=SIZES["badge_radius"])
        role_badge.pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(role_badge, text=label,
                     font=ctk.CTkFont(size=_FS["tiny"], weight="bold"),
                     text_color=fg).pack(padx=8, pady=3)

        # Eliminar (no puede eliminarse a sí mismo)
        if not is_self:
            ctk.CTkButton(c, text="🗑️",
                          command=lambda u=uid, n=username: self.eliminar_usuario(u, n),
                          width=32, height=32, corner_radius=6,
                          fg_color=UI_COLORS.BADGE_BG["danger"],
                          hover_color="#FECACA",
                          text_color=UI_COLORS.DANGER,
                          font=ctk.CTkFont(size=_FS["body"]),
                          ).pack(side="right")

    def eliminar_usuario(self, uid, username):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("DELETE FROM users WHERE id=?", (uid,))
            conn.commit()
            conn.close()
            logger.info(f"Usuario eliminado: {username}")
            self.load_users()
        except Exception as e:
            log_error("users_view", "eliminar_usuario", e)
            self.message.configure(text="⚠  Error al eliminar",
                                   text_color=UI_COLORS.DANGER)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _lbl(parent, text):
        ctk.CTkLabel(parent, text=text,
                     font=ctk.CTkFont(size=_FS["small"], weight="bold"),
                     text_color=UI_COLORS.TEXT_SECONDARY).pack(anchor="w", pady=(0, 4))

    @staticmethod
    def _err_lbl(parent):
        lbl = ctk.CTkLabel(parent, text="",
                           font=ctk.CTkFont(size=_FS["tiny"]),
                           text_color=UI_COLORS.DANGER,
                           anchor="w")
        lbl.pack(anchor="w", pady=(0, SIZES["pad_small"]))
        return lbl

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
