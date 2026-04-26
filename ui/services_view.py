import customtkinter as ctk
import sqlite3
import os
from datetime import date, timedelta
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
    "orange": "#F59E0B",
}

class ServicesView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS["bg"])
        self.pack(fill="both", expand=True)

        self.clients_dict = {}
        self.machines_dict = {}
        self.load_data()
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color=COLORS["dark"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="🔧 Servicios y Mantenimientos",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=20)

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        form_card = ctk.CTkFrame(main, fg_color=COLORS["card"], corner_radius=16)
        form_card.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            form_card,
            text="Registrar Nuevo Servicio",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["dark"]
        ).pack(anchor="w", padx=25, pady=(20, 10))

        ctk.CTkFrame(form_card, height=1, fg_color="#E5E7EB").pack(fill="x", padx=25)

        fields = ctk.CTkFrame(form_card, fg_color="transparent")
        fields.pack(fill="x", padx=25, pady=20)

        col1 = ctk.CTkFrame(fields, fg_color="transparent")
        col1.pack(side="left", fill="both", expand=True, padx=(0, 15))

        ctk.CTkLabel(col1, text="Tipo de Servicio", font=ctk.CTkFont(size=12), text_color=COLORS["gray"]).pack(anchor="w")
        self.type_combo = ctk.CTkComboBox(
            col1,
            values=["Instalación", "Mantenimiento Preventivo", "Reparación"],
            width=250,
            corner_radius=8
        )
        self.type_combo.pack(anchor="w", pady=(5, 15))

        ctk.CTkLabel(col1, text="Máquina", font=ctk.CTkFont(size=12), text_color=COLORS["gray"]).pack(anchor="w")
        self.machine_combo = ctk.CTkComboBox(
            col1,
            values=list(self.machines_dict.keys()),
            width=250,
            corner_radius=8
        )
        self.machine_combo.pack(anchor="w", pady=(5, 15))

        col2 = ctk.CTkFrame(fields, fg_color="transparent")
        col2.pack(side="left", fill="both", expand=True, padx=(0, 15))

        ctk.CTkLabel(col2, text="Cliente", font=ctk.CTkFont(size=12), text_color=COLORS["gray"]).pack(anchor="w")
        self.client_combo = ctk.CTkComboBox(
            col2,
            values=list(self.clients_dict.keys()),
            width=250,
            corner_radius=8
        )
        self.client_combo.pack(anchor="w", pady=(5, 15))

        ctk.CTkLabel(fields, text="Observaciones", font=ctk.CTkFont(size=12), text_color=COLORS["gray"]).pack(anchor="w")
        self.remarks = ctk.CTkTextbox(fields, width=300, height=60, corner_radius=8)
        self.remarks.pack(anchor="w", pady=10)

        actions = ctk.CTkFrame(fields, fg_color="transparent")
        actions.pack(anchor="w", pady=10)

        ctk.CTkButton(
            actions,
            text="✓ Registrar Servicio",
            command=self.save_service,
            fg_color=COLORS["gold"],
            hover_color="#C78A32",
            text_color=COLORS["dark"],
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
            text="Historial de Servicios",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["dark"]
        ).pack(anchor="w", padx=25, pady=(20, 5))

        ctk.CTkFrame(table_card, height=1, fg_color="#E5E7EB").pack(fill="x", padx=25)

        self.table = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.table.pack(fill="both", expand=True, padx=20, pady=15)

        headers = ["ID", "Máquina", "Cliente", "Tipo", "Fecha", "Próximo Mant."]
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                self.table, text=h,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS["dark"]
            ).grid(row=0, column=i, padx=8, pady=8, sticky="w")

        self.rows = []
        for i in range(1, 30):
            row = []
            for j in range(6):
                lbl = ctk.CTkLabel(self.table, text="", font=ctk.CTkFont(size=10), text_color=COLORS["gray"])
                lbl.grid(row=i, column=j, padx=8, pady=3, sticky="w")
                row.append(lbl)
            self.rows.append(row)

        self.load_history()

    def load_data(self):
        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)
        for r in conn.execute("SELECT id, name FROM clients"):
            self.clients_dict[r[1]] = r[0]
        for r in conn.execute("SELECT id, serial_number, status FROM machines"):
            self.machines_dict[f"{r[1]} ({r[2]})"] = r[0]
        conn.close()

    def save_service(self):
        stype = self.type_combo.get()
        mstr = self.machine_combo.get()
        cstr = self.client_combo.get()
        remarks = self.remarks.get("1.0", "end-1c")

        if mstr not in self.machines_dict or cstr not in self.clients_dict:
            self.message.configure(text="⚠ Seleccione máquina y cliente válidos", text_color=COLORS["red"])
            return

        m_id = self.machines_dict[mstr]
        c_id = self.clients_dict[cstr]
        sdate = date.today().strftime("%Y-%m-%d")
        next_maint = None
        if stype in ["Instalación", "Mantenimiento Preventivo"]:
            next_maint = (date.today() + timedelta(days=365)).strftime("%Y-%m-%d")

        conn = sqlite3.connect(DB_PATH)
        if stype == "Instalación":
            conn.execute("UPDATE machines SET status='Instalada', client_id=? WHERE id=?", (c_id, m_id))
        conn.execute(
            "INSERT INTO services (machine_id, service_type, service_date, next_maintenance_date, remarks) VALUES (?, ?, ?, ?, ?)",
            (m_id, stype, sdate, next_maint, remarks)
        )
        conn.commit()
        conn.close()

        self.remarks.delete("1.0", "end")
        self.message.configure(text=f"✓ Servicio registrado. Próximo mantenimiento: {next_maint or 'N/A'}", text_color=COLORS["green"])
        self.load_history()
        self.load_data()

        opts = list(self.machines_dict.keys())
        self.machine_combo.configure(values=opts)
        if opts:
            self.machine_combo.set(opts[0])

    def load_history(self):
        for row in self.rows:
            for lbl in row:
                lbl.configure(text="")

        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)
        query = '''
            SELECT s.id, m.serial_number, c.name, s.service_type, s.service_date, IFNULL(s.next_maintenance_date, 'N/A')
            FROM services s
            JOIN machines m ON s.machine_id = m.id
            JOIN clients c ON m.client_id = c.id
            ORDER BY s.id DESC LIMIT 29
        '''
        type_colors = {
            "Instalación": COLORS["green"],
            "Mantenimiento Preventivo": COLORS["blue"],
            "Reparación": COLORS["red"],
        }

        for idx, row in enumerate(conn.execute(query)):
            for col, val in enumerate(row):
                self.rows[idx][col].configure(text=str(val))
            self.rows[idx][3].configure(text_color=type_colors.get(row[3], COLORS["gray"]))
        conn.close()