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
        user_frame.pack(side="left", padx=15, pady=8)

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

        nav_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        nav_frame.pack(side="right", padx=15, pady=8)

        menu_items = [
            ("🏠", "Inicio", self.show_home),
            ("📦", "Inventario", self.show_inventory_view),
            ("👥", "Clientes", self.show_clients_view),
            ("⚙️", "Servicios", self.show_services_view),
            ("📑", "Catálogos", self.show_catalogs_view),
            ("📊", "Reportes", self.show_reportes_view),
        ]

        self.menu_buttons = []
        for icon, text, cmd in menu_items:
            btn = ctk.CTkButton(
                nav_frame,
                text=f"{icon}",
                width=42,
                height=34,
                command=cmd,
                fg_color="transparent",
                hover_color=COLORS["hover"],
                text_color=COLORS["text_light"],
                font=ctk.CTkFont(size=16),
            )
            btn.pack(side="left", padx=3)
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
        super().__init__(master, fg_color=COLORS["bg_gray"])
        self.pack(fill="both", expand=True)

        self.setup_sidebar()
        self.setup_main_content()

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self, width=220, corner_radius=0, fg_color=COLORS["dark_blue"]
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        sidebar_title = ctk.CTkLabel(
            self.sidebar,
            text="📊 Estadísticas",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_light"],
        )
        sidebar_title.pack(pady=(20, 15))

        stats = self.get_stats()
        cards_data = [
            ("📦", "En Stock", stats["en_stock"], COLORS["dark_blue"]),
            ("🔧", "Instaladas", stats["instaladas"], COLORS["gold"]),
            ("👥", "Clientes", stats["clientes"], COLORS["dark_blue"]),
            ("⚙️", "Servicios", stats["servicios"], COLORS["gold"]),
        ]

        cards_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        cards_container.pack(fill="both", expand=True, padx=15)

        for icon, label, value, color in cards_data:
            card = ctk.CTkFrame(
                cards_container, fg_color=COLORS["card_bg"], corner_radius=8
            )
            card.pack(fill="x", pady=8)

            icon_label = ctk.CTkLabel(
                card, text=icon, font=ctk.CTkFont(size=20), justify="center"
            )
            icon_label.pack(anchor="center", pady=(12, 0))

            value_label = ctk.CTkLabel(
                card,
                text=str(value),
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=color,
                justify="center",
            )
            value_label.pack(anchor="center")

            label_text = ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_dark"],
                justify="center",
            )
            label_text.pack(anchor="center", pady=(0, 12))

    def setup_main_content(self):
        self.main_content = ctk.CTkFrame(self, fg_color=COLORS["bg_gray"])
        self.main_content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.title = ctk.CTkLabel(
            self.main_content,
            text="Panel Principal",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_dark"],
        )
        self.title.pack(anchor="w", pady=(0, 15))

        self.setup_recent_activity()

    def setup_recent_activity(self):
        activity_frame = ctk.CTkFrame(
            self.main_content, fg_color=COLORS["white"], corner_radius=10
        )
        activity_frame.pack(fill="both", expand=True)

        activity_header = ctk.CTkFrame(
            activity_frame, fg_color=COLORS["card_bg"], corner_radius=10
        )
        activity_header.pack(fill="x")
        activity_header.pack_propagate(False)
        activity_header.configure(height=50)

        activity_title = ctk.CTkLabel(
            activity_header,
            text="📋 Movimientos Recientes",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_dark"],
        )
        activity_title.pack(side="left", padx=20, pady=12)

        activity_content = ctk.CTkFrame(activity_frame, fg_color="transparent")
        activity_content.pack(fill="both", expand=True, padx=15, pady=15)

        recent = self.get_recent_activity()

        if not recent:
            no_data = ctk.CTkLabel(
                activity_content,
                text="No hay movimientos recientes",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_gray"],
            )
            no_data.pack(pady=30)
        else:
            for tipo, serial, cliente, fecha in recent:
                item_frame = ctk.CTkFrame(
                    activity_content, fg_color=COLORS["card_bg"], corner_radius=8
                )
                item_frame.pack(fill="x", pady=5)

                tipo_color = (
                    COLORS["gold"] if tipo == "Instalación" else COLORS["dark_blue"]
                )
                tipo_label = ctk.CTkLabel(
                    item_frame,
                    text=f"  {tipo}  ",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=COLORS["text_dark"],
                )
                tipo_label.pack(side="left", padx=10, pady=10)
                tipo_label.configure(fg_color=tipo_color, corner_radius=5)

                info_text = f"Serial: {serial} • Cliente: {cliente}"
                info_label = ctk.CTkLabel(
                    item_frame, text=info_text, font=ctk.CTkFont(size=12), anchor="w"
                )
                info_label.pack(side="left", padx=10, pady=10, fill="x", expand=True)

                date_label = ctk.CTkLabel(
                    item_frame,
                    text=fecha,
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS["text_gray"],
                )
                date_label.pack(side="right", padx=10, pady=10)

    def get_stats(self):
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

    def get_recent_activity(self):
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
            LIMIT 5
        """
        cursor = conn.execute(query)
        activities = cursor.fetchall()
        conn.close()
        return activities
