import customtkinter as ctk
from theme import AppTheme, apply_global_theme

# Apply the global theme before creating any widgets
apply_global_theme()

def main():
    # Create the main window
    root = ctk.CTk()
    root.title("Ejemplo de Tema Global")
    root.geometry("800x600")
    
    # Configure grid layout (1x2)
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(0, weight=1)
    
    # Create a sidebar frame (using CTkFrame which will use AppTheme.BACKGROUND)
    sidebar_frame = ctk.CTkFrame(root, width=140, corner_radius=0)
    sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
    sidebar_frame.grid_rowconfigure(4, weight=1)
    
    # Add a label to the sidebar (using CTkLabel which will use AppTheme.TEXT)
    logo_label = ctk.CTkLabel(sidebar_frame, text="Menú", font=ctk.CTkFont(size=20, weight="bold"))
    logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
    
    # Add a button in the sidebar (using CTkButton which uses AppTheme.PRIMARY and AppTheme.SECONDARY for hover)
    sidebar_button_1 = ctk.CTkButton(sidebar_frame, text="Opción 1", height=40)
    sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
    
    sidebar_button_2 = ctk.CTkButton(sidebar_frame, text="Opción 2", height=40)
    sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
    
    # Create the main entry field (using CTkEntry which uses AppTheme.BORDER and AppTheme.TEXT)
    entry = ctk.CTkEntry(root, placeholder_text="Ingrese texto aquí", width=300, height=40)
    entry.grid(row=0, column=1, padx=(20, 20), pady=(20, 10), sticky="ew")
    
    # Create a button in the main area (using CTkButton with theme colors)
    main_button = ctk.CTkButton(root, text="Botón Principal", height=40)
    main_button.grid(row=1, column=1, padx=(20, 20), pady=10, sticky="ew")
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()