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

        # Buscador
        search_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        search_frame.pack(fill="x", padx=25, pady=(15, 10))

        search_box = ctk.CTkFrame(search_frame, fg_color="#F3F4F6", corner_radius=10)
        search_box.pack(side="left", fill="x", expand=True)

        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *e: self.load_clients())
        ctk.CTkEntry(search_box, textvariable=self.search_var, placeholder_text="🔍 Buscar por nombre, documento...", fg_color="transparent", border_width=0, corner_radius=10).pack(fill="x", padx=12, pady=8)

        ctk.CTkLabel(
            table_card,
            text="Clientes Registrados",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["dark"]
        ).pack(anchor="w", padx=25, pady=(15, 5))

        ctk.CTkFrame(table_card, height=1, fg_color="#E5E7EB").pack(fill="x", padx=25)

        self.table = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.table.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Header tabla
        header_frame = ctk.CTkFrame(self.table, fg_color="#F8FAFC", corner_radius=10)
        header_frame.pack(fill="x", pady=(0, 5))
        headers = [("Documento", 1), ("Nombre", 2), ("Teléfono", 1), ("Dirección", 2), ("Acciones", 1)]
        for i, (h, span) in enumerate(headers):
            f = ctk.CTkFrame(header_frame, fg_color="transparent")
            f.grid(row=0, column=i, sticky="ew", padx=5, pady=5)
            ctk.CTkLabel(f, text=h, font=ctk.CTkFont(size=10, weight="bold"), text_color="#6B7280").pack()
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=2)
        header_frame.grid_columnconfigure(2, weight=1)
        header_frame.grid_columnconfigure(3, weight=2)
        header_frame.grid_columnconfigure(4, weight=1)

        self.clients_list = ctk.CTkFrame(self.table, fg_color="transparent")
        self.clients_list.pack(fill="x")

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
        for w in self.clients_list.winfo_children():
            w.destroy()

        if not os.path.exists(DB_PATH):
            ctk.CTkLabel(self.clients_list, text="No hay clientes", text_color="#9CA3AF").pack(pady=20)
            self.count_label.configure(text="0 clientes")
            return

        conn = sqlite3.connect(DB_PATH)
        busq = self.search_var.get().strip().lower()

        where_clause = ""
        params = []
        if busq:
            where_clause = "WHERE LOWER(name) LIKE ? OR LOWER(document_id) LIKE ?"
            like = f"%{busq}%"
            params.extend([like, like])

        rows = conn.execute(f"SELECT id, document_id, name, phone, address FROM clients {where_clause} ORDER BY id DESC", params).fetchall()
        conn.close()

        if not rows:
            ctk.CTkLabel(self.clients_list, text="🔍 No se encontraron clientes", text_color="#9CA3AF").pack(pady=20)
            self.count_label.configure(text="0 clientes")
            return

        self.count_label.configure(text=f"{len(rows)} cliente{'s' if len(rows)!=1 else ''}")

        for r in rows:
            cid, doc, name, phone, addr = r
            row_fg = ctk.CTkFrame(self.clients_list, fg_color="#F8FAFC", corner_radius=10)
            row_fg.pack(fill="x", pady=4)
            row_fg.bind("<Enter>", lambda e, f=row_fg: f.configure(fg_color="#F1F5F9"))
            row_fg.bind("<Leave>", lambda e, f=row_fg: f.configure(fg_color="#F8FAFC"))

            row_frame = ctk.CTkFrame(row_fg, fg_color="transparent")
            row_frame.pack(fill="x", padx=10, pady=8)

            row_frame.grid_columnconfigure(0, weight=1)
            row_frame.grid_columnconfigure(1, weight=2)
            row_frame.grid_columnconfigure(2, weight=1)
            row_frame.grid_columnconfigure(3, weight=2)
            row_frame.grid_columnconfigure(4, weight=1)

            ctk.CTkLabel(row_frame, text=doc, font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["dark"]).grid(row=0, column=0, sticky="w", padx=5)
            ctk.CTkLabel(row_frame, text=name, font=ctk.CTkFont(size=11), text_color=COLORS["dark"]).grid(row=0, column=1, sticky="w", padx=5)
            ctk.CTkLabel(row_frame, text=phone, font=ctk.CTkFont(size=11), text_color=COLORS["gray"]).grid(row=0, column=2, sticky="w", padx=5)
            ctk.CTkLabel(row_frame, text=addr or "-", font=ctk.CTkFont(size=11), text_color=COLORS["gray"]).grid(row=0, column=3, sticky="w", padx=5)

            btn_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            btn_frame.grid(row=0, column=4, sticky="e", padx=5)
            ctk.CTkButton(btn_frame, text="✏️", width=30, height=24, corner_radius=6, font=ctk.CTkFont(size=11), command=lambda c=cid: self.edit_client(c), fg_color=COLORS["gold"], hover_color="#C78A32", text_color="white").pack(side="left", padx=2)
            ctk.CTkButton(btn_frame, text="🗑️", width=30, height=24, corner_radius=6, font=ctk.CTkFont(size=11), command=lambda c=cid, n=name: self.delete_client(c, n), fg_color="#EF4444", hover_color="#DC2626", text_color="white").pack(side="left", padx=2)

    def delete_client(self, cid, name):
        top = ctk.CTkToplevel(self)
        top.title("Confirmar eliminación")
        top.geometry("320x160")
        top.transient(self.master)
        top.grab_set()
        ctk.CTkLabel(top, text=f"¿Eliminar cliente?", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(16,4))
        ctk.CTkLabel(top, text=name, font=ctk.CTkFont(size=11), text_color="#6B7280").pack()
        ctk.CTkLabel(top, text="Esta acción no se puede deshacer", font=ctk.CTkFont(size=10), text_color="#EF4444").pack(pady=(4,12))
        btns = ctk.CTkFrame(top, fg_color="transparent")
        btns.pack()
        ctk.CTkButton(btns, text="Cancelar", command=top.destroy, width=80, corner_radius=6, fg_color="#6B7280", hover_color="#4B5563").pack(side="left", padx=4)
        ctk.CTkButton(btns, text="Eliminar", width=80, corner_radius=6, fg_color="#EF4444", hover_color="#DC2626", text_color="white", command=lambda: (self._do_delete_client(cid), top.destroy())).pack(side="left", padx=4)

    def _do_delete_client(self, cid):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("DELETE FROM clients WHERE id = ?", (cid,))
            conn.commit()
            conn.close()
            self.message.configure(text="✓ Cliente eliminado", text_color=COLORS["green"])
            self.load_clients()
        except Exception as e:
            self.message.configure(text=f"⚠ Error: {e}", text_color=COLORS["red"])

    def edit_client(self, cid):
        top = ctk.CTkToplevel(self)
        top.title("Editar Cliente")
        top.geometry("400x340")
        top.transient(self.master)
        top.grab_set()
        conn = sqlite3.connect(DB_PATH)
        r = conn.execute("SELECT document_id, name, phone, address FROM clients WHERE id = ?", (cid,)).fetchone()
        conn.close()
        if not r:
            return
        doc_o, name_o, phone_o, addr_o = r

        f = ctk.CTkFrame(top, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(f, text="Documento", font=ctk.CTkFont(size=11), text_color=COLORS["gray"]).pack(anchor="w")
        e_doc = ctk.CTkEntry(f, width=250, corner_radius=8)
        e_doc.insert(0, doc_o)
        e_doc.pack(fill="x", pady=(2,10))

        ctk.CTkLabel(f, text="Nombre/Razón Social", font=ctk.CTkFont(size=11), text_color=COLORS["gray"]).pack(anchor="w")
        e_name = ctk.CTkEntry(f, width=280, corner_radius=8)
        e_name.insert(0, name_o)
        e_name.pack(fill="x", pady=(2,10))

        ctk.CTkLabel(f, text="Teléfono", font=ctk.CTkFont(size=11), text_color=COLORS["gray"]).pack(anchor="w")
        e_phone = ctk.CTkEntry(f, width=200, corner_radius=8)
        e_phone.insert(0, phone_o or "")
        e_phone.pack(fill="x", pady=(2,10))

        ctk.CTkLabel(f, text="Dirección", font=ctk.CTkFont(size=11), text_color=COLORS["gray"]).pack(anchor="w")
        e_addr = ctk.CTkEntry(f, width=280, corner_radius=8)
        e_addr.insert(0, addr_o or "")
        e_addr.pack(fill="x", pady=(2,12))

        msg = ctk.CTkLabel(f, text="", font=ctk.CTkFont(size=11))
        msg.pack()

        def save():
            nd = e_doc.get().strip()
            nn = e_name.get().strip()
            np = e_phone.get().strip()
            na = e_addr.get().strip()
            if not nd or not nn:
                msg.configure(text="⚠ Complete campos requeridos", text_color=COLORS["red"])
                return
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("UPDATE clients SET document_id=?, name=?, phone=?, address=? WHERE id=?",
                             (nd, nn, np or None, na or None, cid))
                conn.commit()
                conn.close()
                top.destroy()
                self.message.configure(text="✓ Cliente actualizado", text_color=COLORS["green"])
                self.load_clients()
            except sqlite3.IntegrityError:
                msg.configure(text="⚠ Documento ya existe", text_color=COLORS["red"])

        ctk.CTkButton(f, text="Guardar cambios", command=save, fg_color=COLORS["medium"], hover_color=COLORS["dark"], text_color="white", corner_radius=8, height=36).pack(pady=4)