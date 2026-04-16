import tkinter
import customtkinter as ctk
from ui.catalogs_view import CatalogsView
from ui.inventory_view import InventoryView
from ui.clients_view import ClientsView
from ui.services_view import ServicesView
from ui.reports_view import ReportsView
import sqlite3
import os
from datetime import date, timedelta

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "inventario.db"
)

COLORS = {
    "dark_blue": "#1A3263",
    "gold": "#FAB95B",
    "bg_gray": "#F5F5F5",
    "white": "#FFFFFF",
    "text_dark": "#1A3263",
    "text_light": "#FFFFFF",
    "text_gray": "#6B7280",
    "card_bg": "#FFFFFF",
    "hover": "#456282",
}


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, user_info, on_logout):
        super().__init__(master, fg_color=COLORS["bg_gray"])
        self.pack(fill="both", expand=True)

        self.username = user_info[1]
        self.role = user_info[3]
        self.on_logout = on_logout

        self.current_view = None
        self.active_button = None

        self.setup_header()
        self.setup_main_content()
        self.show_home()

    def setup_header(self):
        self.header = ctk.CTkFrame(
            self, height=50, corner_radius=0, fg_color=COLORS["dark_blue"]
        )
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        user_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        user_frame.place(relx=1, rely=0.5, anchor="e", x=-15, y=0)

        self.user_label = ctk.CTkLabel(
            user_frame,
            text=f"👤 {self.username.capitalize()}",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_light"],
        )
        self.user_label.pack(side="left", padx=10)

        self.logout_btn = ctk.CTkButton(
            user_frame,
            text="↩",
            width=36,
            height=34,
            command=self.on_logout_click,
            fg_color=COLORS["gold"],
            hover_color="#E5A84A",
            text_color=COLORS["dark_blue"],
            font=ctk.CTkFont(size=16),
        )
        self.logout_btn.pack(side="left", padx=5)

        nav_container = ctk.CTkFrame(self.header, fg_color="transparent")
        nav_container.place(relx=0.5, rely=0.5, anchor="center")

        menu_items = [
            ("🏠 Inicio", self.show_home),
            ("📦 Inventario", self.show_inventory_view),
            ("👥 Clientes", self.show_clients_view),
            ("⚙️ Servicios", self.show_services_view),
            ("📑 Catálogos", self.show_catalogs_view),
            ("📊 Reportes", self.show_reportes_view),
        ]

        self.menu_buttons = []
        for text, cmd in menu_items:
            btn = ctk.CTkButton(
                nav_container,
                text=text,
                width=100,
                height=34,
                command=cmd,
                fg_color="transparent",
                hover_color=COLORS["hover"],
                text_color=COLORS["text_light"],
                font=ctk.CTkFont(size=13),
            )
            btn.pack(side="left", padx=4)
            self.menu_buttons.append(btn)

    def setup_main_content(self):
        self.main_content = ctk.CTkFrame(self, fg_color=COLORS["bg_gray"])
        self.main_content.pack(side="right", fill="both", expand=True)
        self.main_content.pack_propagate(False)

    def clear_content(self):
        if self.current_view:
            self.current_view.destroy()
        for btn in self.menu_buttons:
            btn.configure(fg_color="transparent")

    def set_active(self, index):
        for i, btn in enumerate(self.menu_buttons):
            if i == index:
                btn.configure(fg_color=COLORS["gold"])
            else:
                btn.configure(fg_color="transparent")

    def show_home(self):
        self.clear_content()
        self.set_active(0)
        self.current_view = DashboardHome(self.main_content)

    def show_inventory_view(self):
        self.clear_content()
        self.set_active(1)
        self.current_view = InventoryView(self.main_content)

    def show_clients_view(self):
        self.clear_content()
        self.set_active(2)
        from ui.clients_view import ClientsView

        self.current_view = ClientsView(self.main_content)

    def show_services_view(self):
        self.clear_content()
        self.set_active(3)
        from ui.services_view import ServicesView

        self.current_view = ServicesView(self.main_content)

    def show_reportes_view(self):
        self.clear_content()
        self.set_active(5)
        from ui.reports_view import ReportsView

        self.current_view = ReportsView(self.main_content)

    def show_catalogs_view(self):
        self.clear_content()
        self.set_active(4)
        self.current_view = CatalogsView(self.main_content)

    def on_logout_click(self):
        self.clear_content()
        self.on_logout()


class DashboardHome(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#F5F5F5")
        self.pack(fill="both", expand=True)

        self.stats = DashboardHelpers.get_stats()
        self.recent_activity = DashboardHelpers.get_recent_activity()

        self.setup_content()

    def setup_content(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=20)

        content.grid_rowconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=0)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)

        self.setup_left_panel(content)
        self.setup_right_panel(content)

        self.setup_quick_actions(content)

    def setup_left_panel(self, parent):
        left = ctk.CTkFrame(parent, fg_color="white", corner_radius=16)
        left.grid(row=0, column=0, padx=(0, 12), sticky="nsew")

        header = ctk.CTkFrame(left, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(16, 12))

        ctk.CTkLabel(
            header,
            text="Estadísticas",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1A1A2E",
        ).pack(side="left")

        ctk.CTkFrame(left, height=1, fg_color="#E5E7EB").pack(fill="x", padx=18)

        stats_grid = ctk.CTkFrame(left, fg_color="transparent")
        stats_grid.pack(fill="both", expand=True, padx=12, pady=10)

        stats_grid.grid_rowconfigure(0, weight=1)
        stats_grid.grid_rowconfigure(1, weight=1)
        stats_grid.grid_columnconfigure(0, weight=1)
        stats_grid.grid_columnconfigure(1, weight=1)

        self.create_stat(
            stats_grid,
            0,
            0,
            "En Stock",
            self.stats["en_stock"],
            "#3B82F6",
            "📦",
            "#EBF5FF",
        )
        self.create_stat(
            stats_grid,
            0,
            1,
            "Instaladas",
            self.stats["instaladas"],
            "#10B981",
            "🔧",
            "#ECFDF5",
        )
        self.create_stat(
            stats_grid,
            1,
            0,
            "Clientes",
            self.stats["clientes"],
            "#8B5CF6",
            "👥",
            "#F5F3FF",
        )
        self.create_stat(
            stats_grid,
            1,
            1,
            "Servicios",
            self.stats["servicios"],
            "#F59E0B",
            "⚙️",
            "#FFFBEB",
        )

    def create_stat(self, parent, row, col, label, value, color, icon, bg_color):
        card = ctk.CTkFrame(parent, fg_color=bg_color, corner_radius=14)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(expand=True)

        ctk.CTkLabel(
            content, text=icon, font=ctk.CTkFont(size=32), text_color=color
        ).pack(pady=(10, 4))

        ctk.CTkLabel(
            content,
            text=str(value),
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=color,
        ).pack()

        ctk.CTkLabel(
            content,
            text=label,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#374151",
        ).pack(pady=(2, 10))

    def setup_right_panel(self, parent):
        right = ctk.CTkFrame(parent, fg_color="white", corner_radius=16)
        right.grid(row=0, column=1, padx=(12, 0), sticky="nsew")

        header = ctk.CTkFrame(right, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(16, 12))

        ctk.CTkLabel(
            header,
            text="Actividad Reciente",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1A1A2E",
        ).pack(side="left")

        count_badge = ctk.CTkLabel(
            header,
            text=f" {len(self.recent_activity)} ",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="white",
            fg_color="#1A3263",
            corner_radius=10,
        )
        count_badge.pack(side="right")

        ctk.CTkFrame(right, height=1, fg_color="#E5E7EB").pack(fill="x", padx=18)

        scroll = ctk.CTkScrollableFrame(
            right, fg_color="transparent", scrollbar_button_color="#D1D5DB"
        )
        scroll.pack(fill="both", expand=True, padx=12, pady=10)

        if not self.recent_activity:
            empty = ctk.CTkFrame(scroll, fg_color="#F9FAFB", corner_radius=12)
            empty.pack(fill="x", pady=30)
            ctk.CTkLabel(
                empty, text="📭", font=ctk.CTkFont(size=28), text_color="#D1D5DB"
            ).pack(pady=(16, 6))
            ctk.CTkLabel(
                empty,
                text="Sin actividad",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#9CA3AF",
            ).pack()
        else:
            for activity in self.recent_activity:
                self.create_activity(scroll, activity)

    def create_activity(self, parent, activity):
        tipo, serial, cliente, fecha = activity

        colors = {
            "Instalación": ("#3B82F6", "#EFF6FF"),
            "Mantenimiento Preventivo": ("#10B981", "#ECFDF5"),
            "Reparación": ("#EF4444", "#FEF2F2"),
        }
        icons = {
            "Instalación": "🔧",
            "Mantenimiento Preventivo": "🛠️",
            "Reparación": "⚙️",
        }

        color, bg = colors.get(tipo, ("#6B7280", "#F5F5F5"))
        icon = icons.get(tipo, "📋")

        item = ctk.CTkFrame(parent, fg_color=bg, corner_radius=10)
        item.pack(fill="x", pady=5)

        content = ctk.CTkFrame(item, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=12, pady=10)

        top = ctk.CTkFrame(content, fg_color="transparent")
        top.pack(fill="x")

        badge = ctk.CTkLabel(
            top,
            text=f" {tipo} ",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="white",
            fg_color=color,
            corner_radius=6,
        )
        badge.pack(side="left")

        ctk.CTkLabel(
            top, text=fecha, font=ctk.CTkFont(size=11), text_color="#9CA3AF"
        ).pack(side="right")

        bottom = ctk.CTkFrame(content, fg_color="transparent")
        bottom.pack(fill="x", pady=(6, 0))

        ctk.CTkLabel(
            bottom,
            text=f"{icon} {serial}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#374151",
        ).pack(side="left")

        ctk.CTkLabel(
            bottom, text=f"• {cliente}", font=ctk.CTkFont(size=11), text_color="#6B7280"
        ).pack(side="left", padx=(10, 0))

    def navigate_to(self, view):
        pass

    def setup_quick_actions(self, parent):
        actions_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=14)
        actions_frame.grid(
            row=1, column=0, columnspan=2, padx=(0, 0), pady=(15, 0), sticky="ew"
        )

        header = ctk.CTkFrame(actions_frame, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(14, 10))

        ctk.CTkLabel(
            header,
            text="Acciones Rápidas",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1A1A2E",
        ).pack(side="left")

        actions = ctk.CTkFrame(actions_frame, fg_color="transparent")
        actions.pack(fill="x", padx=12, pady=(0, 12))

        actions.grid_rowconfigure(0, weight=1)
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)
        actions.grid_columnconfigure(2, weight=1)
        actions.grid_columnconfigure(3, weight=1)

        buttons = [
            ("Nueva Máquina", "📦", "#3B82F6", lambda: self.show_inventory_view()),
            ("Nuevo Cliente", "👤", "#10B981", lambda: self.show_clients_view()),
            ("Registrar Servicio", "🔧", "#F59E0B", lambda: self.show_services_view()),
            ("Ver Reportes", "📊", "#8B5CF6", lambda: self.show_reportes_view()),
        ]

        for i, (text, icon, color, cmd) in enumerate(buttons):
            btn_frame = ctk.CTkFrame(actions, fg_color="#F8FAFC", corner_radius=12)
            btn_frame.grid(row=0, column=i, padx=8, pady=8, sticky="nsew")

            btn = ctk.CTkButton(
                btn_frame,
                text=f"{icon}\n{text}",
                command=cmd,
                fg_color=color,
                hover_color=color,
                text_color="white",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=130,
                height=50,
                corner_radius=10,
            )
            btn.pack(expand=True, padx=8, pady=8)


class DashboardHelpers:
    @staticmethod
    def get_stats():
        stats = {"en_stock": 0, "instaladas": 0, "clientes": 0, "servicios": 0}
        if not os.path.exists(DB_PATH):
            return stats

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM machines WHERE status = 'En Stock'")
        stats["en_stock"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM machines WHERE status = 'Instalada'")
        stats["instaladas"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM clients")
        stats["clientes"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM services")
        stats["servicios"] = cursor.fetchone()[0]

        conn.close()
        return stats

    @staticmethod
    def get_recent_activity():
        activities = []
        if not os.path.exists(DB_PATH):
            return activities

        conn = sqlite3.connect(DB_PATH)
        query = """
            SELECT s.service_type, m.serial_number, c.name, s.service_date
            FROM services s
            JOIN machines m ON s.machine_id = m.id
            JOIN clients c ON m.client_id = c.id
            ORDER BY s.service_date DESC, s.id DESC
            LIMIT 15
        """
        cursor = conn.execute(query)
        activities = cursor.fetchall()
        conn.close()
        return activities

    @staticmethod
    def get_distributor_count():
        if not os.path.exists(DB_PATH):
            return 0
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute("SELECT COUNT(*) FROM distributors")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    @staticmethod
    def get_next_maintenance():
        if not os.path.exists(DB_PATH):
            return "N/A"
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute("""
            SELECT next_maintenance_date FROM services 
            WHERE next_maintenance_date IS NOT NULL 
            ORDER BY next_maintenance_date ASC LIMIT 1
        """)
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "N/A"
