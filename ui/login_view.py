import customtkinter as ctk
import sqlite3
import os
from PIL import Image
from database.db_manager import verify_password, DB_PATH
from theme import AppTheme, UI_COLORS, FONT_SIZES, SIZES

_LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'img', 'logo-nombre.png')

_FS = {k: round(v * 1.15) for k, v in FONT_SIZES.items()}


class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color=UI_COLORS.BASE)
        self.master = master
        self.on_login_success = on_login_success
        self.pack(fill="both", expand=True)
        self.build_ui()

    def build_ui(self):
        # Grid centering: weight=1 on both axes centers the child widget
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(self, fg_color=UI_COLORS.CARD, corner_radius=SIZES["card_radius"])
        card.grid(row=0, column=0)

        self.build_side_decorative(card)
        self.build_form(card)

    def build_side_decorative(self, parent):
        side = ctk.CTkFrame(parent, fg_color=UI_COLORS.SIDEBAR, corner_radius=0, width=308)
        side.pack(side="left", fill="y")

        content = ctk.CTkFrame(side, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=35, pady=48)

        try:
            _pil = Image.open(_LOGO_PATH).convert("RGBA")
            _pil.putdata([(r, g, b, 0) if r > 230 and g > 230 and b > 230 else (r, g, b, a)
                          for r, g, b, a in _pil.getdata()])
            _logo_img = ctk.CTkImage(light_image=_pil, dark_image=_pil, size=(231, 121))
            logo_bg = ctk.CTkFrame(content, fg_color="#FFFFFF", corner_radius=10)
            logo_bg.pack(anchor="w", pady=(0, 4))
            ctk.CTkLabel(logo_bg, image=_logo_img, text="").pack(padx=8, pady=6)
        except Exception:
            ctk.CTkLabel(
                content, text="Adamo",
                font=ctk.CTkFont(size=_FS["xlarge"], weight="bold"),
                text_color=UI_COLORS.TEXT_ON_DARK,
            ).pack(anchor="w", pady=(20, 0))
            ctk.CTkLabel(
                content, text="Corporación Adamo Gentile C.A",
                font=ctk.CTkFont(size=_FS["body"]),
                text_color=UI_COLORS.SIDEBAR_TEXT,
            ).pack(anchor="w", pady=(6, 0))

        ctk.CTkFrame(content, height=1, fg_color="#2A3550").pack(fill="x", pady=28)

        features = [
            ("📦", "Inventario de máquinas"),
            ("👥", "Gestión de clientes"),
            ("🔧", "Historial de servicios"),
            ("📊", "Reportes en Excel"),
        ]
        for icon, text in features:
            row = ctk.CTkFrame(content, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=icon, font=ctk.CTkFont(size=14),
                         text_color=UI_COLORS.PRIMARY, width=24).pack(side="left")
            ctk.CTkLabel(row, text=text, font=ctk.CTkFont(size=_FS["small"]),
                         text_color=UI_COLORS.SIDEBAR_TEXT).pack(side="left", padx=(8, 0))

    def build_form(self, parent):
        form = ctk.CTkFrame(parent, fg_color=UI_COLORS.CARD, corner_radius=0, width=340)
        form.pack(side="left", fill="y")

        content = ctk.CTkFrame(form, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=36, pady=48)

        ctk.CTkLabel(
            content, text="Bienvenido",
            font=ctk.CTkFont(size=_FS["xxlarge"], weight="bold"),
            text_color=UI_COLORS.TEXT,
        ).pack(anchor="w")

        ctk.CTkLabel(
            content, text="Ingresa tus credenciales para continuar",
            font=ctk.CTkFont(size=_FS["small"]),
            text_color=UI_COLORS.TEXT_MUTED,
        ).pack(anchor="w", pady=(4, 28))

        ctk.CTkLabel(content, text="Usuario",
                     font=ctk.CTkFont(size=_FS["small"], weight="bold"),
                     text_color=UI_COLORS.TEXT_SECONDARY).pack(anchor="w")

        self.username_entry = ctk.CTkEntry(
            content,
            placeholder_text="Nombre de usuario",
            height=SIZES["entry_height"],
            corner_radius=SIZES["button_radius"],
            border_width=SIZES["border_width"],
            border_color=UI_COLORS.BORDER,
            fg_color="#F8FAFC",
            text_color=UI_COLORS.TEXT,
            placeholder_text_color=UI_COLORS.TEXT_MUTED,
            font=ctk.CTkFont(size=_FS["body"]),
        )
        self.username_entry.pack(fill="x", pady=(4, 16))

        ctk.CTkLabel(content, text="Contraseña",
                     font=ctk.CTkFont(size=_FS["small"], weight="bold"),
                     text_color=UI_COLORS.TEXT_SECONDARY).pack(anchor="w")

        self.password_entry = ctk.CTkEntry(
            content,
            placeholder_text="••••••••",
            show="*",
            height=SIZES["entry_height"],
            corner_radius=SIZES["button_radius"],
            border_width=SIZES["border_width"],
            border_color=UI_COLORS.BORDER,
            fg_color="#F8FAFC",
            text_color=UI_COLORS.TEXT,
            placeholder_text_color=UI_COLORS.TEXT_MUTED,
            font=ctk.CTkFont(size=_FS["body"]),
        )
        self.password_entry.pack(fill="x", pady=(4, 8))

        self.error_label = ctk.CTkLabel(
            content, text="",
            text_color=UI_COLORS.DANGER,
            font=ctk.CTkFont(size=_FS["tiny"]),
        )
        self.error_label.pack(anchor="w", pady=(0, 12))

        self.login_btn = ctk.CTkButton(
            content,
            text="Iniciar Sesión",
            command=self.attempt_login,
            height=SIZES["button_height"],
            corner_radius=SIZES["button_radius"],
            fg_color=UI_COLORS.PRIMARY,
            hover_color=UI_COLORS.SECONDARY,
            text_color="#ffffff",
            font=ctk.CTkFont(size=_FS["body"], weight="bold"),
        )
        self.login_btn.pack(fill="x")

        ctk.CTkLabel(
            content, text="🔒  Sistema seguro",
            font=ctk.CTkFont(size=_FS["tiny"]),
            text_color=UI_COLORS.TEXT_MUTED,
        ).pack(pady=(20, 0))

        self.master.bind("<Return>", lambda e: self.attempt_login())

    def attempt_login(self):
        user = self.username_entry.get().strip()
        pwd  = self.password_entry.get()

        if not user or not pwd:
            self.error_label.configure(text="Complete todos los campos")
            return

        if not os.path.exists(DB_PATH):
            self.error_label.configure(text="Base de datos no encontrada")
            return

        self.login_btn.configure(text="Verificando...", state="disabled")
        self.update()

        import time
        time.sleep(0.3)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (user,))
        user_row = cursor.fetchone()
        conn.close()

        self.login_btn.configure(text="Iniciar Sesión", state="normal")

        if user_row and verify_password(pwd, user_row[2]):
            self.error_label.configure(text="✓ Acceso concedido", text_color=UI_COLORS.GREEN)
            self.master.unbind("<Return>")
            self.on_login_success(user_row)
        else:
            self.password_entry.configure(border_color=UI_COLORS.DANGER)
            self.error_label.configure(text="Credenciales inválidas", text_color=UI_COLORS.DANGER)
            self.after(2000, lambda: self.password_entry.configure(border_color=UI_COLORS.BORDER))
