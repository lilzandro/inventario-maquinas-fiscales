    def load_inventory(self):
        for w in self.inv_rows_frame.winfo_children():
            w.destroy()

        if not os.path.exists(DB_PATH):
            ctk.CTkLabel(self.inv_rows_frame, text="Sin datos", text_color="#9CA3AF").pack(pady=20)
            return

        conn = sqlite3.connect(DB_PATH)
        query = '''
            SELECT m.serial_number, mo.brand || ' ' || mo.model_name, d.name, m.status, IFNULL(c.name, 'Sin asignar')
            FROM machines m
            LEFT JOIN machine_models mo ON m.model_id = mo.id
            LEFT JOIN distributors d ON m.distributor_id = d.id
            LEFT JOIN clients c ON m.client_id = c.id
            ORDER BY m.id DESC
        '''
        rows = conn.execute(query).fetchall()
        conn.close()

        if not rows:
            ctk.CTkLabel(self.inv_rows_frame, text="No hay máquinas registradas", text_color="#9CA3AF").pack(pady=20)
            return

        st_colors = {"En Stock": COLORS["blue"], "Instalada": COLORS["green"], "Desincorporada": COLORS["red"]}

        for r in rows:
            serial, modelo, distrib, estado, cliente = r
            rf = ctk.CTkFrame(self.inv_rows_frame, fg_color="#F8FAFC", corner_radius=10)
            rf.pack(fill="x", pady=4)
            rf.bind("<Enter>", lambda e, w=rf: w.configure(fg_color="#F1F5F9"))
            rf.bind("<Leave>", lambda e, w=rf: w.configure(fg_color="#F8FAFC"))

            rf.grid_columnconfigure(0, weight=15)
            rf.grid_columnconfigure(1, weight=20)
            rf.grid_columnconfigure(2, weight=18)
            rf.grid_columnconfigure(3, weight=10)
            rf.grid_columnconfigure(4, weight=17)

            ctk.CTkLabel(rf, text=serial, font=ctk.CTkFont(size=11), text_color=COLORS["dark"]).grid(row=0, col=0, sticky="w", padx=8)
            ctk.CTkLabel(rf, text=modelo, font=ctk.CTkFont(size=11), text_color=COLORS["dark"]).grid(row=0, col=1, sticky="w", padx=8)
            ctk.CTkLabel(rf, text=distrib or "—", font=ctk.CTkFont(size=11), text_color=COLORS["gray"]).grid(row=0, col=2, sticky="w", padx=8)

            stf=ctk.CTkFrame(rf, fg_color=st_colors.get(estado, COLORS["gray"]), corner_radius=6, width=70)
            stf.grid(row=0, col=3, sticky="w", padx=5)
            ctk.CTkLabel(stf, text=estado, font=ctk.CTkFont(size=9, weight="bold"), text_color="white").pack(pady=3)

            ctk.CTkLabel(rf, text=cliente, font=ctk.CTkFont(size=11), text_color=COLORS["gray"]).grid(row=0, col=4, sticky="w", padx=8)