import customtkinter as ctk
import sqlite3
import os
from PIL import Image
from database.db_manager import DB_PATH
from theme import AppTheme, UI_COLORS, FONT_SIZES, SIZES

_LOGO_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "img", "logo-nombre.png"
)

_FS = {k: round(v * 1.15) for k, v in FONT_SIZES.items()}
_NAV_FS = {k: round(v * 1.30) for k, v in FONT_SIZES.items()}
_ACT_FS = {k: round(v * 1.10) for k, v in _FS.items()}
from utils.logger import logger


_SIDEBAR_HOVER = "#243048"
_SIDEBAR_SEP = "#2A3550"
_TOPBAR_BORDER = "#E8EDF2"
_SIDEBAR_W = 270  # expanded
_SIDEBAR_W_COL = 64  # collapsed


def _stat_card(parent, col, label, value, bg, color, icon):
    card = ctk.CTkFrame(
        parent,
        fg_color=UI_COLORS.CARD,
        corner_radius=SIZES["card_radius"],
        border_width=1,
        border_color=UI_COLORS.BORDER,
    )
    card.grid(
        row=0, column=col, padx=(0 if col == 0 else SIZES["pad_small"], 0), sticky="ew"
    )
    inner = ctk.CTkFrame(card, fg_color="transparent")
    inner.pack(fill="x", padx=SIZES["pad"], pady=SIZES["pad"])
    box = ctk.CTkFrame(
        inner,
        width=SIZES["icon_box"],
        height=SIZES["icon_box"],
        fg_color=bg,
        corner_radius=10,
    )
    box.pack(anchor="w")
    box.pack_propagate(False)
    ctk.CTkLabel(box, text=icon, font=ctk.CTkFont(size=16), text_color=color).place(
        relx=0.5, rely=0.5, anchor="center"
    )
    ctk.CTkLabel(
        inner,
        text=str(value),
        font=ctk.CTkFont(size=_FS["xxlarge"], weight="bold"),
        text_color=UI_COLORS.TEXT,
    ).pack(anchor="w", pady=(6, 2))
    ctk.CTkLabel(
        inner,
        text=label,
        font=ctk.CTkFont(size=_FS["small"]),
        text_color=UI_COLORS.TEXT_MUTED,
    ).pack(anchor="w")


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, user_info, on_logout):
        super().__init__(master, fg_color=AppTheme.BACKGROUND)
        self.pack(fill="both", expand=True)

        self.user_info = user_info
        self.username = user_info[1]
        self.role = user_info[3]
        self.on_logout = on_logout

        self.current_view = None
        self._current_key = None
        self._view_cache = {}
        self.nav_buttons = []  # (btn, label)
        self._nav_data = []  # (btn, icon, label)
        self.sidebar_collapsed = False

        self._setup_sidebar()
        self._setup_right_panel()
        self.show_home()
        self.master.bind("<Configure>", self._on_window_resize)

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self, fg_color=UI_COLORS.SIDEBAR, width=_SIDEBAR_W, corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # ── Logo area
        logo_area = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=116)
        logo_area.pack(fill="x", padx=16, pady=(20, 8))
        logo_area.pack_propagate(False)

        # store ref to hide/show on collapse
        self._logo_text = ctk.CTkFrame(logo_area, fg_color="transparent")
        self._logo_text.pack(fill="x")
        try:
            _pil = Image.open(_LOGO_PATH).convert("RGBA")
            _pil.putdata(
                [
                    (r, g, b, 0) if r > 230 and g > 230 and b > 230 else (r, g, b, a)
                    for r, g, b, a in _pil.getdata()
                ]
            )
            _logo_img = ctk.CTkImage(light_image=_pil, dark_image=_pil, size=(200, 104))
            logo_bg = ctk.CTkFrame(self._logo_text, fg_color="#FFFFFF", corner_radius=8)
            logo_bg.pack(anchor="w")
            ctk.CTkLabel(logo_bg, image=_logo_img, text="").pack(padx=6, pady=4)
        except Exception:
            ctk.CTkLabel(
                self._logo_text,
                text="Adamo",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color="#ffffff",
            ).pack(anchor="w")
            ctk.CTkLabel(
                self._logo_text,
                text="Corporación Adamo Gentile C.A",
                font=ctk.CTkFont(size=10),
                text_color=UI_COLORS.SIDEBAR_TEXT,
            ).pack(anchor="w")

        ctk.CTkFrame(self.sidebar, height=1, fg_color=_SIDEBAR_SEP).pack(
            fill="x", padx=16, pady=(8, 12)
        )

        # ── Nav items
        nav_items = [
            ("🏠", "Inicio", self.show_home),
            ("⚙️", "Servicios", self.show_services_view),
            ("📊", "Reportes", self.show_reportes_view),
        ]
        if self.role == "admin":
            nav_items.insert(1, ("📦", "Inventario", self.show_inventory_view))
            nav_items.insert(2, ("👥", "Clientes", self.show_clients_view))
            nav_items.append(("🔐", "Usuarios", self.show_users_view))

        self._nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self._nav_frame.pack(fill="x", padx=8)
        self._nav_frame.grid_columnconfigure(0, weight=1)

        for idx, (icon, label, cmd) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self._nav_frame,
                text=f"  {icon}  {label}",
                anchor="w",
                corner_radius=SIZES["button_radius"],
                height=SIZES["nav_item_height"],
                fg_color="transparent",
                hover_color=_SIDEBAR_HOVER,
                text_color=UI_COLORS.SIDEBAR_TEXT,
                font=ctk.CTkFont(size=_FS["large"], weight="bold"),
                command=cmd,
            )
            btn.grid(row=idx, column=0, sticky="ew", pady=1)
            self.nav_buttons.append((btn, label))
            self._nav_data.append((btn, icon, label))

        # ── Logout (bottom)
        ctk.CTkFrame(self.sidebar, height=1, fg_color=_SIDEBAR_SEP).pack(
            fill="x", padx=16, side="bottom", pady=(0, 8)
        )
        self._logout_btn = ctk.CTkButton(
            self.sidebar,
            text="  ↩  Cerrar Sesión",
            anchor="w",
            height=SIZES["nav_item_height"],
            corner_radius=SIZES["button_radius"],
            fg_color="transparent",
            hover_color="#3B1F1F",
            text_color="#EF4444",
            font=ctk.CTkFont(size=_FS["large"], weight="bold"),
            command=self._on_logout_click,
        )
        self._logout_btn.pack(fill="x", padx=8, side="bottom", pady=(0, 8))

    # ── Responsive resize ─────────────────────────────────────────────────────

    def _on_window_resize(self, event):
        if event.widget is not self.master:
            return
        w = event.width
        if w < 950 and not self.sidebar_collapsed:
            self.toggle_sidebar()
        elif w >= 950 and self.sidebar_collapsed:
            self.toggle_sidebar()

    # ── Sidebar collapse toggle ───────────────────────────────────────────────

    def toggle_sidebar(self):
        self.sidebar_collapsed = not self.sidebar_collapsed

        if self.sidebar_collapsed:
            self.sidebar.configure(width=_SIDEBAR_W_COL)
            self._logo_text.pack_forget()
            for btn, icon, _ in self._nav_data:
                btn.configure(text=icon, anchor="center")
            self._logout_btn.configure(text="↩", anchor="center")
        else:
            self.sidebar.configure(width=_SIDEBAR_W)
            self._logo_text.pack(fill="x")
            for btn, icon, label in self._nav_data:
                btn.configure(text=f"  {icon}  {label}", anchor="w")
            self._logout_btn.configure(text="  ↩  Cerrar Sesión", anchor="w")

    # ── Right panel ───────────────────────────────────────────────────────────

    def _setup_right_panel(self):
        right = ctk.CTkFrame(self, fg_color=AppTheme.BACKGROUND, corner_radius=0)
        right.pack(side="right", fill="both", expand=True)

        self._setup_topbar(right)

        self.main_content = ctk.CTkFrame(
            right, fg_color=AppTheme.BACKGROUND, corner_radius=0
        )
        self.main_content.pack(fill="both", expand=True)

    def _setup_topbar(self, parent):
        topbar = ctk.CTkFrame(
            parent,
            height=SIZES["header_height"],
            fg_color=UI_COLORS.TOPBAR,
            corner_radius=0,
        )
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        ctk.CTkFrame(topbar, height=1, fg_color=_TOPBAR_BORDER).pack(
            fill="x", side="bottom"
        )

        inner = ctk.CTkFrame(topbar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=SIZES["pad"])

        # Hamburger toggle button
        self._toggle_btn = ctk.CTkButton(
            inner,
            text="☰",
            width=36,
            height=36,
            corner_radius=SIZES["button_radius"],
            fg_color="transparent",
            hover_color=UI_COLORS.BORDER_SUBTLE,
            text_color=UI_COLORS.TEXT_SECONDARY,
            font=ctk.CTkFont(size=16),
            command=self.toggle_sidebar,
        )
        self._toggle_btn.pack(side="left", padx=(0, SIZES["pad_small"]))

        self.module_label = ctk.CTkLabel(
            inner,
            text="Inicio",
            font=ctk.CTkFont(size=_FS["medium"], weight="bold"),
            text_color=UI_COLORS.TEXT,
        )
        self.module_label.pack(side="left")

        # User info (right)
        user_frame = ctk.CTkFrame(inner, fg_color="transparent")
        user_frame.pack(side="right")

        avatar = ctk.CTkFrame(
            user_frame,
            width=32,
            height=32,
            fg_color=UI_COLORS.PRIMARY,
            corner_radius=16,
        )
        avatar.pack(side="right", padx=(8, 0))
        avatar.pack_propagate(False)
        ctk.CTkLabel(
            avatar,
            text=self.username[:2].upper(),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#ffffff",
        ).place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(user_frame, fg_color="transparent")
        info.pack(side="right")
        ctk.CTkLabel(
            info,
            text=self.username.capitalize(),
            font=ctk.CTkFont(size=_FS["small"], weight="bold"),
            text_color=UI_COLORS.TEXT,
        ).pack(anchor="e")
        ctk.CTkLabel(
            info,
            text=self.role,
            font=ctk.CTkFont(size=_FS["micro"]),
            text_color=UI_COLORS.TEXT_MUTED,
        ).pack(anchor="e")

    # ── Nav helpers ───────────────────────────────────────────────────────────

    def _set_active_nav(self, index, module_name):
        for i, (btn, _) in enumerate(self.nav_buttons):
            if i == index:
                btn.configure(
                    fg_color=UI_COLORS.PRIMARY,
                    text_color="#ffffff",
                    font=ctk.CTkFont(size=_FS["large"], weight="bold"),
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=UI_COLORS.SIDEBAR_TEXT,
                    font=ctk.CTkFont(size=_FS["large"]),
                )
        self.module_label.configure(text=module_name)

    def _hide_current(self):
        if self.current_view is None:
            return
        if self._current_key == "home":
            self.current_view.destroy()
        else:
            self.current_view.pack_forget()
        self.current_view = None

    def _switch_to(self, key, factory, nav_idx, module_name):
        self._hide_current()
        self._set_active_nav(nav_idx, module_name)
        if key in self._view_cache:
            view = self._view_cache[key]
            view.pack(fill="both", expand=True)
            if hasattr(view, "refresh"):
                view.after(0, view.refresh)
        else:
            view = factory()
            self._view_cache[key] = view
        self.current_view = view
        self._current_key = key

    def _clear_content(self):
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None
        for v in self._view_cache.values():
            try:
                v.destroy()
            except Exception:
                pass
        self._view_cache.clear()
        self._current_key = None

    def show_home(self):
        self._hide_current()
        self._set_active_nav(0, "Inicio")
        nav_callbacks = {
            "inventory": self.show_inventory_view,
            "clients": self.show_clients_view,
            "services": self.show_services_view,
            "reports": self.show_reportes_view,
        }
        self.current_view = DashboardHome(
            self.main_content,
            nav_callbacks=nav_callbacks,
            user_info=self.user_info,
        )
        self._current_key = "home"

    def show_inventory_view(self):
        from ui.inventory_view import InventoryView
        self._switch_to(
            "inventory",
            lambda: InventoryView(self.main_content, self.user_info),
            1, "Inventario",
        )

    def show_clients_view(self):
        from ui.clients_view import ClientsView
        self._switch_to(
            "clients",
            lambda: ClientsView(self.main_content),
            2, "Clientes",
        )

    def show_services_view(self):
        from ui.services_view import ServicesView
        self._switch_to(
            "services",
            lambda: ServicesView(self.main_content, self.user_info),
            3, "Servicios",
        )

    def show_reportes_view(self):
        from ui.reports_view import ReportsView
        self._switch_to(
            "reports",
            lambda: ReportsView(self.main_content),
            4, "Reportes",
        )

    def show_users_view(self):
        from ui.users_view import UsersView
        self._switch_to(
            "users",
            lambda: UsersView(self.main_content, self.user_info),
            len(self.nav_buttons) - 1, "Usuarios",
        )

    def _on_logout_click(self):
        self._clear_content()
        self.on_logout()


# ── Dashboard Home ────────────────────────────────────────────────────────────


class DashboardHome(ctk.CTkFrame):
    def __init__(self, master, nav_callbacks=None, user_info=None):
        super().__init__(master, fg_color=AppTheme.BACKGROUND)
        self.pack(fill="both", expand=True)
        self._nav = nav_callbacks or {}
        self._username = user_info[1] if user_info else "sistema"
        self.stats = self._get_stats()
        self.recent_activity = self._get_recent_activity()
        self._build()
        self._bind_fkeys()

    def _build(self):
        pad = SIZES["pad_large"]
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=pad, pady=pad)

        self._build_stat_cards(content)  # top row, fixed height
        self._build_activity_panel(content)  # middle, expands
        self._build_quick_actions_bar(content)  # bottom bar, fixed height

    # ── Stat cards ────────────────────────────────────────────────────────────

    def _build_stat_cards(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, SIZES["pad"]))
        for i in range(4):
            row.grid_columnconfigure(i, weight=1)

        data = [
            ("Total Máquinas", self.stats["total"], "#EFF6FF", "#2563EB", "📦"),
            ("En Stock", self.stats["en_stock"], "#F0FDF4", "#16A34A", "🟢"),
            ("Instaladas", self.stats["instaladas"], "#FFFBEB", "#D97706", "🔧"),
            ("Clientes", self.stats["clientes"], "#FAF5FF", "#7C3AED", "👥"),
        ]
        for i, args in enumerate(data):
            _stat_card(row, i, *args)

    # ── Activity panel (full width, expandable) ───────────────────────────────

    def _build_activity_panel(self, parent):
        card = ctk.CTkFrame(
            parent,
            fg_color=UI_COLORS.CARD,
            corner_radius=SIZES["card_radius"],
            border_width=1,
            border_color=UI_COLORS.BORDER,
        )
        card.pack(fill="both", expand=True, pady=(0, SIZES["pad"]))

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=SIZES["pad"], pady=(SIZES["pad"], SIZES["pad_small"]))
        ctk.CTkLabel(
            hdr,
            text="Actividad Reciente",
            font=ctk.CTkFont(size=_ACT_FS["large"], weight="bold"),
            text_color=UI_COLORS.TEXT,
        ).pack(side="left")

        ctk.CTkFrame(card, height=1, fg_color=UI_COLORS.BORDER_SUBTLE).pack(
            fill="x", padx=SIZES["pad"]
        )

        sf = ctk.CTkScrollableFrame(
            card, fg_color="transparent", scrollbar_button_color=UI_COLORS.BORDER
        )
        sf.pack(
            fill="both", expand=True, padx=SIZES["pad_small"], pady=SIZES["pad_small"]
        )

        if not self.recent_activity:
            ctk.CTkLabel(
                sf,
                text="Sin actividad reciente",
                font=ctk.CTkFont(size=_ACT_FS["body"]),
                text_color=UI_COLORS.TEXT_MUTED,
            ).pack(pady=20)
        else:
            for act in self.recent_activity[:10]:
                self._activity_row(sf, act)

    def _activity_row(self, parent, activity):
        (
            tipo,
            serial,
            client_name,
            fecha,
            completion_date,
            m_status,
            applied_by,
            remarks,
            next_maint,
            serial_raw,
            model_name,
            distribuidor,
        ) = activity

        _SVC = {
            "Instalación": ("default", "🔧"),
            "Mantenimiento Preventivo": ("success", "🛠️"),
            "Reparación": ("warning", "⚙️"),
        }
        variant, icon = _SVC.get(tipo, ("neutral", "📋"))

        item = ctk.CTkFrame(
            parent,
            fg_color=UI_COLORS.CARD,
            corner_radius=8,
            border_width=1,
            border_color=UI_COLORS.BORDER,
        )
        item.pack(fill="x", pady=3)

        detail_data = (
            tipo,
            serial,
            client_name,
            fecha,
            completion_date,
            m_status,
            applied_by,
            remarks,
            next_maint,
            serial_raw,
            model_name,
            distribuidor,
        )

        def _on_click(_evt, d=detail_data):
            self._show_activity_detail(d)

        def _on_enter(_evt):
            item.configure(border_color=UI_COLORS.PRIMARY)

        def _on_leave(_evt):
            item.configure(border_color=UI_COLORS.BORDER)

        def _bind_tree(widget):
            widget.bind("<Button-1>", _on_click)
            widget.bind("<Enter>", _on_enter)
            widget.bind("<Leave>", _on_leave)
            for child in widget.winfo_children():
                _bind_tree(child)

        body = ctk.CTkFrame(item, fg_color="transparent")
        body.pack(fill="x", padx=SIZES["pad_small"], pady=SIZES["pad_small"])

        # ── Fila 1: badge tipo + estado + fecha
        row1 = ctk.CTkFrame(body, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 4))

        badge = ctk.CTkFrame(
            row1, fg_color=UI_COLORS.BADGE_BG[variant], corner_radius=6
        )
        badge.pack(side="left")
        ctk.CTkLabel(
            badge,
            text=f"{icon} {tipo}",
            font=ctk.CTkFont(size=_ACT_FS["tiny"], weight="bold"),
            text_color=UI_COLORS.BADGE_FG[variant],
        ).pack(padx=8, pady=3)

        # Estado para Mant/Rep
        if tipo in ("Mantenimiento Preventivo", "Reparación"):
            if m_status in ("En Mantenimiento", "En Reparación"):
                s_bg, s_fg, s_txt = "#FFFBEB", "#D97706", "⏳ Pendiente"
            else:
                s_bg, s_fg = "#F0FDF4", "#16A34A"
                s_txt = (
                    f"✓ Listo {completion_date}" if completion_date else "✓ Completado"
                )
            sb = ctk.CTkFrame(row1, fg_color=s_bg, corner_radius=6)
            sb.pack(side="left", padx=(6, 0))
            ctk.CTkLabel(
                sb,
                text=s_txt,
                font=ctk.CTkFont(size=_ACT_FS["tiny"], weight="bold"),
                text_color=s_fg,
            ).pack(padx=8, pady=3)

        ctk.CTkLabel(
            row1,
            text=f"📅 {fecha}",
            font=ctk.CTkFont(size=_ACT_FS["tiny"]),
            text_color=UI_COLORS.TEXT_MUTED,
        ).pack(side="right")

        # ── Fila 2: serial máquina
        ctk.CTkLabel(
            body,
            text=serial or "Sin máquina asignada",
            font=ctk.CTkFont(size=_ACT_FS["small"], weight="bold"),
            text_color=UI_COLORS.TEXT,
        ).pack(anchor="w")

        # ── Fila 3: cliente + aplicado por
        row3 = ctk.CTkFrame(body, fg_color="transparent")
        row3.pack(fill="x", pady=(2, 0))
        ctk.CTkLabel(
            row3,
            text=f"👤 Cliente: {client_name or 'Sin asignar'}",
            font=ctk.CTkFont(size=_ACT_FS["tiny"]),
            text_color=UI_COLORS.TEXT_SECONDARY,
        ).pack(side="left")
        ctk.CTkLabel(
            row3,
            text=f"Por: {applied_by}",
            font=ctk.CTkFont(size=_ACT_FS["tiny"]),
            text_color=UI_COLORS.TEXT_MUTED,
        ).pack(side="right")

        # bind después de construir todos los hijos
        item.after(10, lambda: _bind_tree(item))

    def _show_activity_detail(self, data):
        (
            tipo,
            serial,
            client_name,
            fecha,
            completion_date,
            m_status,
            applied_by,
            remarks,
            next_maint,
            serial_raw,
            model_name,
            distribuidor,
        ) = data

        _SVC_COLOR = {
            "Instalación": ("#EFF6FF", "#2563EB", "🔧"),
            "Mantenimiento Preventivo": ("#F0FDF4", "#16A34A", "🛠️"),
            "Reparación": ("#FFFBEB", "#D97706", "⚙️"),
        }
        t_bg, t_fg, t_icon = _SVC_COLOR.get(tipo, ("#F8FAFC", "#64748B", "📋"))

        dlg = ctk.CTkToplevel()
        dlg.title("")
        dlg.resizable(False, False)
        dlg.attributes("-topmost", True)
        dlg.configure(fg_color=UI_COLORS.CARD)
        dlg.after(50, dlg.grab_set)

        w, h = 620, 680
        dlg.update_idletasks()
        sx, sy = dlg.winfo_screenwidth(), dlg.winfo_screenheight()
        dlg.geometry(f"{w}x{h}+{(sx - w) // 2}+{(sy - h) // 2}")

        # Header
        hdr = ctk.CTkFrame(dlg, fg_color="#2A3550", corner_radius=0, height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(
            hdr,
            text=f"{t_icon}  Detalle de Actividad",
            font=ctk.CTkFont(size=_FS["medium"], weight="bold"),
            text_color="#ffffff",
        ).pack(side="left", padx=20)

        body = ctk.CTkScrollableFrame(
            dlg, fg_color="transparent", scrollbar_button_color=UI_COLORS.BORDER
        )
        body.pack(fill="both", expand=True, padx=20, pady=16)

        def _section(title):
            ctk.CTkLabel(
                body,
                text=title,
                font=ctk.CTkFont(size=_FS["small"], weight="bold"),
                text_color=UI_COLORS.TEXT_SECONDARY,
            ).pack(anchor="w", pady=(12, 4))
            ctk.CTkFrame(body, height=1, fg_color=UI_COLORS.BORDER_SUBTLE).pack(
                fill="x"
            )

        def _row(label, value, value_color=None):
            r = ctk.CTkFrame(body, fg_color="transparent")
            r.pack(fill="x", pady=3)
            ctk.CTkLabel(
                r,
                text=label,
                width=160,
                anchor="w",
                font=ctk.CTkFont(size=_FS["small"]),
                text_color=UI_COLORS.TEXT_MUTED,
            ).pack(side="left")
            ctk.CTkLabel(
                r,
                text=str(value) if value else "—",
                anchor="w",
                font=ctk.CTkFont(size=_FS["body"], weight="bold"),
                text_color=value_color or UI_COLORS.TEXT,
            ).pack(side="left")

        # Tipo badge
        top = ctk.CTkFrame(body, fg_color="transparent")
        top.pack(fill="x", pady=(0, 8))
        badge = ctk.CTkFrame(top, fg_color=t_bg, corner_radius=6)
        badge.pack(side="left")
        ctk.CTkLabel(
            badge,
            text=f"{t_icon}  {tipo}",
            font=ctk.CTkFont(size=_FS["body"], weight="bold"),
            text_color=t_fg,
        ).pack(padx=12, pady=5)

        # Estado badge (Mant/Rep)
        if tipo in ("Mantenimiento Preventivo", "Reparación"):
            if m_status in ("En Mantenimiento", "En Reparación"):
                s_bg, s_fg, s_txt = "#FFFBEB", "#D97706", "⏳ Pendiente"
            else:
                s_bg, s_fg = "#F0FDF4", "#16A34A"
                s_txt = (
                    f"✓ Listo — {completion_date}"
                    if completion_date
                    else "✓ Completado"
                )
            sb = ctk.CTkFrame(top, fg_color=s_bg, corner_radius=6)
            sb.pack(side="left", padx=(8, 0))
            ctk.CTkLabel(
                sb,
                text=s_txt,
                font=ctk.CTkFont(size=_FS["body"], weight="bold"),
                text_color=s_fg,
            ).pack(padx=12, pady=5)

        # Sección: Servicio
        _section("Información del Servicio")
        _row("Fecha de servicio:", fecha)
        _row("Próximo mantenimiento:", next_maint or "No programado")
        if completion_date:
            _row("Fecha de culminación:", completion_date, "#16A34A")
        _row("Aplicado por:", applied_by)

        # Sección: Máquina
        _section("Máquina")
        _row("Serial:", serial_raw or "—")
        _row("Modelo:", model_name)
        _row("Proveedor:", distribuidor)
        _row("Estado:", m_status, UI_COLORS.STATUS_COLORS.get(m_status, UI_COLORS.TEXT))

        # Sección: Cliente
        _section("Cliente")
        _row("Nombre:", client_name or "Sin asignar")

        # Sección: Observaciones
        if remarks:
            _section("Observaciones")
            obs = ctk.CTkFrame(
                body,
                fg_color="#F8FAFC",
                corner_radius=6,
                border_width=1,
                border_color=UI_COLORS.BORDER_SUBTLE,
            )
            obs.pack(fill="x", pady=(4, 0))
            ctk.CTkLabel(
                obs,
                text=remarks,
                font=ctk.CTkFont(size=_FS["small"]),
                text_color=UI_COLORS.TEXT,
                wraplength=520,
                justify="left",
            ).pack(padx=12, pady=10)

        # Botón cerrar
        ctk.CTkButton(
            dlg,
            text="Cerrar",
            command=dlg.destroy,
            fg_color=UI_COLORS.BORDER_SUBTLE,
            hover_color=UI_COLORS.BORDER,
            text_color=UI_COLORS.TEXT_SECONDARY,
            font=ctk.CTkFont(size=_FS["body"]),
            corner_radius=SIZES["button_radius"],
            height=SIZES["button_height"],
        ).pack(fill="x", padx=20, pady=(0, 16))

    # ── F-key bindings ────────────────────────────────────────────────────────

    def _bind_fkeys(self):
        root = self.winfo_toplevel()
        fkey_map = {
            "<F1>": self._open_machine_dlg,
            "<F2>": self._open_client_dlg,
            "<F3>": self._open_service_dlg,
            "<F4>": self._nav.get("reports"),
        }
        for key, cb in fkey_map.items():
            if cb:
                root.bind(key, lambda e, fn=cb: fn())

        def _unbind(_e):
            for key in fkey_map:
                root.unbind(key)

        self.bind("<Destroy>", _unbind)

    # ── Quick actions horizontal bar (bottom) ─────────────────────────────────

    def _build_quick_actions_bar(self, parent):
        bar = ctk.CTkFrame(
            parent,
            fg_color=UI_COLORS.CARD,
            corner_radius=SIZES["card_radius"],
            border_width=1,
            border_color=UI_COLORS.BORDER,
            height=68,
        )
        bar.pack(fill="x")
        bar.pack_propagate(False)

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=SIZES["pad"], pady=SIZES["pad_small"])

        label = ctk.CTkLabel(
            inner,
            text="Acciones rápidas",
            font=ctk.CTkFont(size=_FS["small"]),
            text_color=UI_COLORS.TEXT_MUTED,
        )
        label.pack(side="left", padx=(0, SIZES["pad"]))

        actions = [
            (
                "📦  Nueva Máquina  [F1]",
                UI_COLORS.PRIMARY,
                UI_COLORS.SECONDARY,
                self._open_machine_dlg,
            ),
            ("👥  Nuevo Cliente  [F2]", "#319795", "#267a7a", self._open_client_dlg),
            (
                "🔧  Registrar Servicio  [F3]",
                "#D97706",
                "#b86200",
                self._open_service_dlg,
            ),
            ("📊  Ver Reportes  [F4]", "#16A34A", "#138a3e", self._nav.get("reports")),
        ]
        for text, fg, hover, cmd in actions:
            ctk.CTkButton(
                inner,
                text=text,
                fg_color=fg,
                hover_color=hover,
                text_color="#ffffff",
                font=ctk.CTkFont(size=_FS["small"], weight="bold"),
                height=SIZES["button_height"],
                corner_radius=SIZES["button_radius"],
                command=cmd,
            ).pack(side="left", padx=(0, SIZES["pad_small"]), fill="y")

    # ── DB helpers ────────────────────────────────────────────────────────────

    @staticmethod
    def _get_stats():
        s = {"total": 0, "en_stock": 0, "instaladas": 0, "clientes": 0}
        if not os.path.exists(DB_PATH):
            return s
        conn = sqlite3.connect(DB_PATH)
        s["total"] = conn.execute("SELECT COUNT(*) FROM machines").fetchone()[0]
        s["en_stock"] = conn.execute(
            "SELECT COUNT(*) FROM machines WHERE status='En Stock'"
        ).fetchone()[0]
        s["instaladas"] = conn.execute(
            "SELECT COUNT(*) FROM machines WHERE status='Instalada'"
        ).fetchone()[0]
        s["clientes"] = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
        conn.close()
        return s

    @staticmethod
    def _get_recent_activity():
        if not os.path.exists(DB_PATH):
            return []
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute("""
            SELECT s.service_type,
                   m.serial_number || '  (' || COALESCE(mo.model_name, '?') || ')',
                   c.name,
                   s.service_date,
                   s.completion_date,
                   m.status,
                   COALESCE(u.first_name || ' ' || u.last_name, s.applied_by, 'desconocido'),
                   s.remarks,
                   s.next_maintenance_date,
                   m.serial_number,
                   COALESCE(mo.model_name, '—'),
                   COALESCE(d.name, '—')
            FROM services s
            LEFT JOIN machines m ON s.machine_id = m.id
            LEFT JOIN machine_models mo ON m.model_id = mo.id
            LEFT JOIN clients c ON m.client_id = c.id
            LEFT JOIN distributors d ON m.distributor_id = d.id
            LEFT JOIN users u ON s.applied_by = u.username
            ORDER BY s.service_date DESC, s.id DESC LIMIT 15
        """).fetchall()
        conn.close()
        return rows

    # ── Widget helpers (shared by dialogs) ───────────────────────────────────

    @staticmethod
    def _dlg_lbl(parent, text):
        ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=_FS["small"], weight="bold"),
            text_color=UI_COLORS.TEXT_SECONDARY,
        ).pack(anchor="w", pady=(0, 4))

    @staticmethod
    def _dlg_entry(parent, placeholder):
        e = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=SIZES["entry_height"],
            corner_radius=SIZES["button_radius"],
            border_width=SIZES["border_width"],
            border_color=UI_COLORS.BORDER,
            fg_color="#F8FAFC",
            text_color=UI_COLORS.TEXT,
            placeholder_text_color=UI_COLORS.TEXT_MUTED,
        )
        e.pack(fill="x", pady=(0, SIZES["pad"]))
        return e

    @staticmethod
    def _dlg_combo(parent, values, state="readonly"):
        c = ctk.CTkComboBox(
            parent,
            values=values,
            height=SIZES["entry_height"],
            corner_radius=SIZES["button_radius"],
            state=state,
            fg_color="#F8FAFC",
            text_color=UI_COLORS.TEXT,
            button_color=UI_COLORS.BORDER,
            button_hover_color=UI_COLORS.PRIMARY,
            dropdown_fg_color="white",
            dropdown_text_color=UI_COLORS.TEXT,
            border_color=UI_COLORS.BORDER,
        )
        c.pack(fill="x", pady=(0, SIZES["pad"]))
        return c

    @staticmethod
    def _dlg_window(title, icon, w, h):
        dlg = ctk.CTkToplevel()
        dlg.title("")
        dlg.resizable(False, False)
        dlg.attributes("-topmost", True)
        dlg.configure(fg_color=UI_COLORS.CARD)
        dlg.after(50, dlg.grab_set)
        dlg.update_idletasks()
        sx, sy = dlg.winfo_screenwidth(), dlg.winfo_screenheight()
        dlg.geometry(f"{w}x{h}+{(sx - w) // 2}+{(sy - h) // 2}")
        # Header
        hdr = ctk.CTkFrame(dlg, fg_color="#2A3550", corner_radius=0, height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        row = ctk.CTkFrame(hdr, fg_color="transparent")
        row.pack(fill="both", expand=True, padx=16)
        ctk.CTkLabel(row, text=icon, font=ctk.CTkFont(size=20)).pack(
            side="left", padx=(0, 10)
        )
        ctk.CTkLabel(
            row,
            text=title,
            font=ctk.CTkFont(size=_FS["medium"], weight="bold"),
            text_color="#ffffff",
        ).pack(side="left")
        # Scrollable body
        body = ctk.CTkScrollableFrame(
            dlg, fg_color="transparent", scrollbar_button_color=UI_COLORS.BORDER
        )
        body.pack(fill="both", expand=True, padx=SIZES["pad_large"], pady=SIZES["pad"])
        return dlg, body

    # ── Dialog: Nueva Máquina ────────────────────────────────────────────────

    def _open_machine_dlg(self):
        from datetime import date as _date

        dlg, body = self._dlg_window("Nueva Máquina Fiscal", "📦", 720, 640)

        # Load reference data
        conn = sqlite3.connect(DB_PATH)
        models_by_brand = {}
        distrib_dict = {}
        for mid, brand, model_name in conn.execute(
            "SELECT id, brand, model_name FROM machine_models ORDER BY brand, model_name"
        ):
            models_by_brand.setdefault(brand, {})[model_name] = mid
        for r in conn.execute("SELECT id, name FROM distributors ORDER BY name"):
            distrib_dict[r[1]] = r[0]
        conn.close()

        self._dlg_lbl(body, "Proveedor")
        prov_list = list(distrib_dict.keys()) or ["Sin proveedores"]
        prov_combo = self._dlg_combo(body, prov_list)

        self._dlg_lbl(body, "Modelo")
        model_combo = self._dlg_combo(body, [""], state="normal")

        def on_prov(val):
            modelos = list(models_by_brand.get(val, {}).keys())
            model_combo.configure(values=modelos if modelos else [""])
            model_combo.set("")

        prov_combo.configure(command=on_prov)
        if prov_list:
            on_prov(prov_list[0])
            prov_combo.set(prov_list[0])

        self._dlg_lbl(body, "Serial")
        serial_e = self._dlg_entry(body, "Número de serial")

        self._dlg_lbl(body, "Reg. SENIAT  *")
        reg_e = self._dlg_entry(body, "Nro. Registro SENIAT")

        msg_lbl = ctk.CTkLabel(body, text="", font=ctk.CTkFont(size=_FS["tiny"]))
        msg_lbl.pack()

        def _field_err(widget, msg):
            widget.configure(border_color=UI_COLORS.DANGER)
            msg_lbl.configure(text=msg, text_color=UI_COLORS.DANGER)

        def _reset_borders():
            for w in (serial_e, reg_e):
                w.configure(border_color=UI_COLORS.BORDER)
            msg_lbl.configure(text="")

        def save():
            prov = prov_combo.get()
            modelo = model_combo.get().strip()
            serial = serial_e.get().strip()
            reg = reg_e.get().strip()
            _reset_borders()
            if not modelo:
                msg_lbl.configure(
                    text="⚠  Seleccione el modelo", text_color=UI_COLORS.DANGER
                )
                return
            if not serial:
                _field_err(serial_e, "⚠  Serial obligatorio")
                return
            if not reg:
                _field_err(reg_e, "⚠  Reg. SENIAT obligatorio")
                return
            serial_full = f"{serial} | Reg.SENIAT:{reg}"
            distrib_id = distrib_dict.get(prov)
            conn2 = None
            try:
                conn2 = sqlite3.connect(DB_PATH)
                existing = conn2.execute(
                    "SELECT id FROM machine_models WHERE brand=? AND model_name=?",
                    (prov, modelo),
                ).fetchone()
                model_id = (
                    existing[0]
                    if existing
                    else conn2.execute(
                        "INSERT INTO machine_models (brand, model_name) VALUES (?,?)",
                        (prov, modelo),
                    ).lastrowid
                )
                conn2.execute(
                    "INSERT INTO machines (serial_number, model_id, distributor_id, status) "
                    "VALUES (?, ?, ?, 'En Stock')",
                    (serial_full, model_id, distrib_id),
                )
                conn2.commit()
                msg_lbl.configure(
                    text="✓  Máquina registrada", text_color=UI_COLORS.GREEN
                )
                serial_e.delete(0, "end")
                reg_e.delete(0, "end")
            except sqlite3.IntegrityError:
                msg_lbl.configure(
                    text="⚠  Serial ya existe", text_color=UI_COLORS.DANGER
                )
            except Exception:
                msg_lbl.configure(text="⚠  Error interno", text_color=UI_COLORS.DANGER)
            finally:
                if conn2:
                    conn2.close()

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(
            fill="x", padx=SIZES["pad_large"], pady=(SIZES["pad_small"], SIZES["pad"])
        )
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            btn_row,
            text="Cerrar",
            command=dlg.destroy,
            fg_color=UI_COLORS.BORDER_SUBTLE,
            hover_color=UI_COLORS.BORDER,
            text_color=UI_COLORS.TEXT_SECONDARY,
            font=ctk.CTkFont(size=_FS["small"]),
            corner_radius=SIZES["button_radius"],
            height=SIZES["button_height"],
        ).grid(row=0, column=0, sticky="ew", padx=(0, SIZES["pad_small"]))

        ctk.CTkButton(
            btn_row,
            text="✓  Registrar en Inventario",
            command=save,
            fg_color=UI_COLORS.PRIMARY,
            hover_color=UI_COLORS.SECONDARY,
            text_color="#ffffff",
            font=ctk.CTkFont(size=_FS["body"], weight="bold"),
            corner_radius=SIZES["button_radius"],
            height=SIZES["button_height"],
        ).grid(row=0, column=1, sticky="ew")

    # ── Dialog: Nuevo Cliente ────────────────────────────────────────────────

    def _open_client_dlg(self):
        dlg, body = self._dlg_window("Nuevo Cliente", "👥", 700, 600)

        # ── Documento: [prefix combo] [-] [number entry]
        self._dlg_lbl(body, "Documento (RIF/RUT)")
        doc_row = ctk.CTkFrame(body, fg_color="transparent")
        doc_row.pack(fill="x", pady=(0, SIZES["pad"]))

        prefix_combo = ctk.CTkComboBox(
            doc_row,
            values=["J", "C", "V", "G", "E"],
            width=72,
            height=SIZES["entry_height"],
            state="readonly",
            corner_radius=SIZES["button_radius"],
            fg_color="#F8FAFC",
            text_color=UI_COLORS.TEXT,
            button_color=UI_COLORS.BORDER,
            button_hover_color=UI_COLORS.PRIMARY,
            dropdown_fg_color="white",
            dropdown_text_color=UI_COLORS.TEXT,
            border_color=UI_COLORS.BORDER,
            font=ctk.CTkFont(size=_FS["body"], weight="bold"),
        )
        prefix_combo.set("J")
        prefix_combo.pack(side="left")

        ctk.CTkLabel(
            doc_row,
            text=" - ",
            font=ctk.CTkFont(size=_FS["body"]),
            text_color=UI_COLORS.TEXT_MUTED,
        ).pack(side="left")

        doc_num_e = ctk.CTkEntry(
            doc_row,
            placeholder_text="12345678-9",
            height=SIZES["entry_height"],
            corner_radius=SIZES["button_radius"],
            border_width=SIZES["border_width"],
            border_color=UI_COLORS.BORDER,
            fg_color="#F8FAFC",
            text_color=UI_COLORS.TEXT,
            placeholder_text_color=UI_COLORS.TEXT_MUTED,
        )
        doc_num_e.pack(side="left", fill="x", expand=True)

        self._dlg_lbl(body, "Nombre / Razón Social")
        name_e = self._dlg_entry(body, "Empresa SA")

        # ── Teléfono: solo dígitos
        self._dlg_lbl(body, "Teléfono")
        phone_var = ctk.StringVar()
        phone_e = ctk.CTkEntry(
            body,
            textvariable=phone_var,
            placeholder_text="04140000000",
            height=SIZES["entry_height"],
            corner_radius=SIZES["button_radius"],
            border_width=SIZES["border_width"],
            border_color=UI_COLORS.BORDER,
            fg_color="#F8FAFC",
            text_color=UI_COLORS.TEXT,
            placeholder_text_color=UI_COLORS.TEXT_MUTED,
        )
        phone_e.pack(fill="x", pady=(0, SIZES["pad"]))

        def _digits_only(*_):
            val = phone_var.get()
            clean = "".join(c for c in val if c.isdigit())
            if clean != val:
                phone_var.set(clean)

        phone_var.trace("w", _digits_only)

        self._dlg_lbl(body, "Dirección")
        addr_e = self._dlg_entry(body, "Dirección completa")

        msg_lbl = ctk.CTkLabel(
            body,
            text="",
            font=ctk.CTkFont(size=_FS["tiny"]),
            wraplength=520,
            justify="left",
        )
        msg_lbl.pack(pady=(0, SIZES["pad_small"]))

        def _clear_field_err(widget):
            def _cb(_e):
                widget.configure(border_color=UI_COLORS.BORDER)
                if msg_lbl.cget("text_color") == UI_COLORS.DANGER:
                    msg_lbl.configure(text="")

            widget.bind("<KeyRelease>", _cb)

        for w in (doc_num_e, name_e, phone_e, addr_e):
            _clear_field_err(w)

        def save():
            doc_num = doc_num_e.get().strip()
            doc = f"{prefix_combo.get()}-{doc_num}" if doc_num else ""
            name = name_e.get().strip()
            phone = phone_var.get().strip()
            addr = addr_e.get().strip()

            for w in (doc_num_e, name_e, phone_e, addr_e):
                w.configure(border_color=UI_COLORS.BORDER)
            msg_lbl.configure(text="")

            errors = []
            if not doc_num:
                doc_num_e.configure(border_color=UI_COLORS.DANGER)
                errors.append("número de documento")
            if not name:
                name_e.configure(border_color=UI_COLORS.DANGER)
                errors.append("nombre")
            if not phone:
                phone_e.configure(border_color=UI_COLORS.DANGER)
                errors.append("teléfono")
            if not addr:
                addr_e.configure(border_color=UI_COLORS.DANGER)
                errors.append("dirección")
            if errors:
                msg_lbl.configure(
                    text=f"⚠  Requerido: {', '.join(errors)}",
                    text_color=UI_COLORS.DANGER,
                )
                return

            conn = None
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute(
                    "INSERT INTO clients (document_id, name, address, phone) VALUES (?, ?, ?, ?)",
                    (doc, name, addr, phone),
                )
                conn.commit()
                doc_num_e.delete(0, "end")
                name_e.delete(0, "end")
                phone_var.set("")
                addr_e.delete(0, "end")
                msg_lbl.configure(
                    text="✓  Cliente registrado", text_color=UI_COLORS.GREEN
                )
            except sqlite3.IntegrityError:
                doc_num_e.configure(border_color=UI_COLORS.DANGER)
                msg_lbl.configure(
                    text="⚠  El documento ya existe", text_color=UI_COLORS.DANGER
                )
            except Exception:
                msg_lbl.configure(text="⚠  Error interno", text_color=UI_COLORS.DANGER)
            finally:
                if conn:
                    conn.close()

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(
            fill="x", padx=SIZES["pad_large"], pady=(SIZES["pad_small"], SIZES["pad"])
        )
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            btn_row,
            text="Cerrar",
            command=dlg.destroy,
            fg_color=UI_COLORS.BORDER_SUBTLE,
            hover_color=UI_COLORS.BORDER,
            text_color=UI_COLORS.TEXT_SECONDARY,
            font=ctk.CTkFont(size=_FS["small"]),
            corner_radius=SIZES["button_radius"],
            height=SIZES["button_height"],
        ).grid(row=0, column=0, sticky="ew", padx=(0, SIZES["pad_small"]))

        ctk.CTkButton(
            btn_row,
            text="✓  Registrar Cliente",
            command=save,
            fg_color=UI_COLORS.PRIMARY,
            hover_color=UI_COLORS.SECONDARY,
            text_color="#ffffff",
            font=ctk.CTkFont(size=_FS["body"], weight="bold"),
            corner_radius=SIZES["button_radius"],
            height=SIZES["button_height"],
        ).grid(row=0, column=1, sticky="ew")

    # ── Dialog: Registrar Servicio ───────────────────────────────────────────

    def _open_service_dlg(self):
        from datetime import date as _date, datetime as _dt

        dlg, body = self._dlg_window("Registrar Servicio", "🔧", 820, 660)

        # ── Load reference data ───────────────────────────────────────────────
        conn = sqlite3.connect(DB_PATH)
        clients_dict = {}
        machines_dict = {}
        for r in conn.execute("SELECT id, name FROM clients ORDER BY name"):
            clients_dict[r[1]] = r[0]
        for mid, serial, model_name, client_id, status in conn.execute("""
            SELECT m.id, m.serial_number, COALESCE(mo.model_name,'?'), m.client_id, m.status
            FROM machines m
            LEFT JOIN machine_models mo ON m.model_id = mo.id
            WHERE m.status != 'Desincorporada' ORDER BY m.serial_number
        """):
            machines_dict[f"{serial}  ({model_name})"] = (mid, client_id, status)
        conn.close()

        available_machines = list(machines_dict.keys())

        def _card(parent, title):
            c = ctk.CTkFrame(
                parent,
                fg_color=UI_COLORS.CARD,
                corner_radius=SIZES["card_radius"],
                border_width=1,
                border_color=UI_COLORS.BORDER,
            )
            ctk.CTkLabel(
                c,
                text=title,
                font=ctk.CTkFont(size=_FS["tiny"], weight="bold"),
                text_color=UI_COLORS.TEXT_MUTED,
            ).pack(anchor="w", padx=SIZES["pad"], pady=(SIZES["pad_small"], 4))
            ctk.CTkFrame(c, height=1, fg_color=UI_COLORS.BORDER_SUBTLE).pack(
                fill="x", padx=SIZES["pad"]
            )
            inner = ctk.CTkFrame(c, fg_color="transparent")
            inner.pack(
                fill="both", expand=True, padx=SIZES["pad"], pady=SIZES["pad_small"]
            )
            return c, inner

        # ── Fila superior: Servicio (izq) | Fechas (der) ──────────────────────
        top_row = ctk.CTkFrame(body, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, SIZES["pad_small"]))
        top_row.grid_columnconfigure(0, weight=1)
        top_row.grid_columnconfigure(1, weight=1)

        svc_card, svc_inner = _card(top_row, "SERVICIO")
        svc_card.grid(row=0, column=0, sticky="nsew", padx=(0, SIZES["pad_small"]))

        dates_card, dates_inner = _card(top_row, "FECHAS")
        dates_card.grid(row=0, column=1, sticky="nsew", padx=(SIZES["pad_small"], 0))

        # Servicio: tipo + máquina
        self._dlg_lbl(svc_inner, "Tipo de Servicio")
        type_combo = self._dlg_combo(
            svc_inner, ["Instalación", "Mantenimiento Preventivo", "Reparación"]
        )

        self._dlg_lbl(svc_inner, "Máquina")
        machine_combo = self._dlg_combo(svc_inner, list(machines_dict.keys()) or [""])

        # Fechas: servicio + próximo mantenimiento
        self._dlg_lbl(dates_inner, "Fecha de Servicio")
        svc_date_e = ctk.CTkEntry(
            dates_inner,
            placeholder_text="YYYY-MM-DD",
            height=SIZES["entry_height"],
            corner_radius=SIZES["button_radius"],
            border_width=SIZES["border_width"],
            border_color=UI_COLORS.BORDER,
            fg_color="#F8FAFC",
            text_color=UI_COLORS.TEXT,
            placeholder_text_color=UI_COLORS.TEXT_MUTED,
        )
        svc_date_e.pack(fill="x", pady=(0, SIZES["pad"]))
        svc_date_e.insert(0, _date.today().strftime("%Y-%m-%d"))

        self._dlg_lbl(dates_inner, "Próximo Mantenimiento")
        next_maint_e = ctk.CTkEntry(
            dates_inner,
            placeholder_text="YYYY-MM-DD (opcional)",
            height=SIZES["entry_height"],
            corner_radius=SIZES["button_radius"],
            border_width=SIZES["border_width"],
            border_color=UI_COLORS.BORDER,
            fg_color="#F8FAFC",
            text_color=UI_COLORS.TEXT,
            placeholder_text_color=UI_COLORS.TEXT_MUTED,
        )
        next_maint_e.pack(fill="x", pady=(0, SIZES["pad"]))

        # ── Cliente (solo Instalación) — card oculto, se inserta after top_row ─
        client_card, client_inner = _card(body, "CLIENTE — INSTALACIÓN")

        self._dlg_lbl(client_inner, "Cliente")
        client_combo = ctk.CTkComboBox(
            client_inner,
            values=list(clients_dict.keys()) or [""],
            height=SIZES["entry_height"],
            corner_radius=SIZES["button_radius"],
            state="readonly",
            fg_color="#F8FAFC",
            text_color=UI_COLORS.TEXT,
            button_color=UI_COLORS.BORDER,
            button_hover_color=UI_COLORS.PRIMARY,
            dropdown_fg_color="white",
            dropdown_text_color=UI_COLORS.TEXT,
            border_color=UI_COLORS.BORDER,
        )
        client_combo.pack(fill="x", pady=(0, SIZES["pad_small"]))

        # ── Observaciones ─────────────────────────────────────────────────────
        obs_card, obs_inner = _card(body, "OBSERVACIONES")
        obs_card.pack(fill="x", pady=(0, SIZES["pad_small"]))

        remarks_tb = ctk.CTkTextbox(
            obs_inner,
            height=80,
            corner_radius=SIZES["button_radius"],
            fg_color="#F8FAFC",
            text_color=UI_COLORS.TEXT,
            border_width=SIZES["border_width"],
            border_color=UI_COLORS.BORDER,
        )
        remarks_tb.pack(fill="x", pady=(0, SIZES["pad_small"]))

        msg_lbl = ctk.CTkLabel(
            body,
            text="",
            font=ctk.CTkFont(size=_FS["tiny"]),
            wraplength=720,
            justify="left",
        )
        msg_lbl.pack(pady=(0, SIZES["pad_small"]))

        def on_type(value):
            nonlocal available_machines
            try:
                svc_dt = _dt.strptime(svc_date_e.get().strip(), "%Y-%m-%d").date()
            except ValueError:
                svc_dt = _date.today()
            nxt_auto = svc_dt.replace(year=svc_dt.year + 1).strftime("%Y-%m-%d")

            if value == "Instalación":
                available_machines = [
                    k for k, v in machines_dict.items() if v[2] == "En Stock"
                ]
                client_card.pack(fill="x", pady=(0, SIZES["pad_small"]), after=top_row)
                client_combo.set("")
                next_maint_e.delete(0, "end")
                next_maint_e.insert(0, nxt_auto)
            elif value == "Mantenimiento Preventivo":
                available_machines = [
                    k for k, v in machines_dict.items() if v[2] == "Instalada"
                ]
                client_card.pack_forget()
                next_maint_e.delete(0, "end")
                next_maint_e.insert(0, nxt_auto)
            else:
                available_machines = [
                    k for k, v in machines_dict.items() if v[2] == "Instalada"
                ]
                client_card.pack_forget()
                next_maint_e.delete(0, "end")

            machine_combo.configure(
                values=available_machines if available_machines else [""]
            )
            machine_combo.set("")

        type_combo.configure(command=on_type)

        def _field_err(widget, msg):
            widget.configure(border_color=UI_COLORS.DANGER)
            msg_lbl.configure(text=msg, text_color=UI_COLORS.DANGER)

        def _reset_borders():
            for w in (svc_date_e, next_maint_e):
                w.configure(border_color=UI_COLORS.BORDER)
            machine_combo.configure(border_color=UI_COLORS.BORDER)
            msg_lbl.configure(text="")

        def save():
            stype = type_combo.get()
            machine = machine_combo.get()
            svc_dt = svc_date_e.get().strip()
            nxt = next_maint_e.get().strip()
            remarks = remarks_tb.get("1.0", "end").strip()
            _reset_borders()

            if not stype:
                msg_lbl.configure(
                    text="⚠  Seleccione tipo de servicio", text_color=UI_COLORS.DANGER
                )
                return
            if not machine or machine not in machines_dict:
                _field_err(machine_combo, "⚠  Seleccione una máquina válida")
                return
            try:
                _dt.strptime(svc_dt, "%Y-%m-%d")
            except ValueError:
                _field_err(svc_date_e, "⚠  Fecha inválida (YYYY-MM-DD)")
                return
            if nxt:
                try:
                    _dt.strptime(nxt, "%Y-%m-%d")
                except ValueError:
                    _field_err(next_maint_e, "⚠  Fecha próximo mantenimiento inválida")
                    return

            machine_id, client_id_cur, m_status = machines_dict[machine]

            if stype == "Instalación":
                sel_client = client_combo.get().strip()
                if not sel_client or sel_client not in clients_dict:
                    msg_lbl.configure(
                        text="⚠  Instalación requiere cliente",
                        text_color=UI_COLORS.DANGER,
                    )
                    return
                if m_status != "En Stock":
                    msg_lbl.configure(
                        text="⚠  Solo máquinas 'En Stock' pueden instalarse",
                        text_color=UI_COLORS.DANGER,
                    )
                    return
                new_client_id = clients_dict[sel_client]
                new_status = "Instalada"
            elif stype in ("Mantenimiento Preventivo", "Reparación"):
                if m_status != "Instalada":
                    msg_lbl.configure(
                        text=f"⚠  {stype} solo aplica a máquinas instaladas",
                        text_color=UI_COLORS.DANGER,
                    )
                    return
                new_client_id = None
                new_status = (
                    "En Mantenimiento"
                    if stype == "Mantenimiento Preventivo"
                    else "En Reparación"
                )
            else:
                new_client_id = None
                new_status = None

            conn2 = None
            try:
                conn2 = sqlite3.connect(DB_PATH)
                conn2.execute(
                    "INSERT INTO services (machine_id, service_type, service_date, "
                    "next_maintenance_date, remarks, applied_by) VALUES (?,?,?,?,?,?)",
                    (
                        machine_id,
                        stype,
                        svc_dt,
                        nxt or None,
                        remarks or None,
                        self._username,
                    ),
                )
                if stype == "Instalación":
                    conn2.execute(
                        "UPDATE machines SET status='Instalada', client_id=? WHERE id=?",
                        (new_client_id, machine_id),
                    )
                elif new_status:
                    conn2.execute(
                        "UPDATE machines SET status=? WHERE id=?",
                        (new_status, machine_id),
                    )
                conn2.commit()
                msg_lbl.configure(
                    text="✓  Servicio registrado", text_color=UI_COLORS.GREEN
                )
                type_combo.set("")
                machine_combo.set("")
                client_combo.set("")
                client_card.pack_forget()
                next_maint_e.delete(0, "end")
                remarks_tb.delete("1.0", "end")
                machines_dict.clear()
                for mid2, ser2, mn2, cid2, st2 in conn2.execute("""
                    SELECT m.id, m.serial_number, COALESCE(mo.model_name,'?'),
                           m.client_id, m.status
                    FROM machines m
                    LEFT JOIN machine_models mo ON m.model_id = mo.id
                    WHERE m.status != 'Desincorporada' ORDER BY m.serial_number
                """):
                    machines_dict[f"{ser2}  ({mn2})"] = (mid2, cid2, st2)
            except Exception:
                msg_lbl.configure(
                    text="⚠  Error al registrar", text_color=UI_COLORS.DANGER
                )
            finally:
                if conn2:
                    conn2.close()

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(
            fill="x", padx=SIZES["pad_large"], pady=(SIZES["pad_small"], SIZES["pad"])
        )
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            btn_row,
            text="Cerrar",
            command=dlg.destroy,
            fg_color=UI_COLORS.BORDER_SUBTLE,
            hover_color=UI_COLORS.BORDER,
            text_color=UI_COLORS.TEXT_SECONDARY,
            font=ctk.CTkFont(size=_FS["small"]),
            corner_radius=SIZES["button_radius"],
            height=SIZES["button_height"],
        ).grid(row=0, column=0, sticky="ew", padx=(0, SIZES["pad_small"]))

        ctk.CTkButton(
            btn_row,
            text="✓  Registrar Servicio",
            command=save,
            fg_color=UI_COLORS.PRIMARY,
            hover_color=UI_COLORS.SECONDARY,
            text_color="#ffffff",
            font=ctk.CTkFont(size=_FS["body"], weight="bold"),
            corner_radius=SIZES["button_radius"],
            height=SIZES["button_height"],
        ).grid(row=0, column=1, sticky="ew")
