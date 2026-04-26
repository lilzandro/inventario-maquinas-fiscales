import customtkinter as ctk
import sqlite3
import os
import openpyxl
from datetime import date, datetime
from tkinter import filedialog
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

class ReportsView(ctk.CTkFrame):
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
            text="📊 Reportes del Sistema",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=20)

        self.stats = ctk.CTkLabel(header, text="", font=ctk.CTkFont(size=12), text_color="#9CA3AF")
        self.stats.pack(side="right", padx=20)

        self.tabview = ctk.CTkTabview(
            self,
            fg_color=COLORS["card"],
            segmented_button_fg_color=COLORS["bg"],
            segmented_button_selected_color=COLORS["medium"],
            segmented_button_text_color=COLORS["gray"],
            segmented_button_selected_text_color="white"
        )
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        self.tab_inventory = self.tabview.add("📦 Inventario")
        self.tab_alerts = self.tabview.add("⚠️ Alertas")
        self.tab_summary = self.tabview.add("📈 Resumen")

        self.build_inventory()
        self.build_alerts()
        self.build_summary()

        self.update_stats()

    def build_inventory(self):
        bar = ctk.CTkFrame(self.tab_inventory, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            bar,
            text="Inventario General de Máquinas",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["dark"]
        ).pack(side="left")

        ctk.CTkButton(
            bar,
            text="📥 Exportar Excel",
            command=self.export_inventory,
            fg_color=COLORS["green"],
            hover_color="#059669",
            text_color="white",
            corner_radius=8,
            height=32
        ).pack(side="right")

        self.inv_frame = ctk.CTkScrollableFrame(self.tab_inventory, fg_color="transparent")
        self.inv_frame.pack(fill="both", expand=True, padx=20, pady=10)

        headers = ["Serial", "Modelo", "Distribuidor", "Estado", "Cliente"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                self.inv_frame, text=h,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["dark"]
            ).grid(row=0, column=i, padx=12, pady=8, sticky="w")

        self.inv_rows = []
        for i in range(1, 40):
            row = []
            for j in range(5):
                lbl = ctk.CTkLabel(self.inv_frame, text="", font=ctk.CTkFont(size=10), text_color=COLORS["gray"])
                lbl.grid(row=i, column=j, padx=12, pady=3, sticky="w")
                row.append(lbl)
            self.inv_rows.append(row)

        self.load_inventory()

    def load_inventory(self):
        for row in self.inv_rows:
            for lbl in row:
                lbl.configure(text="")

        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)
        query = '''
            SELECT m.serial_number, mo.brand || ' ' || mo.model_name, d.name, m.status, IFNULL(c.name, 'Sin asignar')
            FROM machines m
            LEFT JOIN machine_models mo ON m.model_id = mo.id
            LEFT JOIN distributors d ON m.distributor_id = d.id
            LEFT JOIN clients c ON m.client_id = c.id
            ORDER BY m.id DESC LIMIT 39
        '''
        for idx, row in enumerate(conn.execute(query)):
            for col, val in enumerate(row):
                self.inv_rows[idx][col].configure(text=str(val))
                if col == 3:
                    if val == "En Stock":
                        self.inv_rows[idx][col].configure(text_color=COLORS["blue"])
                    else:
                        self.inv_rows[idx][col].configure(text_color=COLORS["green"])
        conn.close()

    def export_inventory(self):
        if not os.path.exists(DB_PATH):
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=f"Inventario_{date.today().strftime('%Y%m%d')}.xlsx",
            filetypes=[("Excel", "*.xlsx")]
        )
        if not path:
            return

        conn = sqlite3.connect(DB_PATH)
        query = '''
            SELECT m.serial_number, mo.brand || ' ' || mo.model_name, d.name, m.status, IFNULL(c.name, 'Sin asignar')
            FROM machines m
            LEFT JOIN machine_models mo ON m.model_id = mo.id
            LEFT JOIN distributors d ON m.distributor_id = d.id
            LEFT JOIN clients c ON m.client_id = c.id
        '''
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Serial", "Modelo", "Distribuidor", "Estado", "Cliente"])
        for row in conn.execute(query):
            ws.append(row)
        conn.close()
        wb.save(path)

    def build_alerts(self):
        bar = ctk.CTkFrame(self.tab_alerts, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            bar,
            text="Alertas de Mantenimiento",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["dark"]
        ).pack(side="left")

        ctk.CTkButton(
            bar,
            text="📥 Exportar Excel",
            command=self.export_alerts,
            fg_color=COLORS["orange"],
            hover_color="#D97706",
            text_color="white",
            corner_radius=8,
            height=32
        ).pack(side="right")

        self.alert_frame = ctk.CTkScrollableFrame(self.tab_alerts, fg_color="transparent")
        self.alert_frame.pack(fill="both", expand=True, padx=20, pady=10)

        headers = ["Serial", "Cliente", "Teléfono", "Último Servicio", "Próximo Mant.", "Estado"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                self.alert_frame, text=h,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["dark"]
            ).grid(row=0, column=i, padx=10, pady=8, sticky="w")

        self.alert_rows = []
        for i in range(1, 25):
            row = []
            for j in range(6):
                lbl = ctk.CTkLabel(self.alert_frame, text="", font=ctk.CTkFont(size=10), text_color=COLORS["gray"])
                lbl.grid(row=i, column=j, padx=10, pady=3, sticky="w")
                row.append(lbl)
            self.alert_rows.append(row)

        self.load_alerts()

    def load_alerts(self):
        for row in self.alert_rows:
            for lbl in row:
                lbl.configure(text="")

        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)
        query = '''
            WITH LS AS (
                SELECT machine_id, MAX(service_date) as ld
                FROM services WHERE next_maintenance_date IS NOT NULL
                GROUP BY machine_id
            )
            SELECT m.serial_number, c.name, c.phone, s.service_date, s.next_maintenance_date
            FROM services s
            JOIN LS ON s.machine_id = LS.machine_id AND s.service_date = LS.ld
            JOIN machines m ON s.machine_id = m.id
            JOIN clients c ON m.client_id = c.id
        '''
        today = date.today()
        idx = 0
        for row in conn.execute(query):
            if idx >= len(self.alert_rows):
                break
            next_str = row[4]
            if not next_str:
                continue
            try:
                next_date = datetime.strptime(next_str, "%Y-%m-%d").date()
                days = (next_date - today).days
                if days < 0:
                    status = "VENCIDO"
                elif days <= 30:
                    status = "PRÓXIMO"
                else:
                    continue
            except:
                continue
            for col, val in enumerate(row):
                self.alert_rows[idx][col].configure(text=str(val))
            self.alert_rows[idx][5].configure(
                text=status,
                text_color=COLORS["red"] if status == "VENCIDO" else COLORS["orange"]
            )
            idx += 1
        conn.close()

    def export_alerts(self):
        if not os.path.exists(DB_PATH):
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=f"Alertas_{date.today().strftime('%Y%m%d')}.xlsx",
            filetypes=[("Excel", "*.xlsx")]
        )
        if not path:
            return

        conn = sqlite3.connect(DB_PATH)
        query = '''
            WITH LS AS (
                SELECT machine_id, MAX(service_date) as ld
                FROM services WHERE next_maintenance_date IS NOT NULL
                GROUP BY machine_id
            )
            SELECT m.serial_number, c.name, c.phone, s.service_date, s.next_maintenance_date
            FROM services s
            JOIN LS ON s.machine_id = LS.machine_id AND s.service_date = LS.ld
            JOIN machines m ON s.machine_id = m.id
            JOIN clients c ON m.client_id = c.id
        '''
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Serial", "Cliente", "Teléfono", "Último Servicio", "Próximo Mant.", "Estado"])
        today = date.today()
        for row in conn.execute(query):
            next_str = row[4]
            if not next_str:
                continue
            try:
                next_date = datetime.strptime(next_str, "%Y-%m-%d").date()
                days = (next_date - today).days
                if days < 0:
                    status = "VENCIDO"
                elif days <= 30:
                    status = "PRÓXIMO"
                else:
                    continue
            except:
                continue
            ws.append(list(row) + [status])
        conn.close()
        wb.save(path)

    def build_summary(self):
        stats = ctk.CTkFrame(self.tab_summary, fg_color="transparent")
        stats.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            stats,
            text="Resumen del Sistema",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["dark"]
        ).pack(anchor="w")

        cards = ctk.CTkFrame(stats, fg_color="transparent")
        cards.pack(fill="x", pady=15)

        self.summary_cards = {}
        items = [
            ("blue", "📦 Máquinas en Stock", "stock"),
            ("green", "🔧 Máquinas Instaladas", "installed"),
            ("gray", "👥 Clientes", "clients"),
            ("gold", "🔧 Total Servicios", "services"),
        ]
        for i, (color, label, key) in enumerate(items):
            card = ctk.CTkFrame(cards, fg_color=COLORS["card"], corner_radius=12)
            card.grid(row=0, column=i, padx=8, sticky="ew")
            cards.grid_columnconfigure(i, weight=1)

            ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["gray"]
            ).pack(pady=(15, 5))

            val = ctk.CTkLabel(
                card,
                text="0",
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color=COLORS[color]
            )
            val.pack(pady=(0, 15))
            self.summary_cards[key] = val

        self.load_summary()

    def load_summary(self):
        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)

        stock = conn.execute("SELECT COUNT(*) FROM machines WHERE status = 'En Stock'").fetchone()[0]
        installed = conn.execute("SELECT COUNT(*) FROM machines WHERE status = 'Instalada'").fetchone()[0]
        clients = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
        services = conn.execute("SELECT COUNT(*) FROM services").fetchone()[0]

        conn.close()

        self.summary_cards["stock"].configure(text=str(stock))
        self.summary_cards["installed"].configure(text=str(installed))
        self.summary_cards["clients"].configure(text=str(clients))
        self.summary_cards["services"].configure(text=str(services))

    def update_stats(self):
        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)
        total = conn.execute("SELECT COUNT(*) FROM machines").fetchone()[0]
        conn.close()
        self.stats.configure(text=f"{total} máquinas en sistema")