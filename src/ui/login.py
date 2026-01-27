import customtkinter as ctk
from tkinter import messagebox
from src.ui.styles import *
import src.database as database
from PIL import Image
import os

class LoginWindow(ctk.CTkToplevel):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        
        self.on_login_success = on_login_success
        self.attempts = 0
        
        self.title("Login - Gestor Fácil")
        self.geometry("400x500")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BACKGROUND)

        # Centralizar na tela (aproximado)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 500) // 2
        # Sequência "Alpha Toggle" para forçar o Windows a pintar o fundo (Correção Definitiva)
        self.attributes("-alpha", 0.0) # Inicia invisivel
        self.geometry(f"400x500+{x}+{y}")
        self.configure(fg_color=COLOR_BACKGROUND)
        
        self.deiconify()
        self.update() # Renderiza invisivel
        self.attributes("-alpha", 1.0) # Força opacidade total
        self.focus_force()

        # Frame Central
        self.frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=CORNER_RADIUS)
        self.frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Logo
        try:
            logo_path = os.path.join("assets", "logotipo.png")
            if os.path.exists(logo_path):
                pil_img = Image.open(logo_path)
                img = ctk.CTkImage(light_image=pil_img, size=(120, 60))
                ctk.CTkLabel(self.frame, image=img, text="").pack(pady=30)
            else:
                ctk.CTkLabel(self.frame, text="Gestor Fácil", font=FONT_HEADER, text_color=COLOR_PRIMARY).pack(pady=30)
        except:
             ctk.CTkLabel(self.frame, text="Gestor Fácil", font=FONT_HEADER, text_color=COLOR_PRIMARY).pack(pady=30)

        # Campos
        self.entry_user = ctk.CTkEntry(self.frame, placeholder_text="Usuário (admin)", width=250, height=40, font=FONT_BODY)
        self.entry_user.pack(pady=10)
        
        self.entry_pass = ctk.CTkEntry(self.frame, placeholder_text="Senha (admin)", show="*", width=250, height=40, font=FONT_BODY)
        self.entry_pass.pack(pady=10)
        self.entry_pass.bind("<Return>", self.fazer_login)

        # Botão
        self.btn_login = ctk.CTkButton(self.frame, text="ENTRAR", command=self.fazer_login, 
                                       fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER, 
                                       width=250, height=40, font=("Segoe UI", 12, "bold"))
        self.btn_login.pack(pady=20)
        
        # Rodapé
        ctk.CTkLabel(self.frame, text="MPE Gestão Comercial", font=FONT_SMALL, text_color=COLOR_TEXT_DIM).pack(side="bottom", pady=20)

    def fazer_login(self, event=None):
        user = self.entry_user.get()
        senha = self.entry_pass.get()
        
        if not user or not senha:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return
            
        try:
            usuario_db = database.verificar_login(user, senha)
            
            if usuario_db == "BLOCKED":
                messagebox.showerror("Acesso Negado", "Este usuário está BLOQUEADO.\nEntre em contacto com o administrador.")
                return

            if usuario_db == "EXPIRED":
                # Senha Expirada - Forçar Troca
                self._fluxo_troca_senha_obrigatoria(user)
                return

            if usuario_db:
                # Sucesso (Usuario, Senha OK e não expirado)
                cargo = usuario_db['cargo']
                print(f"Login sucesso: {user} ({cargo})")
                self.withdraw() # Esconder janela de login
                # self.master.deiconify() # REMOVIDO: App.on_login_success ja faz isso no momento certo
                self.master.on_login_success(usuario_db)
            else:
                self.attempts += 1
                messagebox.showerror("Erro", "Usuário ou senha inválidos.")
        except Exception as e:
             messagebox.showerror("Erro Crítico", f"Erro ao tentar login: {e}")

    def _fluxo_troca_senha_obrigatoria(self, user):
        """Fluxo de troca de senha forçada após 45 dias."""
        msg = "Sua senha expirou (45 dias).\nPor segurança, você deve definir uma nova senha."
        messagebox.showwarning("Senha Expirada", msg)
        
        # Usar dialogos simples para simplificar
        nova_senha = ctk.CTkInputDialog(text="Digite a NOVA senha:", title="Troca de Senha").get_input()
        
        if not nova_senha or len(nova_senha) < 4:
            messagebox.showerror("Erro", "Senha inválida ou muito curta.")
            return

        # Confirmar credenciais antigas para pegar o ID correto e validar seguranca 
        # (Embora ja tenhamos validado antes, precisamos do ID)
        
        # Como verificar_login retorna string se expirado, vamos buscar o usuario manualmente pelo username
        # Mas verificar_login ja retornou EXPIRED, entao sabemos que as credenciais estao certas.
        # Vamos buscar o ID apenas pelo username (autenticacao ja foi feita)
        
        try:
            import src.database as database
            conn = database.conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", (user,))
            res = cursor.fetchone()
            conn.close()
            
            if res:
                uid = res['id']
                database.atualizar_senha(uid, nova_senha)
                messagebox.showinfo("Sucesso", "Senha atualizada! Faça login com a nova senha.")
            else:
                messagebox.showerror("Erro", "Usuário não encontrado.")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atualizar senha: {e}")
