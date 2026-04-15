import customtkinter as ctk
from tkinter import ttk, filedialog
import sqlite3
import os
import openpyxl
from datetime import date, datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'inventario.db')

class ReportsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True)

        self.title = ctk.CTkLabel(self, text="Reportes y Alertas de Mantenimiento", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.pack(pady=(0, 20), anchor="w")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True)

        self.tab_stock = self.tabview.add("Inventario General")
        self.tab_alertas = self.tabview.add("Alertas de Mantenimiento")

        self.setup_stock_tab()
        self.setup_alertas_tab()

    def setup_stock_tab(self):
        tools_frame = ctk.CTkFrame(self.tab_stock, fg_color="transparent")
        tools_frame.pack(fill="x", pady=5)
        ctk.CTkButton(tools_frame, text="Exportar a Excel", command=self.export_stock, fg_color="#107c41", hover_color="#0b5e30").pack(side="left", padx=10)
        
        columns = ("N° Serial", "Modelo", "Distribuidor", "Estado", "Cliente Actual")
        self.tree_stock = ttk.Treeview(self.tab_stock, columns=columns, show="headings")
        for col in columns:
            self.tree_stock.heading(col, text=col)
            self.tree_stock.column(col, width=150, anchor="center")
            
        scrollbar = ttk.Scrollbar(self.tab_stock, orient="vertical", command=self.tree_stock.yview)
        self.tree_stock.configure(yscrollcommand=scrollbar.set)
        
        self.tree_stock.pack(side="left", fill="both", expand=True, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        self.load_stock()

    def load_stock(self):
        for item in self.tree_stock.get_children():
            self.tree_stock.delete(item)
            
        if not os.path.exists(DB_PATH): return
        conn = sqlite3.connect(DB_PATH)
        query = '''
            SELECT m.serial_number, mo.brand || ' ' || mo.model_name, d.name, m.status, IFNULL(c.name, 'N/A')
            FROM machines m
            LEFT JOIN machine_models mo ON m.model_id = mo.id
            LEFT JOIN distributors d ON m.distributor_id = d.id
            LEFT JOIN clients c ON m.client_id = c.id
        '''
        for row in conn.execute(query):
            self.tree_stock.insert("", "end", values=row)
        conn.close()

    def export_stock(self):
        self.export_treeview(self.tree_stock, "Reporte_Inventario")

    def setup_alertas_tab(self):
        tools_frame = ctk.CTkFrame(self.tab_alertas, fg_color="transparent")
        tools_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(tools_frame, text="Equipos que requieren mantenimiento en los próximos 30 días o están vencidos.", font=ctk.CTkFont(slant="italic")).pack(side="left", padx=10)
        ctk.CTkButton(tools_frame, text="Exportar a Excel", command=self.export_alerts, fg_color="#107c41", hover_color="#0b5e30").pack(side="right", padx=10)
        
        columns = ("Máquina (Serial)", "Cliente", "Teléfono", "Último Servicio", "Próximo Mantenimiento", "Estado")
        self.tree_alertas = ttk.Treeview(self.tab_alertas, columns=columns, show="headings")
        
        self.tree_alertas.heading("Máquina (Serial)", text="Serial")
        self.tree_alertas.column("Máquina (Serial)", width=120)
        self.tree_alertas.heading("Cliente", text="Cliente")
        self.tree_alertas.column("Cliente", width=180)
        self.tree_alertas.heading("Teléfono", text="Teléfono")
        self.tree_alertas.column("Teléfono", width=120)
        self.tree_alertas.heading("Último Servicio", text="Último Servicio")
        self.tree_alertas.column("Último Servicio", width=120)
        self.tree_alertas.heading("Próximo Mantenimiento", text="Próximo Mantenimiento")
        self.tree_alertas.column("Próximo Mantenimiento", width=150)
        self.tree_alertas.heading("Estado", text="Estado")
        self.tree_alertas.column("Estado", width=120)
        
        scrollbar = ttk.Scrollbar(self.tab_alertas, orient="vertical", command=self.tree_alertas.yview)
        self.tree_alertas.configure(yscrollcommand=scrollbar.set)
        
        self.tree_alertas.pack(side="left", fill="both", expand=True, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        self.load_alerts()

    def load_alerts(self):
        for item in self.tree_alertas.get_children():
            self.tree_alertas.delete(item)
            
        if not os.path.exists(DB_PATH): return
        conn = sqlite3.connect(DB_PATH)
        
        query = '''
            WITH LatestServices AS (
                SELECT machine_id, MAX(service_date) as last_date
                FROM services
                WHERE next_maintenance_date IS NOT NULL
                GROUP BY machine_id
            )
            SELECT m.serial_number, c.name, c.phone, s.service_date, s.next_maintenance_date
            FROM services s
            JOIN LatestServices ls ON s.machine_id = ls.machine_id AND s.service_date = ls.last_date
            JOIN machines m ON s.machine_id = m.id
            JOIN clients c ON m.client_id = c.id
        '''
        
        today = date.today()
        
        for row in conn.execute(query):
            next_maint_str = row[4]
            if not next_maint_str: continue
            
            try:
                next_maint = datetime.strptime(next_maint_str, "%Y-%m-%d").date()
                days_diff = (next_maint - today).days
                
                estado = ""
                if days_diff < 0:
                    estado = "VENCIDO"
                elif days_diff <= 30:
                    estado = "PRÓXIMO A VENCER"
                else:
                    continue
            except ValueError:
                continue
            
            self.tree_alertas.insert("", "end", values=(row[0], row[1], row[2], row[3], next_maint_str, estado))
        conn.close()

    def export_alerts(self):
        self.export_treeview(self.tree_alertas, "Alertas_Mantenimiento")

    def export_treeview(self, tree, filename_prefix):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                            initialfile=f"{filename_prefix}_{date.today().strftime('%Y%m%d')}.xlsx",
                                            title="Guardar como",
                                            filetypes=[("Excel files", "*.xlsx")])
        if not path:
            return
            
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Reporte"
        
        headers = [tree.heading(col)["text"] for col in tree["columns"]]
        ws.append(headers)
        
        for row_id in tree.get_children():
            row = tree.item(row_id)["values"]
            ws.append(row)
            
        wb.save(path)
