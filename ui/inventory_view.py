import customtkinter as ctk
from tkinter import ttk
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'inventario.db')

class InventoryView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True)

        self.title = ctk.CTkLabel(self, text="Gestión de Inventario (Máquinas Fiscales)", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.pack(pady=(0, 20), anchor="w")
        
        self.models_dict = {} # "Brand - Model": id
        self.distrib_dict = {} # "Name": id
        
        self.load_reference_data()
        self.setup_form()
        self.setup_table()
        self.load_machines()

    def load_reference_data(self):
        if not os.path.exists(DB_PATH): return
        conn = sqlite3.connect(DB_PATH)
        for row in conn.execute("SELECT id, brand, model_name FROM machine_models"):
            self.models_dict[f"{row[1]} - {row[2]}"] = row[0]
            
        for row in conn.execute("SELECT id, name FROM distributors"):
            self.distrib_dict[row[1]] = row[0]
        conn.close()

    def setup_form(self):
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(form_frame, text="N° Serial Fisico:").pack(side="left", padx=5)
        self.entry_serial = ctk.CTkEntry(form_frame, width=150)
        self.entry_serial.pack(side="left", padx=(0, 15))
        
        ctk.CTkLabel(form_frame, text="Modelo:").pack(side="left", padx=5)
        model_options = list(self.models_dict.keys())
        self.combo_model = ctk.CTkComboBox(form_frame, values=model_options if model_options else ["(No hay modelos)"], width=180)
        self.combo_model.pack(side="left", padx=(0, 15))
        
        ctk.CTkLabel(form_frame, text="Distribuidor:").pack(side="left", padx=5)
        distrib_options = list(self.distrib_dict.keys())
        self.combo_distrib = ctk.CTkComboBox(form_frame, values=distrib_options if distrib_options else ["(No hay distribuidores)"], width=180)
        self.combo_distrib.pack(side="left", padx=(0, 15))
        
        ctk.CTkButton(form_frame, text="Ingresar al Stock", command=self.add_machine).pack(side="left", padx=20)
        
        self.error_label = ctk.CTkLabel(form_frame, text="", text_color="red")
        self.error_label.pack(side="left", padx=5)

    def setup_table(self):
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, pady=10)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=30, borderwidth=0)
        style.configure("Treeview.Heading", font=('Helvetica', 11, 'bold'))

        columns = ("ID", "N° Serial", "Modelo", "Distribuidor", "Estado")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Anchos de columna
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=50, anchor="center")
        
        self.tree.heading("N° Serial", text="N° Serial")
        self.tree.column("N° Serial", width=150, anchor="center")
        
        self.tree.heading("Modelo", text="Modelo")
        self.tree.column("Modelo", width=200, anchor="center")
        
        self.tree.heading("Distribuidor", text="Distribuidor")
        self.tree.column("Distribuidor", width=150, anchor="center")
        
        self.tree.heading("Estado", text="Estado")
        self.tree.column("Estado", width=120, anchor="center")
            
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def add_machine(self):
        serial = self.entry_serial.get()
        model_str = self.combo_model.get()
        distrib_str = self.combo_distrib.get()
        
        if not serial or model_str not in self.models_dict or distrib_str not in self.distrib_dict:
            self.error_label.configure(text="Seleccione un modelo y distribuidor válidos.")
            return
            
        model_id = self.models_dict[model_str]
        distrib_id = self.distrib_dict[distrib_str]
        
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO machines (serial_number, model_id, distributor_id, status) VALUES (?, ?, ?, 'En Stock')",
                         (serial, model_id, distrib_id))
            conn.commit()
            conn.close()
            self.error_label.configure(text="")
            self.entry_serial.delete(0, 'end')
            self.load_machines()
        except sqlite3.IntegrityError:
            self.error_label.configure(text="El serial de esta máquina ya existe.")

    def load_machines(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not os.path.exists(DB_PATH): return
        conn = sqlite3.connect(DB_PATH)
        
        query = '''
            SELECT m.id, m.serial_number, mo.brand || ' - ' || mo.model_name, d.name, m.status 
            FROM machines m
            LEFT JOIN machine_models mo ON m.model_id = mo.id
            LEFT JOIN distributors d ON m.distributor_id = d.id
            ORDER BY m.id DESC
        '''
        
        for row in conn.execute(query):
            self.tree.insert("", "end", values=row)
        conn.close()
