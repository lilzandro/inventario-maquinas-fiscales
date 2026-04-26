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

        row1 = ctk.CTkFrame(fields, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(row1, text="N° Serial", font=ctk.CTkFont(size=12), text_color=COLORS["gray"]).pack(anchor="w")
        self.serial = ctk.CTkEntry(row1, width=180, placeholder_text="Número de serie", corner_radius=8, border_color=COLORS["blue"])
        self.serial.pack(anchor="w", pady=(4, 0))

        row2 = ctk.CTkFrame(fields, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(row2, text="Modelo", font=ctk.CTkFont(size=12), text_color=COLORS["gray"]).pack(anchor="w")
        self.model = ctk.CTkComboBox(row2, values=list(self.models_dict.keys()), width=250, corner_radius=8)
        self.model.pack(anchor="w", pady=(4, 0))

        row3 = ctk.CTkFrame(fields, fg_color="transparent")
        row3.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(row3, text="Distribuidor", font=ctk.CTkFont(size=12), text_color=COLORS["gray"]).pack(anchor="w")
        self.distrib = ctk.CTkComboBox(row3, values=list(self.distrib_dict.keys()), width=200, corner_radius=8)
        self.distrib.pack(anchor="w", pady=(4, 0))

        row4 = ctk.CTkFrame(fields, fg_color="transparent")
        row4.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(row4, text="Estado", font=ctk.CTkFont(size=12), text_color=COLORS["gray"]).pack(anchor="w")
        self.estado = ctk.CTkComboBox(row4, values=["En Stock", "Instalada", "Desincorporada"], width=200, corner_radius=8)
        self.estado.set("En Stock")
        self.estado.pack(anchor="w", pady=(4, 0))

        actions = ctk.CTkFrame(fields, fg_color="transparent")
        actions.pack(anchor="w", pady=15)

        ctk.CTkButton(
            actions,
            text="✚ Agregar Máquina",
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

        # Buscador y filtros
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
        # Limpia lista
        for w in self.machines_list.winfo_children():
            w.destroy()

        if not os.path.exists(DB_PATH):
            ctk.CTkLabel(self.machines_list, text="No hay máquinas registradas", text_color="#9CA3AF").pack(pady=20)
            return

        conn = sqlite3.connect(DB_PATH)

        # Construye WHERE para búsqueda y filtro
        busq = self.search_var.get().strip().lower()
        filtro = self.filter_var.get()

        where_parts = []
        params = []

        if busq:
            where_parts.append("(LOWER(m.serial_number) LIKE ? OR LOWER(mo.brand) LIKE ? OR LOWER(mo.model_name) LIKE ? OR LOWER(d.name) LIKE ? OR LOWER(m.client_id) LIKE ?)")
            like = f"%{busq}%"
            params.extend([like, like, like, like, like])

        if filtro != "TODOS":
            where_parts.append("m.status = ?")
            params.append(filtro)

        where_clause = "WHERE " + " AND ".join(where_parts) if where_parts else ""

        query = f'''
            SELECT m.id, m.serial_number, mo.brand || ' - ' || mo.model_name, COALESCE(d.name, '-'), COALESCE(c.name, '-'), m.status
            FROM machines m
            LEFT JOIN machine_models mo ON m.model_id = mo.id
            LEFT JOIN distributors d ON m.distributor_id = d.id
            LEFT JOIN clients c ON m.client_id = c.id
            {where_clause}
            ORDER BY m.id DESC
        '''

        rows = conn.execute(query, params).fetchall()
        conn.close()

        if not rows:
            ctk.CTkLabel(self.machines_list, text="🔍 No se encontraron máquinas", text_color="#9CA3AF").pack(pady=20)
            return

        status_colors = {"En Stock": COLORS["blue"], "Instalada": COLORS["green"], "Desincorporada": COLORS["red"]}

        for r in rows:
            mid, serial, modelo, distrib, cliente, estado = r
            row_fg = ctk.CTkFrame(self.machines_list, fg_color="#F8FAFC", corner_radius=10)
            row_fg.pack(fill="x", pady=4)
            row_fg.bind("<Enter>", lambda e, f=row_fg: f.configure(fg_color="#F1F5F9"))
            row_fg.bind("<Leave>", lambda e, f=row_fg: f.configure(fg_color="#F8FAFC"))

            row_frame = ctk.CTkFrame(row_fg, fg_color="transparent")
            row_frame.pack(fill="x", padx=10, pady=8)

            row_frame.grid_columnconfigure(0, weight=2)
            row_frame.grid_columnconfigure(1, weight=2)
            row_frame.grid_columnconfigure(2, weight=2)
            row_frame.grid_columnconfigure(3, weight=2)
            row_frame.grid_columnconfigure(4, weight=1)
            row_frame.grid_columnconfigure(5, weight=1)

            ctk.CTkLabel(row_frame, text=serial, font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["dark"]).grid(row=0, column=0, sticky="w", padx=5)
            ctk.CTkLabel(row_frame, text=modelo, font=ctk.CTkFont(size=11), text_color=COLORS["dark"]).grid(row=0, column=1, sticky="w", padx=5)
            ctk.CTkLabel(row_frame, text=distrib, font=ctk.CTkFont(size=11), text_color=COLORS["gray"]).grid(row=0, column=2, sticky="w", padx=5)
            ctk.CTkLabel(row_frame, text=cliente, font=ctk.CTkFont(size=11), text_color=COLORS["gray"]).grid(row=0, column=3, sticky="w", padx=5)

            st_fg = ctk.CTkFrame(row_frame, fg_color=status_colors.get(estado, COLORS["gray"]), corner_radius=6, width=80)
            st_fg.grid(row=0, column=4, sticky="w", padx=5)
            ctk.CTkLabel(st_fg, text=estado, font=ctk.CTkFont(size=10, weight="bold"), text_color="white").pack(pady=3)

            btn_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            btn_frame.grid(row=0, column=5, sticky="e", padx=5)
            ctk.CTkButton(btn_frame, text="✏️", width=30, height=24, corner_radius=6, font=ctk.CTkFont(size=11), command=lambda m=mid: self.edit_machine(m), fg_color=COLORS["gold"], hover_color="#C78A32", text_color="white").pack(side="left", padx=2)
            ctk.CTkButton(btn_frame, text="🗑️", width=30, height=24, corner_radius=6, font=ctk.CTkFont(size=11), command=lambda m=mid: self.delete_machine(mid, serial), fg_color="#EF4444", hover_color="#DC2626", text_color="white").pack(side="left", padx=2)

    def delete_machine(self, mid, serial):
        top = ctk.CTkToplevel(self)
        top.title("Confirmar eliminación")
        top.geometry("320x160")
        top.transient(self.master)
        top.grab_set()
        ctk.CTkLabel(top, text=f"¿Eliminar máquina?", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(16,4))
        ctk.CTkLabel(top, text=f"Serial: {serial}", font=ctk.CTkFont(size=11), text_color="#6B7280").pack()
        ctk.CTkLabel(top, text="Esta acción no se puede deshacer", font=ctk.CTkFont(size=10), text_color="#EF4444").pack(pady=(4,12))
        btns = ctk.CTkFrame(top, fg_color="transparent")
        btns.pack()
        ctk.CTkButton(btns, text="Cancelar", command=top.destroy, width=80, corner_radius=6, fg_color="#6B7280", hover_color="#4B5563").pack(side="left", padx=4)
        ctk.CTkButton(btns, text="Eliminar", width=80, corner_radius=6, fg_color="#EF4444", hover_color="#DC2626", text_color="white", command=lambda: (self._do_delete(mid), top.destroy())).pack(side="left", padx=4)

    def _do_delete(self, mid):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("DELETE FROM machines WHERE id = ?", (mid,))
            conn.commit()
            conn.close()
            self.message.configure(text="✓ Máquina eliminada", text_color=COLORS["green"])
            self.load_machines()
        except Exception as e:
            self.message.configure(text=f"⚠ Error: {e}", text_color=COLORS["red"])

    def edit_machine(self, mid):
        top = ctk.CTkToplevel(self)
        top.title("Editar Máquina")
        top.geometry("360x280")
        top.transient(self.master)
        top.grab_set()
        conn = sqlite3.connect(DB_PATH)
        r = conn.execute("SELECT serial_number, model_id, distributor_id, status FROM machines WHERE id = ?", (mid,)).fetchone()
        conn.close()
        if not r:
            return
        serial_old, mid_old, did_old, status_old = r

        f = ctk.CTkFrame(top, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(f, text="N° Serial", font=ctk.CTkFont(size=11), text_color=COLORS["gray"]).pack(anchor="w")
        e_serial = ctk.CTkEntry(f, width=200, corner_radius=8)
        e_serial.insert(0, serial_old)
        e_serial.pack(fill="x", pady=(2,10))

        ctk.CTkLabel(f, text="Modelo", font=ctk.CTkFont(size=11), text_color=COLORS["gray"]).pack(anchor="w")
        cb_model = ctk.CTkComboBox(f, values=list(self.models_dict.keys()), width=200, corner_radius=8)
        # busca clave
        mk = [k for k,v in self.models_dict.items() if v == mid_old]
        cb_model.set(mk[0] if mk else list(self.models_dict.keys())[0] if self.models_dict else "")
        cb_model.pack(fill="x", pady=(2,10))

        ctk.CTkLabel(f, text="Distribuidor", font=ctk.CTkFont(size=11), text_color=COLORS["gray"]).pack(anchor="w")
        cb_dist = ctk.CTkComboBox(f, values=list(self.distrib_dict.keys()), width=200, corner_radius=8)
        dk = [k for k,v in self.distrib_dict.items() if v == did_old]
        cb_dist.set(dk[0] if dk else list(self.distrib_dict.keys())[0] if self.distrib_dict else "")
        cb_dist.pack(fill="x", pady=(2,10))

        ctk.CTkLabel(f, text="Estado", font=ctk.CTkFont(size=11), text_color=COLORS["gray"]).pack(anchor="w")
        cb_stat = ctk.CTkComboBox(f, values=["En Stock", "Instalada", "Desincorporada"], width=200, corner_radius=8)
        cb_stat.set(status_old)
        cb_stat.pack(fill="x", pady=(2,12))

        msg = ctk.CTkLabel(f, text="", font=ctk.CTkFont(size=11))
        msg.pack()

        def save():
            ns = e_serial.get().strip()
            nm = cb_model.get()
            nd = cb_dist.get()
            st = cb_stat.get()
            if not ns or not nm or not nd:
                msg.configure(text="⚠ Complete campos", text_color=COLORS["red"])
                return
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("UPDATE machines SET serial_number=?, model_id=?, distributor_id=?, status=? WHERE id=?",
                             (ns, self.models_dict[nm], self.distrib_dict[nd], st, mid))
                conn.commit()
                conn.close()
                top.destroy()
                self.message.configure(text="✓ Actualizado", text_color=COLORS["green"])
                self.load_machines()
            except sqlite3.IntegrityError:
                msg.configure(text="⚠ Serial ya existe", text_color=COLORS["red"])

        ctk.CTkButton(f, text="Guardar cambios", command=save, fg_color=COLORS["blue"], hover_color="#027A9E", text_color="white", corner_radius=8, height=36).pack(pady=4)