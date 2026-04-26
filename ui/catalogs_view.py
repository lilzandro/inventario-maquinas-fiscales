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

class CatalogsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS["bg"])
        self.pack(fill="both", expand=True)

        self.tabview = ctk.CTkTabview(
            self,
            fg_color=COLORS["card"],
            segmented_button_fg_color=COLORS["medium"],
            segmented_button_selected_color=COLORS["blue"]
        )
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        self.tab_distrib = self.tabview.add("📦 Distribuidores")
        self.tab_model = self.tabview.add("🏷️ Modelos")

        self.build_distrib()
        self.build_model()

    def build_distrib(self):
        header = ctk.CTkFrame(self.tab_distrib, fg_color=COLORS["medium"], height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="Distribuidores",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=15)

        form = ctk.CTkFrame(self.tab_distrib, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=15)

        self.d_name = ctk.CTkEntry(form, width=280, placeholder_text="Nombre del distribuidor", corner_radius=8, border_color=COLORS["blue"])
        self.d_name.pack(side="left", padx=(0, 10))

        self.d_contact = ctk.CTkEntry(form, width=250, placeholder_text="Contacto (teléfono/email)", corner_radius=8, border_color=COLORS["blue"])
        self.d_contact.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            form,
            text="+ Agregar",
            command=self.add_distrib,
            fg_color=COLORS["blue"],
            hover_color="#027A9E",
            text_color="white",
            corner_radius=8,
            height=36
        ).pack(side="left", padx=10)

        self.d_msg = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=12))
        self.d_msg.pack(side="left")

        table = ctk.CTkFrame(self.tab_distrib, fg_color=COLORS["card"], corner_radius=12)
        table.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.d_frame = ctk.CTkScrollableFrame(table, fg_color="transparent")
        self.d_frame.pack(fill="both", expand=True, padx=15, pady=15)

        headers = ["ID", "Nombre", "Contacto", "Acciones"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                self.d_frame, text=h,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["dark"]
            ).grid(row=0, column=i, padx=12, pady=8, sticky="w")

        self.d_rows = []
        for i in range(1, 20):
            row = []
            for j in range(3):
                lbl = ctk.CTkLabel(self.d_frame, text="", font=ctk.CTkFont(size=11), text_color=COLORS["gray"])
                lbl.grid(row=i, column=j, padx=12, pady=4, sticky="w")
                row.append(lbl)
            btn = ctk.CTkButton(
                self.d_frame, text="🗑️",
                fg_color="transparent",
                text_color=COLORS["red"],
                width=40,
                height=24
            )
            btn.grid(row=i, column=3, padx=5, pady=2)
            row.append(btn)
            self.d_rows.append(row)

        self.load_distrib()

    def build_model(self):
        header = ctk.CTkFrame(self.tab_model, fg_color=COLORS["medium"], height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="Modelos de Máquinas",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=15)

        form = ctk.CTkFrame(self.tab_model, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=15)

        self.m_brand = ctk.CTkEntry(form, width=200, placeholder_text="Marca", corner_radius=8, border_color=COLORS["gold"])
        self.m_brand.pack(side="left", padx=(0, 10))

        self.m_model = ctk.CTkEntry(form, width=300, placeholder_text="Nombre del modelo", corner_radius=8, border_color=COLORS["gold"])
        self.m_model.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            form,
            text="+ Agregar",
            command=self.add_model,
            fg_color=COLORS["gold"],
            hover_color="#C78A32",
            text_color=COLORS["dark"],
            corner_radius=8,
            height=36
        ).pack(side="left", padx=10)

        self.m_msg = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=12))
        self.m_msg.pack(side="left")

        table = ctk.CTkFrame(self.tab_model, fg_color=COLORS["card"], corner_radius=12)
        table.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.m_frame = ctk.CTkScrollableFrame(table, fg_color="transparent")
        self.m_frame.pack(fill="both", expand=True, padx=15, pady=15)

        headers = ["ID", "Marca", "Modelo"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                self.m_frame, text=h,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["dark"]
            ).grid(row=0, column=i, padx=15, pady=8, sticky="w")

        self.m_rows = []
        for i in range(1, 25):
            row = []
            for j in range(3):
                lbl = ctk.CTkLabel(self.m_frame, text="", font=ctk.CTkFont(size=11), text_color=COLORS["gray"])
                lbl.grid(row=i, column=j, padx=15, pady=4, sticky="w")
                row.append(lbl)
            self.m_rows.append(row)

        self.load_model()

    def add_model(self):
        brand = self.m_brand.get()
        model = self.m_model.get()
        if not brand or not model:
            self.m_msg.configure(text="⚠ Ingrese marca y modelo", text_color=COLORS["red"])
            return

        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO machine_models (brand, model_name) VALUES (?, ?)", (brand, model))
        conn.commit()
        conn.close()
        self.m_brand.delete(0, 'end')
        self.m_model.delete(0, 'end')
        self.m_msg.configure(text="✓ Modelo agregado", text_color=COLORS["green"])
        self.load_model()

    def load_model(self):
        for w in self.m_frame.winfo_children():
            w.destroy()
        conn=sqlite3.connect(DB_PATH)
        rows=conn.execute("SELECT id, brand, model_name FROM machine_models ORDER BY brand, model_name").fetchall()
        conn.close()
        if not rows:
            ctk.CTkLabel(self.m_frame, text="No hay modelos", text_color="#9CA3AF", font=ctk.CTkFont(size=12)).pack(pady=20)
            return
        for r in rows:
            fid, fb, fm = r
            row=ctk.CTkFrame(self.m_frame, fg_color="#F8FAFC", corner_radius=10)
            row.pack(fill="x", pady=4)
            row.bind("<Enter>", lambda e, w=row: w.configure(fg_color="#F1F5F9"))
            row.bind("<Leave>", lambda e, w=row: w.configure(fg_color="#F8FAFC"))
            rf=ctk.CTkFrame(row, fg_color="transparent"); rf.pack(fill="x", padx=12, pady=8)
            rf.grid_columnconfigure(0, weight=2); rf.grid_columnconfigure(1, weight=3); rf.grid_columnconfigure(2, weight=1)
            ctk.CTkLabel(rf, text=fb, font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["dark"]).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(rf, text=fm, font=ctk.CTkFont(size=12), text_color=COLORS["gray"]).grid(row=0, column=1, sticky="w", padx=(10,0))
            btnf=ctk.CTkFrame(rf, fg_color="transparent"); btnf.grid(row=0, column=2, sticky="e")
            ctk.CTkButton(btnf, text="✏️", width=26, height=22, corner_radius=6, font=ctk.CTkFont(size=10),
                          command=lambda i=fid, b=fb, m=fm: self._m_edit(i, b, m), fg_color=COLORS["gold"], hover_color="#C78A32", text_color="white").pack(side="left", padx=1)
            ctk.CTkButton(btnf, text="🗑️", width=26, height=22, corner_radius=6, font=ctk.CTkFont(size=10),
                          command=lambda i=fid, t=fb+" - "+fm: self._m_borrar(i, t), fg_color="#EF4444", hover_color="#DC2626", text_color="white").pack(side="left", padx=1)

    def _m_borrar(self, mid, txt):
        top=ctk.CTkToplevel(self); top.title("Confirmar"); top.geometry("300x140"); top.transient(self.master); top.grab_set()
        ctk.CTkLabel(top, text="¿Eliminar?", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(16,2))
        ctk.CTkLabel(top, text=txt, font=ctk.CTkFont(size=11), text_color="#6B7280").pack()
        ctk.CTkLabel(top, text="Esta acción no se puede deshacer", font=ctk.CTkFont(size=10), text_color="#EF4444").pack(pady=(2,12))
        f=ctk.CTkFrame(top, fg_color="transparent")
        f.pack()
        ctk.CTkButton(f, text="Cancelar", command=top.destroy, width=70, corner_radius=6, fg_color="#6B7280").pack(side="left", padx=4)
        ctk.CTkButton(f, text="Eliminar", width=70, corner_radius=6, fg_color="#EF4444", text_color="white",
                       command=lambda: (self._m_do(mid), top.destroy())).pack(side="left", padx=4)

    def _m_do(self, mid):
        try:
            conn=sqlite3.connect(DB_PATH)
            conn.execute("DELETE FROM machine_models WHERE id=?", (mid,))
            conn.commit(); conn.close()
            self.load_model()
        except Exception:
            pass

    def _m_edit(self, mid, old_brand, old_model):
        top=ctk.CTkToplevel(self); top.title("Editar"); top.geometry("320x200"); top.transient(self.master); top.grab_set()
        f=ctk.CTkFrame(top, fg_color="transparent"); f.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(f, text="Marca", font=ctk.CTkFont(size=11), text_color=COLORS["gray"]).pack(anchor="w")
        e1=ctk.CTkEntry(f, width=220, corner_radius=8); e1.insert(0, old_brand); e1.pack(fill="x", pady=(2,10))
        ctk.CTkLabel(f, text="Modelo", font=ctk.CTkFont(size=11), text_color=COLORS["gray"]).pack(anchor="w")
        e2=ctk.CTkEntry(f, width=220, corner_radius=8); e2.insert(0, old_model); e2.pack(fill="x", pady=(2,12))
        def sv():
            try:
                conn=sqlite3.connect(DB_PATH)
                conn.execute("UPDATE machine_models SET brand=?, model_name=? WHERE id=?", (e1.get().strip(), e2.get().strip(), mid))
                conn.commit(); conn.close()
                top.destroy(); self.load_model()
            except: pass
        ctk.CTkButton(f, text="Guardar", command=sv, fg_color=COLORS["blue"], hover_color="#027A9E", text_color="white", corner_radius=8, width=100).pack()