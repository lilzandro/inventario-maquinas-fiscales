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
    "purple": "#8B5CF6",
}

class ClientsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS["bg"])
        self.pack(fill="both", expand=True)
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color=COLORS["dark"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="👥 Gestión de Clientes",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=20)

        self.count_label = ctk.CTkLabel(
            header,
            text="0 clientes",
            font=ctk.CTkFont(size=12),
            text_color="#9CA3AF"
        )
        self.count_label.pack(side="right", padx=20)

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        form_card = ctk.CTkFrame(main, fg_color=COLORS["card"], corner_radius=16)
        form_card.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            form_card,
            text="Nuevo Cliente",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["dark"]
        ).pack(anchor="w", padx=25, pady=(20, 10))

        ctk.CTkFrame(form_card, height=1, fg_color="#E5E7EB").pack(fill="x", padx=25)

        fields = ctk.CTkFrame(form_card, fg_color="transparent")
        fields.pack(fill="x", padx=25, pady=20)

        col1 = ctk.CTkFrame(fields, fg_color="transparent")
        col1.pack(side="left", fill="both", expand=True, padx=(0, 20))

        ctk.CTkLabel(col1, text="Documento (RUT/CI)", font=ctk.CTkFont(size=12), text_color=COLORS["gray"]).pack(anchor="w")
        self.doc = ctk.CTkEntry(col1, width=200, placeholder_text="12345678-9", corner_radius=8, border_color=COLORS["purple"])
        self.doc.pack(anchor="w", pady=(5, 15))

        ctk.CTkLabel(col1, text="Razón Social / Nombre", font=ctk.CTkFont(size=12), text_color=COLORS["gray"]).pack(anchor="w")
        self.name = ctk.CTkEntry(col1, width=280, placeholder_text="Nombre del cliente", corner_radius=8, border_color=COLORS["purple"])
        self.name.pack(anchor="w", pady=(5, 15))

        col2 = ctk.CTkFrame(fields, fg_color="transparent")
        col2.pack(side="left", fill="both", expand=True, padx=(0, 20))

        ctk.CTkLabel(col2, text="Teléfono", font=ctk.CTkFont(size=12), text_color=COLORS["gray"]).pack(anchor="w")
        self.phone = ctk.CTkEntry(col2, width=180, placeholder_text="0999 XXX XXX", corner_radius=8, border_color=COLORS["purple"])
        self.phone.pack(anchor="w", pady=(5, 15))

        ctk.CTkLabel(col2, text="Dirección", font=ctk.CTkFont(size=12), text_color=COLORS["gray"]).pack(anchor="w")
        self.address = ctk.CTkEntry(col2, width=250, placeholder_text="Dirección completa", corner_radius=8, border_color=COLORS["purple"])
        self.address.pack(anchor="w", pady=(5, 15))

        actions = ctk.CTkFrame(fields, fg_color="transparent")
        actions.pack(side="left", fill="both", expand=True)

        ctk.CTkButton(
            actions,
            text="✓ Registrar Cliente",
            command=self.add_client,
            fg_color=COLORS["medium"],
            hover_color=COLORS["dark"],
            text_color="white",
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8,
            height=40
        ).pack(anchor="w", pady=30)

        self.message = ctk.CTkLabel(actions, text="", font=ctk.CTkFont(size=13))
        self.message.pack(anchor="w", pady=(5, 0))

        table_card = ctk.CTkFrame(main, fg_color=COLORS["card"], corner_radius=16)
        table_card.pack(fill="both", expand=True)

        ctk.CTkLabel(
            table_card,
            text="Clientes Registrados",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["dark"]
        ).pack(anchor="w", padx=25, pady=(20, 5))

        ctk.CTkFrame(table_card, height=1, fg_color="#E5E7EB").pack(fill="x", padx=25)

        self.table = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.table.pack(fill="both", expand=True, padx=20, pady=15)

        headers = ["ID", "Documento", "Nombre", "Teléfono", "Dirección"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                self.table, text=h,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["dark"]
            ).grid(row=0, column=i, padx=10, pady=8, sticky="w")

        self.rows = []
        for i in range(1, 35):
            row = []
            for j in range(5):
                lbl = ctk.CTkLabel(self.table, text="", font=ctk.CTkFont(size=11), text_color=COLORS["gray"])
                lbl.grid(row=i, column=j, padx=10, pady=4, sticky="w")
                row.append(lbl)
            self.rows.append(row)

        self.load_clients()

    def add_client(self):
        doc = self.doc.get()
        name = self.name.get()
        phone = self.phone.get()
        address = self.address.get()

        if not doc or not name:
            self.message.configure(text="⚠ Documento y nombre son obligatorios", text_color=COLORS["red"])
            return

        # Validación formato RUT básico (X.XXX.XXX-X o similar)
        doc_clean = doc.replace(".", "").replace("-", "").strip()
        if len(doc_clean) < 7:
            self.message.configure(text="⚠ Documento inválido (mínimo 7 dígitos)", text_color=COLORS["red"])
            return

        # Validación básica de teléfono
        if phone:
            phone_clean = phone.replace(" ", "").replace("-", "").replace("+", "")
            if not phone_clean.isdigit() or len(phone_clean) < 7:
                self.message.configure(text="⚠ Teléfono inválido", text_color=COLORS["red"])
                return

        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "INSERT INTO clients (document_id, name, address, phone) VALUES (?, ?, ?, ?)",
                (doc, name, address, phone)
            )
            conn.commit()
            conn.close()
            self.message.configure(text="✓ Cliente registrado exitosamente", text_color=COLORS["green"])
            self.doc.delete(0, 'end')
            self.name.delete(0, 'end')
            self.phone.delete(0, 'end')
            self.address.delete(0, 'end')
            self.load_clients()
        except sqlite3.IntegrityError:
            self.message.configure(text="⚠ El documento ya existe en el sistema", text_color=COLORS["red"])

    def load_clients(self):
        for row in self.rows:
            for lbl in row:
                lbl.configure(text="")

        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)
        count = 0
        for idx, row in enumerate(conn.execute("SELECT id, document_id, name, phone, address FROM clients ORDER BY id DESC LIMIT 34")):
            count += 1
            for col, val in enumerate(row):
                self.rows[idx][col].configure(text=str(val) if val else "-")
        conn.close()
        self.count_label.configure(text=f"{count} clientes")