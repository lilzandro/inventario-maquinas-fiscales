import customtkinter as ctk
import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "inventario.db"
)

COLORS = {
    "dark_blue": "#1A3263",
    "gold": "#FAB95B",
    "bg_gray": "#F5F5F5",
    "white": "#FFFFFF",
    "text_dark": "#1A3263",
    "text_light": "#FFFFFF",
    "text_gray": "#6B7280",
    "card_bg": "#FFFFFF",
    "hover": "#456282",
}


class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color=COLORS["bg_gray"])
        self.master = master
        self.on_login_success = on_login_success

        self.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        login_card = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=15)
        login_card.pack(padx=40, pady=40)

        title_label = ctk.CTkLabel(
            login_card,
            text="🔐 Sistema de Gestión",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["dark_blue"],
        )
        title_label.pack(pady=(20, 30))

        subtitle = ctk.CTkLabel(
            login_card,
            text="Máquinas Fiscales",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_gray"],
        )
        subtitle.pack(pady=(0, 25))

        self.username_entry = ctk.CTkEntry(
            login_card,
            placeholder_text="Usuario",
            width=280,
            height=45,
            corner_radius=8,
            border_color=COLORS["dark_blue"],
            fg_color=COLORS["card_bg"],
        )
        self.username_entry.pack(pady=8)

        self.password_entry = ctk.CTkEntry(
            login_card,
            placeholder_text="Contraseña",
            show="*",
            width=280,
            height=45,
            corner_radius=8,
            border_color=COLORS["dark_blue"],
            fg_color=COLORS["card_bg"],
        )
        self.password_entry.pack(pady=8)

        self.error_label = ctk.CTkLabel(
            login_card, text="", text_color="#DC2626", font=ctk.CTkFont(size=12)
        )
        self.error_label.pack(pady=5)

        self.login_btn = ctk.CTkButton(
            login_card,
            text="Iniciar Sesión",
            command=self.attempt_login,
            width=280,
            height=45,
            corner_radius=8,
            fg_color=COLORS["dark_blue"],
            hover_color=COLORS["dark_blue"],
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.login_btn.pack(pady=(10, 25))

        self.master.bind("<Return>", lambda event: self.attempt_login())

    def attempt_login(self):
        user = self.username_entry.get()
        pwd = self.password_entry.get()

        if not user or not pwd:
            self.error_label.configure(text="Complete todos los campos")
            return

        if not os.path.exists(DB_PATH):
            self.error_label.configure(text="Base de datos no encontrada.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?", (user, pwd)
        )
        user_row = cursor.fetchone()
        conn.close()

        if user_row:
            self.error_label.configure(text="")
            self.master.unbind("<Return>")
            self.on_login_success(user_row)
        else:
            self.error_label.configure(text="Credenciales inválidas")
