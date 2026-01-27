import customtkinter as ctk
from src.ui.app import App
from src.ui.login import LoginWindow
import src.database as database

if __name__ == "__main__":
    # Tentar desativar escala de DPI que causa bugs gráficos
    try:
        ctk.deactivate_automatic_dpi_awareness()
    except:
        pass

    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    # Garantir que o banco de dados e usuários existam antes do login
    database.inicializar_banco()
    
    # App é a única raiz (Root)
    app = App()
    app.mainloop()
