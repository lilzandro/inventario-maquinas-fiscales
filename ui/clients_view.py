import customtkinter as ctk
from tkinter import ttk
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'inventario.db')

class ClientsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True)

        self.title = ctk.CTkLabel(self, text="Gestión de Clientes", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.pack(pady=(0, 20), anchor="w")

        self.setup_form()
        self.setup_table()
        self.load_clients()

    def setup_form(self):
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(form_frame, text="Documento (RUT/CI):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.c_doc = ctk.CTkEntry(form_frame, width=150)
        self.c_doc.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(form_frame, text="Razón Social/Nombre:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.c_name = ctk.CTkEntry(form_frame, width=200)
        self.c_name.grid(row=0, column=3, padx=5, pady=5)
        
        ctk.CTkLabel(form_frame, text="Teléfono:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.c_phone = ctk.CTkEntry(form_frame, width=150)
        self.c_phone.grid(row=1, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(form_frame, text="Dirección:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.c_address = ctk.CTkEntry(form_frame, width=200)
        self.c_address.grid(row=1, column=3, padx=5, pady=5)
        
        ctk.CTkButton(form_frame, text="Registrar Cliente", command=self.add_client).grid(row=0, column=4, rowspan=2, padx=20, pady=5)
        
        self.error_label = ctk.CTkLabel(form_frame, text="", text_color="red")
        self.error_label.grid(row=2, column=0, columnspan=5, pady=5)

    def setup_table(self):
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, pady=10)

        columns = ("ID", "Documento", "Nombre", "Teléfono", "Dirección")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=50, anchor="center")
        self.tree.heading("Documento", text="Documento")
        self.tree.column("Documento", width=120, anchor="center")
        self.tree.heading("Nombre", text="Razón Social")
        self.tree.column("Nombre", width=250, anchor="w")
        self.tree.heading("Teléfono", text="Teléfono")
        self.tree.column("Teléfono", width=120, anchor="center")
        self.tree.heading("Dirección", text="Dirección")
        self.tree.column("Dirección", width=250, anchor="w")
            
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def add_client(self):
        doc = self.c_doc.get()
        name = self.c_name.get()
        phone = self.c_phone.get()
        addr = self.c_address.get()
        
        if not doc or not name:
            self.error_label.configure(text="Documento y Nombre son obligatorios.")
            return
            
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO clients (document_id, name, address, phone) VALUES (?, ?, ?, ?)",
                         (doc, name, addr, phone))
            conn.commit()
            conn.close()
            self.error_label.configure(text="")
            self.c_doc.delete(0, 'end')
            self.c_name.delete(0, 'end')
            self.c_phone.delete(0, 'end')
            self.c_address.delete(0, 'end')
            self.load_clients()
        except sqlite3.IntegrityError:
            self.error_label.configure(text="El documento de este cliente ya existe.")

    def load_clients(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not os.path.exists(DB_PATH): return
        conn = sqlite3.connect(DB_PATH)
        for row in conn.execute("SELECT id, document_id, name, phone, address FROM clients ORDER BY id DESC"):
            self.tree.insert("", "end", values=row)
        conn.close()
