import customtkinter as ctk
from tkinter import ttk
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'inventario.db')

class CatalogsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True)

        self.title = ctk.CTkLabel(self, text="Gestión de Catálogos Base", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.pack(pady=(0, 20), anchor="w")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True)

        self.tab_distrib = self.tabview.add("Distribuidores")
        self.tab_modelos = self.tabview.add("Modelos")

        # Style Treeview para integrarlo visualmente
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=30, borderwidth=0)
        style.configure("Treeview.Heading", font=('Helvetica', 11, 'bold'))

        self.setup_distributors_tab()
        self.setup_models_tab()

    def setup_distributors_tab(self):
        # Form
        form_frame = ctk.CTkFrame(self.tab_distrib, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(form_frame, text="Nombre:").pack(side="left", padx=5)
        self.d_name = ctk.CTkEntry(form_frame, width=200)
        self.d_name.pack(side="left", padx=5)
        
        ctk.CTkLabel(form_frame, text="Contacto (Telf/Email):").pack(side="left", padx=5)
        self.d_contact = ctk.CTkEntry(form_frame, width=200)
        self.d_contact.pack(side="left", padx=5)
        
        ctk.CTkButton(form_frame, text="Agregar Distribuidor", command=self.add_distrib).pack(side="left", padx=20)
        
        # Table Scrollable
        table_frame = ctk.CTkFrame(self.tab_distrib)
        table_frame.pack(fill="both", expand=True, pady=10)

        columns = ("ID", "Nombre", "Contacto")
        self.tree_distrib = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree_distrib.heading(col, text=col)
            self.tree_distrib.column(col, width=150, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_distrib.yview)
        self.tree_distrib.configure(yscrollcommand=scrollbar.set)
        
        self.tree_distrib.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_distributors()

    def add_distrib(self):
        name = self.d_name.get()
        contact = self.d_contact.get()
        if not name: return
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO distributors (name, contact) VALUES (?, ?)", (name, contact))
        conn.commit()
        conn.close()
        self.d_name.delete(0, 'end')
        self.d_contact.delete(0, 'end')
        self.load_distributors()

    def load_distributors(self):
        for item in self.tree_distrib.get_children():
            self.tree_distrib.delete(item)
        if not os.path.exists(DB_PATH): return
        conn = sqlite3.connect(DB_PATH)
        for row in conn.execute("SELECT id, name, contact FROM distributors"):
            self.tree_distrib.insert("", "end", values=row)
        conn.close()

    def setup_models_tab(self):
        form_frame = ctk.CTkFrame(self.tab_modelos, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(form_frame, text="Marca:").pack(side="left", padx=5)
        self.m_brand = ctk.CTkEntry(form_frame, width=150)
        self.m_brand.pack(side="left", padx=5)
        
        ctk.CTkLabel(form_frame, text="Modelo:").pack(side="left", padx=5)
        self.m_model = ctk.CTkEntry(form_frame, width=150)
        self.m_model.pack(side="left", padx=5)
        
        ctk.CTkButton(form_frame, text="Agregar Modelo", command=self.add_model).pack(side="left", padx=20)
        
        table_frame = ctk.CTkFrame(self.tab_modelos)
        table_frame.pack(fill="both", expand=True, pady=10)

        columns = ("ID", "Marca", "Nombre del Modelo")
        self.tree_models = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree_models.heading(col, text=col)
            self.tree_models.column(col, width=150, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_models.yview)
        self.tree_models.configure(yscrollcommand=scrollbar.set)
        
        self.tree_models.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.load_models()

    def add_model(self):
        brand = self.m_brand.get()
        model_name = self.m_model.get()
        if not brand or not model_name: return
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO machine_models (brand, model_name) VALUES (?, ?)", (brand, model_name))
        conn.commit()
        conn.close()
        self.m_brand.delete(0, 'end')
        self.m_model.delete(0, 'end')
        self.load_models()

    def load_models(self):
        for item in self.tree_models.get_children():
            self.tree_models.delete(item)
        if not os.path.exists(DB_PATH): return
        conn = sqlite3.connect(DB_PATH)
        for row in conn.execute("SELECT id, brand, model_name FROM machine_models"):
            self.tree_models.insert("", "end", values=row)
        conn.close()
