import customtkinter as ctk
from tkinter import ttk
import sqlite3
import os
from datetime import date, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'inventario.db')

class ServicesView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True)

        self.title = ctk.CTkLabel(self, text="Gestión de Servicios y Mantenimientos", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.pack(pady=(0, 20), anchor="w")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True)

        self.tab_nuevo = self.tabview.add("Registrar Servicio / Instalación")
        self.tab_historial = self.tabview.add("Historial Ténico")
        
        self.clients_dict = {}
        self.machines_dict = {}
        
        self.setup_nuevo_tab()
        self.setup_historial_tab()
        
    def load_data(self):
        self.clients_dict.clear()
        self.machines_dict.clear()
        if not os.path.exists(DB_PATH): return
        conn = sqlite3.connect(DB_PATH)
        for row in conn.execute("SELECT id, name FROM clients"):
            self.clients_dict[row[1]] = row[0]
            
        for row in conn.execute("SELECT id, serial_number, status FROM machines"):
            # Para facilitar visualización
            self.machines_dict[f"{row[1]} ({row[2]})"] = row[0]
        conn.close()

    def setup_nuevo_tab(self):
        self.load_data()
        
        form_frame = ctk.CTkFrame(self.tab_nuevo, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, pady=10, padx=20)
        
        ctk.CTkLabel(form_frame, text="Tipo de Servicio:").grid(row=0, column=0, pady=10, sticky="w")
        self.combo_type = ctk.CTkComboBox(form_frame, values=["Instalación", "Mantenimiento Preventivo", "Reparación"], width=250)
        self.combo_type.grid(row=0, column=1, pady=10, padx=10)
        
        ctk.CTkLabel(form_frame, text="Máquina:").grid(row=1, column=0, pady=10, sticky="w")
        machines_opts = list(self.machines_dict.keys())
        self.combo_machine = ctk.CTkComboBox(form_frame, values=machines_opts if machines_opts else ["(Sin Máquinas)"], width=250)
        self.combo_machine.grid(row=1, column=1, pady=10, padx=10)
        
        ctk.CTkLabel(form_frame, text="Cliente:").grid(row=2, column=0, pady=10, sticky="w")
        clients_opts = list(self.clients_dict.keys())
        self.combo_client = ctk.CTkComboBox(form_frame, values=clients_opts if clients_opts else ["(Sin Clientes)"], width=250)
        self.combo_client.grid(row=2, column=1, pady=10, padx=10)
        
        ctk.CTkLabel(form_frame, text="Observaciones:").grid(row=3, column=0, pady=10, sticky="nw")
        self.txt_remarks = ctk.CTkTextbox(form_frame, width=350, height=80)
        self.txt_remarks.grid(row=3, column=1, pady=10, padx=10, columnspan=2, sticky="w")
        
        self.error_label = ctk.CTkLabel(form_frame, text="", text_color="red")
        self.error_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        ctk.CTkButton(form_frame, text="Procesar y Guardar", command=self.save_service).grid(row=5, column=0, columnspan=2, pady=20)

    def save_service(self):
        s_type = self.combo_type.get()
        m_str = self.combo_machine.get()
        c_str = self.combo_client.get()
        remarks = self.txt_remarks.get("1.0", "end-1c")
        
        if m_str not in self.machines_dict or c_str not in self.clients_dict:
            self.error_label.configure(text="Máquina o Cliente inválidos.", text_color="red")
            return
            
        m_id = self.machines_dict[m_str]
        c_id = self.clients_dict[c_str]
        
        # Logica fechas
        service_date = date.today().strftime("%Y-%m-%d")
        next_maint = None
        if s_type in ["Instalación", "Mantenimiento Preventivo"]:
            next_maint = (date.today() + timedelta(days=365)).strftime("%Y-%m-%d")
            
        conn = sqlite3.connect(DB_PATH)
        # Update machine si es instalación o para asegurar su enlace al cliente actual
        if s_type == "Instalación":
            # Cambia a instalada y la enlaza al cliente
            conn.execute("UPDATE machines SET status='Instalada', client_id=? WHERE id=?", (c_id, m_id))
            
        # Register history
        conn.execute("INSERT INTO services (machine_id, service_type, service_date, next_maintenance_date, remarks) VALUES (?, ?, ?, ?, ?)",
                     (m_id, s_type, service_date, next_maint, remarks))
        conn.commit()
        conn.close()
        
        self.error_label.configure(text=f"Registrado con éxito. Próx Mantenimiento: {next_maint or 'N/A'}", text_color="green")
        self.txt_remarks.delete("1.0", "end")
        
        self.load_data()
        updated_opts = list(self.machines_dict.keys())
        self.combo_machine.configure(values=updated_opts)
        if updated_opts:
            self.combo_machine.set(updated_opts[0])
            
        self.load_history()

    def setup_historial_tab(self):
        columns = ("ID", "Máquina (Serial)", "Cliente", "Tipo Servicio", "Fecha", "Próximo Mantenimiento")
        self.tree = ttk.Treeview(self.tab_historial, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
            
        self.tree.column("Cliente", width=220, anchor="w")
        self.tree.column("Próximo Mantenimiento", width=180, anchor="center")
            
        scrollbar = ttk.Scrollbar(self.tab_historial, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        self.load_history()

    def load_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not os.path.exists(DB_PATH): return
        conn = sqlite3.connect(DB_PATH)
        query = '''
            SELECT s.id, m.serial_number, c.name, s.service_type, s.service_date, IFNULL(s.next_maintenance_date, 'N/A')
            FROM services s
            JOIN machines m ON s.machine_id = m.id
            JOIN clients c ON m.client_id = c.id
            ORDER BY s.id DESC
        '''
        for row in conn.execute(query):
            self.tree.insert("", "end", values=row)
        conn.close()
