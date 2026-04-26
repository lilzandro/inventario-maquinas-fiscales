import customtkinter as ctk
import sqlite3
import os
from database.db_manager import DB_PATH

COLORS = {
    "dark": "#010d23",
    "blue": "#038bbb",
    "gold": "#e19f41",
    "medium": "#03223f",
    "gray": "#6B7280",
    "green": "#10B981",
    "red": "#EF4444",
    "bg": "#F3F4F6",
    "card": "#FFFFFF",
}

class CatalogsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS["bg"])
        self.pack(fill="both", expand=True)

        self.tabview = ctk.CTkTabview(
            self,
            fg_color=COLORS["card"],
            segmented_button_fg_color=COLORS["medium"],
            segmented_button_selected_color=COLORS["blue"]
        )
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        self.tab_distrib = self.tabview.add("📦 Distribuidores")
        self.tab_model = self.tabview.add("🏷️ Modelos")

        self.build_distrib()
        self.build_model()

    def build_distrib(self):
        header = ctk.CTkFrame(self.tab_distrib, fg_color=COLORS["medium"], height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="Distribuidores",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=15)

        form = ctk.CTkFrame(self.tab_distrib, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=15)

        self.d_name = ctk.CTkEntry(form, width=280, placeholder_text="Nombre del distribuidor", corner_radius=8, border_color=COLORS["blue"])
        self.d_name.pack(side="left", padx=(0, 10))

        self.d_contact = ctk.CTkEntry(form, width=250, placeholder_text="Contacto (teléfono/email)", corner_radius=8, border_color=COLORS["blue"])
        self.d_contact.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            form,
            text="+ Agregar",
            command=self.add_distrib,
            fg_color=COLORS["blue"],
            hover_color="#027A9E",
            text_color="white",
            corner_radius=8,
            height=36
        ).pack(side="left", padx=10)

        self.d_msg = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=12))
        self.d_msg.pack(side="left")

        table = ctk.CTkFrame(self.tab_distrib, fg_color=COLORS["card"], corner_radius=12)
        table.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.d_frame = ctk.CTkScrollableFrame(table, fg_color="transparent")
        self.d_frame.pack(fill="both", expand=True, padx=15, pady=15)

        headers = ["ID", "Nombre", "Contacto", "Acciones"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                self.d_frame, text=h,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["dark"]
            ).grid(row=0, column=i, padx=12, pady=8, sticky="w")

        self.d_rows = []
        for i in range(1, 20):
            row = []
            for j in range(3):
                lbl = ctk.CTkLabel(self.d_frame, text="", font=ctk.CTkFont(size=11), text_color=COLORS["gray"])
                lbl.grid(row=i, column=j, padx=12, pady=4, sticky="w")
                row.append(lbl)
            btn = ctk.CTkButton(
                self.d_frame, text="🗑️",
                fg_color="transparent",
                text_color=COLORS["red"],
                width=40,
                height=24
            )
            btn.grid(row=i, column=3, padx=5, pady=2)
            row.append(btn)
            self.d_rows.append(row)

        self.load_distrib()

    def add_distrib(self):
        name = self.d_name.get()
        contact = self.d_contact.get()
        if not name:
            self.d_msg.configure(text="⚠ Ingrese nombre", text_color=COLORS["red"])
            return

        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO distributors (name, contact) VALUES (?, ?)", (name, contact))
        conn.commit()
        conn.close()
        self.d_name.delete(0, 'end')
        self.d_contact.delete(0, 'end')
        self.d_msg.configure(text="✓ Distribuidor agregado", text_color=COLORS["green"])
        self.load_distrib()

    def load_distrib(self):
        for row in self.d_rows:
            for lbl in row[:-1]:
                lbl.configure(text="")

        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)
        for idx, row in enumerate(conn.execute("SELECT id, name, contact FROM distributors LIMIT 19")):
            for col, val in enumerate(row):
                self.d_rows[idx][col].configure(text=str(val) if val else "-")
        conn.close()

    def build_model(self):
        header = ctk.CTkFrame(self.tab_model, fg_color=COLORS["medium"], height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="Modelos de Máquinas",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=15)

        form = ctk.CTkFrame(self.tab_model, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=15)

        self.m_brand = ctk.CTkEntry(form, width=200, placeholder_text="Marca", corner_radius=8, border_color=COLORS["gold"])
        self.m_brand.pack(side="left", padx=(0, 10))

        self.m_model = ctk.CTkEntry(form, width=300, placeholder_text="Nombre del modelo", corner_radius=8, border_color=COLORS["gold"])
        self.m_model.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            form,
            text="+ Agregar",
            command=self.add_model,
            fg_color=COLORS["gold"],
            hover_color="#C78A32",
            text_color=COLORS["dark"],
            corner_radius=8,
            height=36
        ).pack(side="left", padx=10)

        self.m_msg = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=12))
        self.m_msg.pack(side="left")

        table = ctk.CTkFrame(self.tab_model, fg_color=COLORS["card"], corner_radius=12)
        table.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.m_frame = ctk.CTkScrollableFrame(table, fg_color="transparent")
        self.m_frame.pack(fill="both", expand=True, padx=15, pady=15)

        headers = ["ID", "Marca", "Modelo"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                self.m_frame, text=h,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["dark"]
            ).grid(row=0, column=i, padx=15, pady=8, sticky="w")

        self.m_rows = []
        for i in range(1, 25):
            row = []
            for j in range(3):
                lbl = ctk.CTkLabel(self.m_frame, text="", font=ctk.CTkFont(size=11), text_color=COLORS["gray"])
                lbl.grid(row=i, column=j, padx=15, pady=4, sticky="w")
                row.append(lbl)
            self.m_rows.append(row)

        self.load_model()

    def add_model(self):
        brand = self.m_brand.get()
        model = self.m_model.get()
        if not brand or not model:
            self.m_msg.configure(text="⚠ Ingrese marca y modelo", text_color=COLORS["red"])
            return

        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO machine_models (brand, model_name) VALUES (?, ?)", (brand, model))
        conn.commit()
        conn.close()
        self.m_brand.delete(0, 'end')
        self.m_model.delete(0, 'end')
        self.m_msg.configure(text="✓ Modelo agregado", text_color=COLORS["green"])
        self.load_model()

    def load_model(self):
        for row in self.m_rows:
            for lbl in row:
                lbl.configure(text="")

        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)
        for idx, row in enumerate(conn.execute("SELECT id, brand, model_name FROM machine_models LIMIT 24")):
            for col, val in enumerate(row):
                self.m_rows[idx][col].configure(text=str(val))
        conn.close()