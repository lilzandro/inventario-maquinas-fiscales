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

class InventoryView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS["bg"])
        self.pack(fill="both", expand=True)

        self.models_dict = {}
        self.distrib_dict = {}
        self.load_reference_data()
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color=COLORS["dark"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="📦 Gestión de Inventario",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=20)

        ctk.CTkLabel(
            header,
            text=f"{len(self.models_dict)} modelos • {len(self.distrib_dict)} distribuidores",
            font=ctk.CTkFont(size=12),
            text_color="#9CA3AF"
        ).pack(side="right", padx=20)

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        form_card = ctk.CTkFrame(main, fg_color=COLORS["card"], corner_radius=16)
        form_card.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            form_card,
            text="Nueva Máquina",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["dark"]
        ).pack(anchor="w", padx=25, pady=(20, 10))

        ctk.CTkFrame(form_card, height=1, fg_color="#E5E7EB").pack(fill="x", padx=25)

        fields = ctk.CTkFrame(form_card, fg_color="transparent")
        fields.pack(fill="x", padx=25, pady=20)

        ctk.CTkLabel(fields, text="N° Serial", font=ctk.CTkFont(size=12), text_color=COLORS["gray"]).pack(anchor="w")
        self.serial = ctk.CTkEntry(fields, width=180, placeholder_text="Número de serie", corner_radius=8, border_color=COLORS["blue"])
        self.serial.pack(anchor="w", pady=(5, 15))

        ctk.CTkLabel(fields, text="Modelo", font=ctk.CTkFont(size=12), text_color=COLORS["gray"]).pack(anchor="w")
        self.model = ctk.CTkComboBox(fields, values=list(self.models_dict.keys()), width=250, corner_radius=8)
        self.model.pack(anchor="w", pady=(5, 15))

        ctk.CTkLabel(fields, text="Distribuidor", font=ctk.CTkFont(size=12), text_color=COLORS["gray"]).pack(anchor="w")
        self.distrib = ctk.CTkComboBox(fields, values=list(self.distrib_dict.keys()), width=200, corner_radius=8)
        self.distrib.pack(anchor="w", pady=(5, 15))

        actions = ctk.CTkFrame(fields, fg_color="transparent")
        actions.pack(anchor="w", pady=15)

        ctk.CTkButton(
            actions,
            text="✓ Agregar Máquina",
            command=self.add_machine,
            fg_color=COLORS["blue"],
            hover_color="#027A9E",
            text_color="white",
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8,
            height=40
        ).pack(side="left")

        self.message = ctk.CTkLabel(actions, text="", font=ctk.CTkFont(size=13))
        self.message.pack(side="left", padx=15)

        table_card = ctk.CTkFrame(main, fg_color=COLORS["card"], corner_radius=16)
        table_card.pack(fill="both", expand=True)

        ctk.CTkLabel(
            table_card,
            text="Inventario de Máquinas",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["dark"]
        ).pack(anchor="w", padx=25, pady=(20, 5))

        ctk.CTkLabel(
            table_card,
            text=f"Total: {self.count_machines()} máquinas",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["gray"]
        ).pack(anchor="w", padx=25, pady=(0, 10))

        ctk.CTkFrame(table_card, height=1, fg_color="#E5E7EB").pack(fill="x", padx=25)

        self.table = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.table.pack(fill="both", expand=True, padx=20, pady=15)

        headers = ["ID", "Serial", "Modelo", "Distribuidor", "Estado"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                self.table, text=h,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["dark"]
            ).grid(row=0, column=i, padx=10, pady=8, sticky="w")

        self.rows = []
        for i in range(1, 40):
            row = []
            for j in range(5):
                color = COLORS["gray"] if j > 0 else COLORS["dark"]
                lbl = ctk.CTkLabel(self.table, text="", font=ctk.CTkFont(size=11), text_color=color)
                lbl.grid(row=i, column=j, padx=10, pady=4, sticky="w")
                row.append(lbl)
            self.rows.append(row)

        self.load_machines()

    def load_reference_data(self):
        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)
        for r in conn.execute("SELECT id, brand, model_name FROM machine_models"):
            self.models_dict[f"{r[1]} - {r[2]}"] = r[0]
        for r in conn.execute("SELECT id, name FROM distributors"):
            self.distrib_dict[r[1]] = r[0]
        conn.close()

    def count_machines(self):
        if not os.path.exists(DB_PATH):
            return 0
        conn = sqlite3.connect(DB_PATH)
        c = conn.execute("SELECT COUNT(*) FROM machines").fetchone()[0]
        conn.close()
        return c

    def add_machine(self):
        serial = self.serial.get()
        model = self.model.get()
        distrib = self.distrib.get()

        if not serial or model not in self.models_dict or distrib not in self.distrib_dict:
            self.message.configure(text="⚠ Complete todos los campos", text_color=COLORS["red"])
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "INSERT INTO machines (serial_number, model_id, distributor_id, status) VALUES (?, ?, ?, 'En Stock')",
                (serial, self.models_dict[model], self.distrib_dict[distrib])
            )
            conn.commit()
            conn.close()
            self.serial.delete(0, 'end')
            self.message.configure(text="✓ Máquina registrada exitosamente", text_color=COLORS["green"])
            self.load_machines()
        except sqlite3.IntegrityError:
            self.message.configure(text="⚠ El serial ya existe", text_color=COLORS["red"])

    def load_machines(self):
        for row in self.rows:
            for lbl in row:
                lbl.configure(text="")

        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)
        query = '''
            SELECT m.id, m.serial_number, mo.brand || ' - ' || mo.model_name, d.name, m.status
            FROM machines m
            LEFT JOIN machine_models mo ON m.model_id = mo.id
            LEFT JOIN distributors d ON m.distributor_id = d.id
            ORDER BY m.id DESC LIMIT 39
        '''
        for idx, row in enumerate(conn.execute(query)):
            for col, val in enumerate(row):
                self.rows[idx][col].configure(text=str(val))
                if col == 4:
                    if val == "En Stock":
                        self.rows[idx][col].configure(text_color=COLORS["blue"])
                    elif val == "Instalada":
                        self.rows[idx][col].configure(text_color=COLORS["green"])
        conn.close()