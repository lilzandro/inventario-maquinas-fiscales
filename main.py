import customtkinter as ctk
from theme import AppTheme, apply_global_theme, UI_COLORS
from ui.login_view import LoginView
from ui.dashboard_view import DashboardView

ctk.deactivate_automatic_dpi_awareness()
apply_global_theme()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.configure(fg_color=UI_COLORS.BASE)
        
        self.title("Adamo — Corporación Adamo Gentile C.A")
        self.geometry("1024x768")
        self.minsize(800, 600)

        self.current_view = None
        self.show_login()

    def show_login(self):
        if self.current_view:
            self.current_view.destroy()

        self.current_view = LoginView(self, self.on_login_success)

    def on_login_success(self, user_info):
        if self.current_view:
            self.current_view.destroy()

        self.current_view = DashboardView(self, user_info, self.show_login)


if __name__ == "__main__":
    app = App()
    app.mainloop()
