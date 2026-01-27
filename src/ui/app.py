import customtkinter as ctk
from tkinter import messagebox
import os
from src.ui.styles import *
from src.ui.dashboard import DashboardFrame
from src.ui.pos import POSFrame
from src.ui.stock import StockFrame
from src.ui.expenses import ExpensesFrame # Importar novo módulo
from src.ui.admin import AdminFrame # Importar novo módulo
import src.database as database
import src.utils as utils
from PIL import Image
import shutil
from datetime import datetime

from src.ui.login import LoginWindow

class App(ctk.CTk):
    def __init__(self, usuario_atual=None):
        super().__init__()
        
        # PASSO 1: Receber o usuário logado (se houver). 
        # Se for None, significa que o programa acabou de abrir.
        self.usuario_atual = usuario_atual

        self.title("Gestor Fácil - Sistema de Gestão Comercial")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(800, 600)
        
        # PASSO 2: Ocultar a janela principal enquanto preparamos tudo
        self.withdraw()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # PASSO 3: Inicializar Banco de Dados e Backups antes de qualquer coisa
        self._inicializar_sistema()
        
        # PASSO 4: Decisão de Fluxo
        if self.usuario_atual:
            # Se ja temos usuario (veio do login), construímos o Painel
            self.construir_interface()
            self.deiconify() # Mostra a janela
        else:
            # Se não temos usuario, abrimos a tela de Login
            self.abrir_login()

    def abrir_login(self):
        """Abre a janela de login como Toplevel."""
        self.login_window = LoginWindow(self, self.on_login_success)
        # LoginWindow se encarrega de se mostrar

    def on_login_success(self, usuario):
        """Callback após login bem-sucedido."""
        # Converter sqlite3.Row para dict para permitir uso de .get()
        self.usuario_atual = dict(usuario)
        self.construir_interface() # Constrói a UI agora que temos usuário
        self.deiconify() # Mostra a janela principal
        # A janela de login se destrói sozinha ou já foi destruída

    def construir_interface(self):
        """Constrói toda a interface do usuário após login."""
        # Configurar Grid Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1) # Importante para expandir altura
        
        # Inicializar Frames
        self.frames = {} 
        self.frame_atual = None
        
        # Passar self como master
        try:
            self.frames["dashboard"] = DashboardFrame(self)
        except Exception as e:
            print(f"Erro ao criar Dashboard: {e}")
            messagebox.showerror("Erro Fatal", f"Erro ao criar Dashboard:\n{e}")
            
        try:
            self.frames["stock"] = StockFrame(self)
        except Exception as e:
            print(f"Erro ao criar Stock: {e}")
            messagebox.showerror("Erro Fatal", f"Erro ao criar Stock:\n{e}")
            
        try:
            self.frames["expenses"] = ExpensesFrame(self)
        except Exception as e:
            print(f"Erro ao criar Expenses: {e}")
            messagebox.showerror("Erro Fatal", f"Erro ao criar Despesas:\n{e}")

        try:
            self.frames["pos"] = POSFrame(self)
        except Exception as e:
            print(f"Erro ao criar POS: {e}")
            messagebox.showerror("Erro Fatal", f"Erro ao criar POS:\n{e}")

        try:
            self.frames["admin"] = AdminFrame(self)
        except Exception as e:
            print(f"Erro ao criar Admin: {e}")
            messagebox.showerror("Erro Fatal", f"Erro ao criar Admin (Verifique o código):\n{e}")


        # Criar Sidebar (PACK LAYOUT para Footer fixo)
        self.sidebar_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew") 
        
        # --- Topo da Sidebar (Logo + Navegação) ---
        self.sidebar_top = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.sidebar_top.pack(side="top", fill="x", padx=0, pady=0)

        # Logo
        logo_path = os.path.join("assets", "logo", "logo_gestor_facil_sidebar.png")
        if os.path.exists(logo_path):
            pil_logo = Image.open(logo_path)
            logo_img = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(180, 50))
            ctk.CTkLabel(self.sidebar_top, text="", image=logo_img).pack(padx=20, pady=20)
        else:
            ctk.CTkLabel(self.sidebar_top, text="Gestor Fácil", font=FONT_TITLE).pack(padx=20, pady=20)

        # Botões da Sidebar - Navegação
        self.btn_dashboard = self._criar_botao_sidebar(self.sidebar_top, "Dashboard", self.mostrar_dashboard, "home.png")
        self.btn_stock = self._criar_botao_sidebar(self.sidebar_top, "Stock / Armazém", self.mostrar_stock, "box.png")
        self.btn_expenses = self._criar_botao_sidebar(self.sidebar_top, "Despesas", self.mostrar_expenses, "money.png")
        self.btn_pos = self._criar_botao_sidebar(self.sidebar_top, "Ponto de Venda", self.mostrar_pos, "cart.png")
        self.btn_admin = self._criar_botao_sidebar(self.sidebar_top, "Administração", self.mostrar_admin, "settings.png")
        
        # --- Rodapé da Sidebar (Fixo em baixo) ---
        self.sidebar_bottom = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.sidebar_bottom.pack(side="bottom", fill="x", padx=0, pady=20)

        self.btn_backup = self._criar_botao_sidebar(self.sidebar_bottom, "Backup Manual", self._realizar_backup_manual, "backup.png")
        self.btn_manual = self._criar_botao_sidebar(self.sidebar_bottom, "Manual Técnico", self.abrir_manual, "manual.png")
        self.btn_exit = self._criar_botao_sidebar(self.sidebar_bottom, "Sair", self.on_closing, "exit.png")

        # Aplicar Permissões
        start_frame = self.mostrar_dashboard
        
        if self.usuario_atual and self.usuario_atual['cargo'] == 'vendedor':
            self.btn_dashboard.pack_forget()
            self.btn_expenses.pack_forget()
            self.btn_admin.pack_forget()
            self.btn_backup.pack_forget()
            start_frame = self.mostrar_pos
            
        elif self.usuario_atual and self.usuario_atual['cargo'] == 'super_admin':
            self.btn_dashboard.pack_forget()
            self.btn_stock.pack_forget()
            self.btn_expenses.pack_forget()
            self.btn_pos.pack_forget()
            # Mantém apenas Admin, Backup, Manual, Sair
            start_frame = self.mostrar_admin
        
        elif self.usuario_atual and self.usuario_atual['cargo'] == 'gerente':
             pass # Acesso total
        
        start_frame()

    def _inicializar_sistema(self):
        """Inicializa base de dados e backups."""
        database.inicializar_banco()
        utils.gerar_manual_tecnico()
        utils.realizar_backup()

    def _criar_botao_sidebar(self, parent, texto, comando, icon_name=None):
        img = None
        if icon_name:
            try:
                # Tentar carregar ícone
                icon_path = os.path.join("assets", "icons", icon_name)
                if os.path.exists(icon_path):
                    pil_img = Image.open(icon_path)
                    img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(20, 20))
            except Exception as e:
                print(f"Erro ao carregar icone {icon_name}: {e}")

        btn = ctk.CTkButton(parent, text=texto, command=comando, 
                            font=FONT_BODY, fg_color="transparent", anchor="w",
                            text_color=COLOR_TEXT, hover_color=COLOR_SURFACE_HOVER,
                            image=img, compound="left", height=40) 
        btn.pack(fill="x", padx=10, pady=5)
        return btn

    def selecionar_frame(self, nome_frame):
        # Verifica se o frame existe (pode ter falhado ao carregar)
        if nome_frame not in self.frames:
            messagebox.showerror("Erro de Navegação", f"O módulo '{nome_frame}' não foi carregado devido a um erro anterior.")
            return
    
        # Esconder frame atual
        if self.frame_atual:
            self.frame_atual.grid_forget()
        
        # Mostrar novo frame
        self.frame_atual = self.frames[nome_frame]
        self.frame_atual.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
    
        
        # Resetar cores dos botões
        self.btn_dashboard.configure(fg_color="transparent")
        self.btn_stock.configure(fg_color="transparent")
        self.btn_expenses.configure(fg_color="transparent")
        self.btn_pos.configure(fg_color="transparent")
        self.btn_admin.configure(fg_color="transparent")
    
    def mostrar_dashboard(self):
        self.selecionar_frame("dashboard")
        self.btn_dashboard.configure(fg_color=COLOR_PRIMARY)
    
    def mostrar_stock(self):
        self.selecionar_frame("stock")
        self.btn_stock.configure(fg_color=COLOR_PRIMARY)
    
    def mostrar_pos(self):
        self.selecionar_frame("pos")
        self.btn_pos.configure(fg_color=COLOR_PRIMARY)
    
    def mostrar_expenses(self):
        self.selecionar_frame("expenses")
        self.btn_expenses.configure(fg_color=COLOR_PRIMARY)
    
    def mostrar_admin(self):
        self.selecionar_frame("admin")
    
    def abrir_manual(self):
        """Abre o ficheiro Manual_Tecnico.txt com o editor padrão do sistema."""
        try:
            # Tenta gerar novamente para garantir que existe
            manual_path = utils.gerar_manual_tecnico()
            
            if manual_path and os.path.exists(manual_path):
                os.startfile(manual_path)
            else:
                # Fallback para tentar encontrar na pasta
                docs_path = utils.get_documents_path("Manual_Tecnico.txt")
                if os.path.exists(docs_path):
                    os.startfile(docs_path)
                else:
                    messagebox.showerror("Erro", "Manual não encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir manual: {e}")
    
    def _realizar_backup_manual(self):
        try:
            output = utils.realizar_backup()
            if output:
                messagebox.showinfo("Sucesso", f"Backup realizado com sucesso!")
            else:
                 messagebox.showerror("Erro", "Falha ao realizar backup.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro crítico no backup: {e}")
    
    def on_closing(self):
        if messagebox.askokcancel("Sair", "Deseja realmente sair?"):
             self.destroy()
