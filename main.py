import customtkinter as ctk
from ui.login_view import LoginView
from ui.dashboard_view import DashboardView, COLORS

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Gestión de Máquinas Fiscales")
        self.geometry("1024x768")
        self.minsize(800, 600)
        self.configure(fg_color=COLORS["bg_gray"])

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
