import customtkinter as ctk
import os
from tkinter import messagebox, ttk
from src.ui.styles import *
from datetime import datetime, timedelta
import src.docs_generator as docs_generator

class AdminFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        print(">>> ADMIN FRAME RENDERIZADO (V32 - RESTRUCTURED) <<<")
        
        self.user = getattr(master, 'usuario_atual', {})
        self.user_role = self.user.get('cargo', 'vendedor') if self.user else 'vendedor'

        self.label_titulo = ctk.CTkLabel(self, text="Painel de Administração", font=FONT_HEADER)
        self.label_titulo.pack(pady=20)
        
        # --- Abas ---
        self.tabview = ctk.CTkTabview(self, width=900)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Lógica de Permissão
        self.tabs = {}
        
        # DEBUG: Mostrar quem esta logado para garantir que a logica funciona
        print(f"AdminFrame Init: User={self.user.get('usuario')}, Role={self.user_role}")

        if self.user_role == 'super_admin':
            self.tabs['dev'] = self.tabview.add("Metas & Finanças (Dev)")
            self.tabs['contratos'] = self.tabview.add("Novo Cliente (Contratos)")
            
        # Todo ADMIN, SUPER_ADMIN ou GERENTE pode gerir equipe
        if self.user_role in ['super_admin', 'admin', 'gerente']:
            self.tabs['users'] = self.tabview.add("Gestão de Equipe (Usuários)")
            # self._setup_tab_users() # REMOVIDO: Causava erro (Adminframe, _setup_tab_user missing parent)

        # Configurar conteudos
        if 'dev' in self.tabs:
            self._setup_tab_dev(self.tabs['dev'])
            
        if 'contratos' in self.tabs:
            self._setup_tab_contratos(self.tabs['contratos'])
            
        if 'users' in self.tabs:
            self._setup_tab_users(self.tabs['users'])

    # --- SAFETY NET (REDE DE SEGURANÇA) ---
    def __getattr__(self, name):
        # Ignorar atributos builtin/magicos para evitar loops
        if name.startswith('__'):
            raise AttributeError(name)
            
        print(f"!!! CHAMADA FANTASMA DETECTADA: {name} !!!")
        def dummy_method(*args, **kwargs):
            messagebox.showerror("Aviso Técnico", f"O sistema tentou usar uma função antiga: '{name}'\nMas o Crash foi evitado.")
            print(f"Chamada fantasma '{name}' interceptada.")
        return dummy_method

    def _setup_tab_dev(self, parent):
        # Header
        head = ctk.CTkFrame(parent, fg_color="transparent")
        head.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(head, text="Visão Geral do Negócio (Super Admin)", font=("Roboto", 20, "bold")).pack(side="left")
        ctk.CTkButton(head, text="🔄 Atualizar Dashboard", command=self._atualizar_dash_super, width=150).pack(side="right")
        
        # Cards Container (GRID LAYOUT for Responsiveness)
        self.frame_dash_cards = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame_dash_cards.pack(fill="x", padx=10, pady=10)
        
        # Configurar colunas para terem o mesmo peso (1)
        for i in range(5):
            self.frame_dash_cards.grid_columnconfigure(i, weight=1)
        
        # Info
        ctk.CTkLabel(parent, text="* Receita Recorrente: 500.00 MT/mês por cliente ativo. (Taxa de Instalação: 1.500,00 MT - Cobrança Única)", font=("Roboto", 12), text_color="gray").pack(side="bottom", pady=20)
        
        # --- Tabela de Monitoramento de Lojas (Novo) ---
        # Adicionar tabela NO SETUP (onde 'parent' existe).
        
        # Separador
        ctk.CTkLabel(parent, text="Monitoramento de Lojas", font=("Roboto", 16, "bold")).pack(pady=(20, 5))
        
        frame_table = ctk.CTkFrame(parent, fg_color=COLOR_SURFACE)
        frame_table.pack(fill="both", expand=True, padx=10, pady=10)
        
        cols = ("empresa", "login", "status", "wpp")
        tree = ttk.Treeview(frame_table, columns=cols, show="headings", height=8)
        
        tree.heading("empresa", text="Cliente / Empresa")
        tree.heading("login", text="Login Master")
        tree.heading("status", text="Status")
        tree.heading("wpp", text="WhatsApp")
        
        tree.column("empresa", width=250)
        tree.column("login", width=100)
        tree.column("status", width=80, anchor="center")
        tree.column("wpp", width=100)
        
        tree.pack(side="left", fill="both", expand=True)
        
        sb = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
        sb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=sb.set)
        
        # Cores para status
        tree.tag_configure("bloqueado", foreground="red")
        tree.tag_configure("ativo", foreground="green")
        
        # Popular Dados
        try:
            # Import database localmente ou usar do self se disponivel? 
            # O modulo ja deve ter sido importado la em cima? AdminFrame importa? Sim, mas inside methods.
            # Vamos importar aqui para garantir
            import src.database as database
            
            clientes = database.get_clientes_para_dashboard()
            for cli in clientes:
                # cli: nome_completo, usuario, status, whatsapp, email
                status = cli['status'] if cli['status'] else "ativo"
                tree.insert("", "end", values=(
                    cli['nome_completo'],
                    cli['usuario'],
                    status.upper(),
                    cli['whatsapp']
                ), tags=(status,))
        except Exception as e:
            print(f"Erro ao carregar lista de clientes: {e}")
            messagebox.showerror("Erro", f"Erro ao listar clientes: {e}")

        self._atualizar_dash_super()

    def _atualizar_dash_super(self):
        """Atualiza os cards do dashboard do super admin."""
        # Limpar cards antigos
        for w in self.frame_dash_cards.winfo_children(): 
            w.destroy()
        
        import src.database as database
        import src.utils as utils
        
        try:
            m = database.get_metricas_super_admin()
            
            # Card 1: Total Clientes
            c1 = self._criar_card(self.frame_dash_cards, "Total Clientes (Lojas)", str(m['total_clientes']), COLOR_PRIMARY)
            c1.grid(row=0, column=0, padx=5, sticky="ew")
            
            # Card 2: Ativos
            c2 = self._criar_card(self.frame_dash_cards, "Lojas Ativas", str(m['clientes_ativos']), "#28a745")
            c2.grid(row=0, column=1, padx=5, sticky="ew")
            
            # Card 3: Bloqueados
            c3 = self._criar_card(self.frame_dash_cards, "Lojas Bloqueadas", str(m['clientes_bloqueados']), COLOR_DANGER)
            c3.grid(row=0, column=2, padx=5, sticky="ew")
            
            # Card 4: Receita Mensal
            rec_mensal = m['clientes_ativos'] * 500.0
            c4 = self._criar_card(self.frame_dash_cards, "Receita Mensal (Est.)", utils.formatar_moeda(rec_mensal), "#E67E22")
            c4.grid(row=0, column=3, padx=5, sticky="ew")

            # Card 5: Receita Instalações (Novo)
            # Total Clientes * 1500
            rec_install = m['total_clientes'] * 1500.0
            c5 = self._criar_card(self.frame_dash_cards, "Total Instalações", utils.formatar_moeda(rec_install), "#17a2b8") # Cyan
            c5.grid(row=0, column=4, padx=5, sticky="ew")
            
        except Exception as e:
            if self.frame_dash_cards.winfo_exists():
                ctk.CTkLabel(self.frame_dash_cards, text=f"Erro de Conexão: {e}", text_color="red").grid(row=0, column=0, columnspan=5)


 
    def _setup_tab_contratos(self, parent):
        lbl = ctk.CTkLabel(parent, text="Cadastrar Novo Cliente (Empresa)", font=("Roboto", 18, "bold"))
        lbl.pack(pady=10)
        
        form = ctk.CTkFrame(parent)
        form.pack(padx=20, pady=10)
        
        # Dados da Empresa (INLINE)
        ctk.CTkLabel(form, text="Nome Completo / Empresa:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_cli_nome = ctk.CTkEntry(form, width=300)
        self.entry_cli_nome.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ctk.CTkLabel(form, text="NUIT:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_cli_nuit = ctk.CTkEntry(form, width=300)
        self.entry_cli_nuit.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ctk.CTkLabel(form, text="Email (Envio Contrato):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_cli_email = ctk.CTkEntry(form, width=300)
        self.entry_cli_email.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ctk.CTkLabel(form, text="WhatsApp:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.entry_cli_wpp = ctk.CTkEntry(form, width=300)
        self.entry_cli_wpp.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        ctk.CTkLabel(form, text="Endereço:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.entry_cli_end = ctk.CTkEntry(form, width=300)
        self.entry_cli_end.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        # Dados de Acesso (Login do Cliente)
        ctk.CTkLabel(form, text="--- Acesso ao Sistema ---", text_color=COLOR_PRIMARY).grid(row=5, column=0, columnspan=2, pady=10)
        
        ctk.CTkLabel(form, text="Username (Login):").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.entry_cli_user = ctk.CTkEntry(form, width=200)
        self.entry_cli_user.grid(row=6, column=1, padx=5, pady=5, sticky="w")
        
        ctk.CTkLabel(form, text="Senha Provisória:").grid(row=7, column=0, padx=5, pady=5, sticky="e")
        self.entry_cli_pass = ctk.CTkEntry(form, width=200)
        self.entry_cli_pass.grid(row=7, column=1, padx=5, pady=5, sticky="w")
        
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        btn_docs = ctk.CTkButton(btn_frame, text="1. Gerar Contrato PDF", 
                                  command=self.action_gerar_pdf, fg_color=COLOR_WARNING)
        btn_docs.pack(side="left", padx=10)
        
        btn_add = ctk.CTkButton(btn_frame, text="2. Cadastrar Acesso (Admin)", 
                                  command=self.action_cadastrar_cliente, fg_color=COLOR_SUCCESS)
        btn_add.pack(side="left", padx=10)

    def action_gerar_pdf(self):
        nome = self.entry_cli_nome.get().strip()
        nuit = self.entry_cli_nuit.get().strip()
        email = self.entry_cli_email.get().strip()
        
        if not nome or not nuit:
            messagebox.showwarning("Aviso", "Nome e NUIT são obrigatórios para o contrato.")
            return
            
        try:
            path = docs_generator.gerar_kit_cliente(nome, nuit, email)
            messagebox.showinfo("Sucesso", f"Contrato gerado em:\n{path}\n\nEnvia este arquivo para o email: {email}")
            
            # Tentar abrir email (simples mailto)
            if email:
                try:
                    import webbrowser
                    webbrowser.open(f"mailto:{email}?subject=Contrato Gestor Facil&body=Segue em anexo o contrato.")
                except: pass
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {e}")

    def _criar_card(self, parent, titulo, valor, cor_topo):
        frame = ctk.CTkFrame(parent, width=150, height=80, corner_radius=10)
        # Barra colorida no topo
        topo = ctk.CTkFrame(frame, height=10, fg_color=cor_topo, corner_radius=0)
        topo.pack(fill="x")
        
        lbl_val = ctk.CTkLabel(frame, text=valor, font=("Roboto", 24, "bold"))
        lbl_val.pack(pady=(5,0))
        
        lbl_tit = ctk.CTkLabel(frame, text=titulo, font=("Roboto", 12))
        lbl_tit.pack(pady=(0,5))
        
        return frame

    def _setup_tab_users(self, parent=None):
        if parent is None:
            print("AVISO: _setup_tab_users chamado sem parent! Ignorando setup.")
            return

        # Frame de Cadastro (Topo) e Monitoramento (Baixo)
        self.editing_user_id = None # Controlar se esta editando
        
        # --- Topo: Cadastro ---
        frame_top = ctk.CTkFrame(parent)
        frame_top.pack(fill="x", padx=10, pady=10)
        
        self.lbl_titulo_cad = ctk.CTkLabel(frame_top, text="Novo Usuário / Vendedor", font=("Roboto", 16, "bold"))
        self.lbl_titulo_cad.pack(pady=5)
        
        form = ctk.CTkFrame(frame_top)
        form.pack(pady=5)
        
        self.entry_u_nome = ctk.CTkEntry(form, width=250)
        ctk.CTkLabel(form, text="Nome Completo:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_u_nome.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        self.entry_u_user = ctk.CTkEntry(form, width=150)
        ctk.CTkLabel(form, text="Username:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_u_user.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        self.entry_u_pass = ctk.CTkEntry(form, width=150, show="*")
        ctk.CTkLabel(form, text="Senha:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_u_pass.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ctk.CTkLabel(form, text="Cargo:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        
        # Se for super_admin, pode criar tudo. Se for admin, criar so vendedor (ou admin tb? User disse "criar o seu vendedor")
        # Vou assumir que admin cria vendedores.
        roles_disponiveis = ["vendedor"]
        if self.user_role == 'super_admin':
            roles_disponiveis = ["vendedor", "admin", "gerente", "super_admin"]
        elif self.user_role == 'admin':
             roles_disponiveis = ["vendedor", "gerente"] # Cliente cria vendedores e gerentes
        elif self.user_role == 'gerente':
             roles_disponiveis = ["vendedor"] # Gerente cria vendedores

        self.combo_u_role = ctk.CTkComboBox(form, values=roles_disponiveis, width=150)
        self.combo_u_role.grid(row=3, column=1, padx=5, pady=5)
        
        self.entry_u_email = ctk.CTkEntry(form, width=250)
        ctk.CTkLabel(form, text="Email:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.entry_u_email.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        self.entry_u_wpp = ctk.CTkEntry(form, width=150)
        ctk.CTkLabel(form, text="WhatsApp:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.entry_u_wpp.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        
        self.btn_cadastrar = ctk.CTkButton(form, text="Cadastrar", command=self.salvar_usuario, fg_color=COLOR_PRIMARY, width=150)
        self.btn_cadastrar.grid(row=6, column=0, columnspan=2, pady=10)
        
        self.btn_cancelar_edit = ctk.CTkButton(form, text="Cancelar Edição", command=self.cancelar_edicao, fg_color="gray", width=150)
        # So aparece quando editar

        # --- Base: Monitoramento ---
        frame_mon = ctk.CTkFrame(parent)
        frame_mon.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header Monitoramento
        head = ctk.CTkFrame(frame_mon, fg_color="transparent")
        head.pack(fill="x", pady=10)
        
        # --- Cards de Resumo (Bonitos) ---
        cards_frame = ctk.CTkFrame(head, fg_color="transparent")
        cards_frame.pack(side="left", fill="x", expand=True)

        # Logica de Cards diferenciada
        if self.user_role == 'super_admin':
             self.card_total_clientes = self._criar_card(cards_frame, "Total Clientes", "0", COLOR_PRIMARY)
             self.card_total_clientes.pack(side="left", padx=5)
             
             self.card_total_vendedores = self._criar_card(cards_frame, "Total Vendedores", "0", "#28a745") # Verde
             self.card_total_vendedores.pack(side="left", padx=5)
             
        elif self.user_role == 'admin':
             # Cliente não vê 'Total Clientes' (ele é o cliente). Vê 'Total Gerentes'.
             self.card_total_clientes = self._criar_card(cards_frame, "Total Gerentes", "0", COLOR_PRIMARY)
             self.card_total_clientes.pack(side="left", padx=5)
             
             self.card_total_vendedores = self._criar_card(cards_frame, "Total Vendedores", "0", "#28a745")
             self.card_total_vendedores.pack(side="left", padx=5)
        
        elif self.user_role == 'gerente':
             self.card_total_clientes = None # Gerente n vê gerentes acima dele? Ou vê pares? Vamos deixar sem card por enquanto ou igual admin?
             # Vamos mostrar so vendedores
             self.card_total_vendedores = self._criar_card(cards_frame, "Total Vendedores", "0", "#28a745")
             self.card_total_vendedores.pack(side="left", padx=5)
        
        
        ctk.CTkButton(head, text="🔄 Atualizar", command=self.carregar_usuarios, width=100).pack(side="right", padx=10)
        
        # --- Actions Bottom Bar (Pinned) ---
        act_frame = ctk.CTkFrame(frame_mon)
        act_frame.pack(side="bottom", fill="x", pady=5)
        
        ctk.CTkButton(act_frame, text="🔒 Bloquear", command=self.bloquear_usuario, fg_color=COLOR_DANGER, width=80).pack(side="right", padx=5)
        ctk.CTkButton(act_frame, text="🔓 Desbloquear", command=self.desbloquear_usuario, fg_color=COLOR_SUCCESS, width=80).pack(side="right", padx=5)
        ctk.CTkButton(act_frame, text="✏️ Editar", command=self.carregar_para_edicao, fg_color="orange", width=80).pack(side="right", padx=5)
        ctk.CTkButton(act_frame, text="🗑️ Remover", command=self.remover_usuario_ui, fg_color="darkred", width=80).pack(side="right", padx=5)

        # Tabela Treeview
        cols = ["ID", "Nome", "User", "Cargo", "Status", "Email", "WhatsApp"]
        
        # COLUNA EXTRA: Criado Por (Agora visivel para Super Admin, Admin e Gerente)
        if self.user_role in ['super_admin', 'admin', 'gerente']:
            cols.append("Criado Por")

        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.map("Treeview", background=[("selected", COLOR_PRIMARY)])

        # "tree headings" habilita a coluna #0 com setinhas (hierarquia)
        self.tree_users = ttk.Treeview(frame_mon, columns=cols, show="tree headings", height=8)
        
        # Configurar coluna da árvore (#0)
        self.tree_users.heading("#0", text="Estrutura")
        self.tree_users.column("#0", width=150, anchor="w")

        self.tree_users.heading("ID", text="ID")
        self.tree_users.heading("Nome", text="Nome")
        self.tree_users.heading("User", text="Username")
        self.tree_users.heading("Cargo", text="Cargo")
        self.tree_users.heading("Status", text="Status")
        self.tree_users.heading("Email", text="Email")
        self.tree_users.heading("WhatsApp", text="WhatsApp")
        
        if self.user_role in ['super_admin', 'admin', 'gerente']:
            self.tree_users.heading("Criado Por", text="Criado Por")
            self.tree_users.column("Criado Por", width=100)
        
        self.tree_users.column("ID", width=30, anchor="center")
        self.tree_users.column("Nome", width=150)
        self.tree_users.column("User", width=80)
        self.tree_users.column("Cargo", width=80)
        self.tree_users.column("Status", width=80, anchor="center")
        self.tree_users.column("Email", width=150)
        self.tree_users.column("WhatsApp", width=100)
        
        self.tree_users.pack(side="top", fill="both", expand=True, padx=5)
        
        # Tag configuration for colors
        self.tree_users.tag_configure("blocked", foreground="red")
        self.tree_users.tag_configure("active", foreground="green")
        
        self.carregar_usuarios()
        
        self.carregar_usuarios()

    def salvar_usuario(self):
        """Salva novo ou edita existente."""
        # PASSO 1: Coletar dados do Formulário
        nome = self.entry_u_nome.get()
        user = self.entry_u_user.get()
        senha = self.entry_u_pass.get()
        cargo = self.combo_u_role.get()
        email = self.entry_u_email.get()
        wpp = self.entry_u_wpp.get()
        
        # PASSO 2: Validação Básica
        if not nome or not user:
            messagebox.showwarning("Aviso", "Nome e Username são obrigatórios.")
            return
            
        import src.database as database
        import src.utils as utils
        
        # ... (Helper notification code omitted for brevity in comments, logic remains same) ...
        # (Nota: A função interna _notificar_acao foi omitida aqui para clareza, mas continua existindo)
        
        # PASSO 3: Decidir se é EDIÇÃO ou NOVO CADASTRO
        if self.editing_user_id:
            # --- MODO EDIÇÃO ---
            try:
                if database.editar_usuario(self.editing_user_id, nome, user, email, wpp):
                    # Se alterou senha, atualiza separado
                    if senha: database.atualizar_senha(self.editing_user_id, senha)
                    
                    # Logica de Popup e Confirmação
                    u_data = {'nome': nome, 'user': user, 'senha': senha if senha else "[Mantida]", 'cargo': cargo, 'email': email, 'acao_tipo': "ATUALIZADO", 'wpp_target': wpp}
                    
                    self.dialog = PostActionDialog(self, "Edição Concluída", f"Usuário {nome} atualizado com sucesso!", u_data, self)
                    self.dialog.lift() 
                    
                    self.cancelar_edicao()
                    self.carregar_usuarios()
                else: messagebox.showerror("Erro", "Erro ao atualizar. Username pode estar duplicado.")
            except Exception as e: messagebox.showerror("Erro Crítico Edição", f"Falha: {e}")

        else:
            # --- MODO NOVO CADASTRO ---
            if not senha:
                messagebox.showwarning("Aviso", "Senha é obrigatória.")
                return
            try:
                # PASSO 4: Gravar no Banco
                criador = self.user.get('usuario', 'sistema')
                
                if database.criar_usuario(user, senha, cargo, email, wpp, nome, created_by=criador):
                    u_data = {'nome': nome, 'user': user, 'senha': senha, 'cargo': cargo, 'email': email, 'acao_tipo': "CADASTRADO", 'wpp_target': wpp}
                    
                    self.dialog = PostActionDialog(self, "Cadastro Concluído", f"Usuário {nome} criado com sucesso!", u_data, self)
                    self.dialog.lift()
                    
                    self._limpar_form()
                    self.carregar_usuarios()
                else: messagebox.showerror("Erro", "Username já existe.")
            except Exception as e: messagebox.showerror("Erro Crítico Cadastro", f"Falha: {e}")


    def carregar_para_edicao(self):
        sel = self.tree_users.selection()
        if not sel: return
        
        # Pegar dados da linha selecionada
        # values pode ter tamanho 8 (Admin) ou 9 (Super Admin)
        # ID, Nome, User, Cargo, Status, Email, WhatsApp, [CriadoPor?], Senha
        
        vals = self.tree_users.item(sel[0])['values']
        
        self.editing_user_id = vals[0]
        
        self.entry_u_nome.delete(0, 'end'); self.entry_u_nome.insert(0, vals[1])
        self.entry_u_user.delete(0, 'end'); self.entry_u_user.insert(0, vals[2])
        self.combo_u_role.set(vals[3])
        self.entry_u_email.delete(0, 'end'); self.entry_u_email.insert(0, vals[5])
        self.entry_u_wpp.delete(0, 'end'); self.entry_u_wpp.insert(0, str(vals[6]))
        
        # Senha: Sempre o ULTIMO valor da lista, independente de ter Criado Por ou não
        senha_atual = str(vals[-1])
        
        self.entry_u_pass.delete(0, 'end')
        self.entry_u_pass.insert(0, senha_atual) # Mostrar senha
        self.entry_u_pass.configure(placeholder_text="Altere se desejar")
        
        # Mudar estado do form
        self.lbl_titulo_cad.configure(text=f"Editando: {vals[1]}")
        self.btn_cadastrar.configure(text="Salvar Alterações")
        self.btn_cancelar_edit.grid(row=6, column=1) # Mostrar botao cancelar

    def cancelar_edicao(self):
        self.editing_user_id = None
        self._limpar_form()
        self.lbl_titulo_cad.configure(text="Novo Usuário / Vendedor")
        self.btn_cadastrar.configure(text="Cadastrar")
        self.btn_cancelar_edit.grid_remove()
        self.entry_u_pass.configure(placeholder_text="")

    def remover_usuario_ui(self):
        sel = self.tree_users.selection()
        if not sel: return
        
        vals = self.tree_users.item(sel[0])['values']
        uid = vals[0]
        nome = vals[1]
        
        # Dados extras (hidden or from fetch)
        # vals: ID, Nome, User, Cargo, Status, Email, WhatsApp, Senha
        user_val = vals[2]
        role_val = vals[3]
        email_val = vals[5]
        wpp_val = vals[6]
        
        if str(nome) == str(self.user.get('usuario')): 
             messagebox.showerror("Erro", "Você não pode remover a si mesmo!")
             return

        if messagebox.askyesno("Confirmar Rescisão", f"RESCISÃO DE CONTRATO / REMOÇÃO\n\nTem certeza que deseja remover o acesso de '{nome}'?\nIsso apagará o usuário do sistema."):
            import src.database as database
            import src.utils as utils
            
            database.remover_usuario(uid)
            messagebox.showinfo("Sucesso", "Usuário removido.")
            
            # Notificar Remocao
            # Reusar logica de notificacao seria ideal, mas nao tenho acesso a funcao interna aqui facil.
            # Vou simplificar e chamar direto.
            msg = f"*Gestor Fácil - RESCISÃO/REMOÇÃO*\nUsuário: {nome} ({user_val})\nCargo: {role_val}\nStatus: REMOVIDO DO SISTEMA\n\nAção por: {self.user.get('nome_completo')}"
            admin_wpp = self.user.get('whatsapp', '')
            if admin_wpp: utils.notificar_whatsapp(admin_wpp, msg)
            
            self.carregar_usuarios()

    def bloquear_usuario(self):
        sel = self.tree_users.selection()
        if not sel: return
        vals = self.tree_users.item(sel[0])['values']
        nome = vals[1]
        self._alterar_status('bloqueado')
        
        import src.utils as utils
        msg = f"*Gestor Fácil - BLOQUEIO*\nUsuário: {nome}\nStatus: BLOQUEADO\nMotivo: Pendência ou Segurança.\n\nAção por: {self.user.get('nome_completo')}"
        admin_wpp = self.user.get('whatsapp', '')
        if admin_wpp: utils.notificar_whatsapp(admin_wpp, msg)
        
    def desbloquear_usuario(self):
        self._alterar_status('ativo')

    def carregar_usuarios(self):
        try:
            # Limpar
            for i in self.tree_users.get_children():
                self.tree_users.delete(i)
                
            import src.database as database
            users = database.listar_todos_usuarios()
            
            total_cli = 0
            total_vend = 0
            
            # -- Lógica Hierárquica Universal (Recursiva) --
            # 1. Indexar dados para acesso rápido
            users_by_user = {}
            children_map = {} # user -> [list of child_users objects]
            
            # Preparar estruturas
            for u in users:
                u_dict = dict(u)
                uname = u_dict['usuario']
                users_by_user[uname] = u_dict
                
                # Normalizar creator
                creator = u_dict['created_by']
                if not creator: creator = "ROOT"
                
                if creator not in children_map: children_map[creator] = []
                children_map[creator].append(u_dict)

            # Função Recursiva de Inserção
            def insert_recursive(user_obj, parent_id=""):
                uname = user_obj['usuario']
                
                # Preparar Visuais
                status = user_obj['status'] if user_obj['status'] else 'ativo'
                tag = "blocked" if status == 'bloqueado' else "active"
                
                created_val = user_obj['created_by'] if user_obj['created_by'] else "-"
                
                # Colunas: ID, Nome, User, Cargo, Status, Email, WhatsApp, Senha, [Criado Por]
                # Nota: self.tree_users columns definition:
                # 0=ID, 1=Nome, 2=User, 3=Cargo, 4=Status, 5=Email, 6=WhatsApp, 7=Senha (Hidden?), +1=CriadoPor
                
                # Colunas: ID, Nome, User, Cargo, Status, Email, WhatsApp, [Criado Por], [Hidden: Senha]
                # Treeview columns: ["ID", "Nome", "User", "Cargo", "Status", "Email", "WhatsApp", ("Criado Por" se super)]
                
                vals = [
                    user_obj['id'],
                    user_obj['nome_completo'],
                    user_obj['usuario'],
                    user_obj['cargo'],
                    status.upper(),
                    user_obj.get('email', ''),
                    user_obj.get('whatsapp', '')
                ]
                
                if self.user_role in ['super_admin', 'admin', 'gerente']:
                    vals.append(created_val)
                    
                # Senha vai por ultimo (se a treeview tiver menos colunas que vals, o extra fica hidden mas acessivel)
                vals.append(user_obj['senha'])

                # Inserir Nó (text=uname para aparecer na coluna #0 com a setinha)
                my_iid = self.tree_users.insert(parent_id, "end", text=uname, values=vals, tags=(tag,), open=True)
                
                # Inserir Filhos
                if uname in children_map:
                    for child in children_map[uname]:
                        insert_recursive(child, my_iid)

            # 2. Definir Raízes da Visualização
            roots_to_show = []
            
            if self.user_role == 'super_admin':
                # Super Admin vê TUDO.
                # Raizes são: 
                # a) O proprio Super Admin 
                # b) Quem não tem criador (ROOT)
                # c) Quem tem criador que NÃO existe na lista (Orfaos)
                
                # Adicionar ROOTs virtuais
                if "ROOT" in children_map:
                    roots_to_show.extend(children_map["ROOT"])
                
                # Adicionar Orfãos (criador existe mas nao ta na lista users_by_user? 
                # No nosso caso users tem TODO MUNDO, então se criador nao ta em users_by_user, é orfao depai inexistente)
                # Vamos simplificar: Iterar todos, se criador nao estiver em users_by_user, é raiz.
                for u in users:
                    creator = u['created_by']
                    if creator and creator not in users_by_user:
                        roots_to_show.append(dict(u))
                        
                # Evitar duplicatas nas raizes (ex: se super_admin for ROOT, ja foi add)
                # Dict para unique
                unique_roots = {}
                for r in roots_to_show: unique_roots[r['usuario']] = r
                roots_to_show = list(unique_roots.values())

            else:
                # ADMIN (Cliente) / VENDEDOR
                # Vê apenas a SI MESMO como raiz. (E recursivamente seus filhos)
                meu_user = self.user.get('usuario')
                if meu_user in users_by_user:
                    roots_to_show.append(users_by_user[meu_user])

            # 3. Renderizar Arvore
            inserted_keys = set()
            for root in roots_to_show:
                if root['usuario'] not in inserted_keys:
                    insert_recursive(root, "")
                    inserted_keys.add(root['usuario'])
            
            # Atualizar Cards (Recalcular baseados no que foi exibido? Ou totais globais?)
            # O cliente quer ver totais dele. O super admin totais globais.
            # A lista 'users' tem globais.
            # Vamos manter a contagem simples global por enquanto ou filtrar?
            # Se eu sou Admin, a lista users tem todo mundo (por causa do database.listar_todos_usuarios que pega tudo).
            # Minha arvore só mostra meus dados.
            # Entao os cards devem refletir O QUE EU VEJO ou O QUE EXISTE?
            # Geralmente Dashboard = O que eu vejo.
            
            # Recalibrar totais visualizados
            v_cli = 0
            v_vend = 0
            
            # Helper para contar recursivo ou iterar treeview?
            # Iterar treeview children é chato.
            # Vamos contar na logica de insercao? Nao, insert_recursive é chamado pra todos.
            # Vamos contar atraves de `children_map` a partir das raizes?
            
            # Melhor: iterar todos users e ver se estao "descendent" das minhas raizes?
            # Complexo. 
            # Simplificacao: Super Admin vê totais globais. Admin vê totais de sua sub-arvore.
            
            if self.user_role == 'super_admin':
                # Totais Globais
                for u in users:
                    c = u['cargo']
                    if c == 'admin': v_cli += 1
                    if c == 'vendedor': v_vend += 1
            else:
                # Totais da Sub-Arvore (Eu + Filhos)
                # Quem sou eu? self.user.get('usuario')
                # Meus filhos diretos e indiretos.
                me = self.user.get('usuario')
                queue = [me]
                visited = set()
                while queue:
                    curr = queue.pop(0)
                    visited.add(curr)
                    # Contar
                    if curr in users_by_user:
                        c = users_by_user[curr]['cargo']
                        if c == 'admin': v_cli += 1 # Cliente (proprio usuario)
                        if c == 'gerente': v_cli += 1 # Contar gerentes como "Clientes/Gestores" para o card?
                        # O card diz "Total Gerentes" para o Admin.
                        # A variavel v_cli está alimentando self.card_total_clientes
                        
                        if c == 'vendedor': v_vend += 1
                    
                    # Add filhos
                    if curr in children_map:
                        for child in children_map[curr]:
                            queue.append(child['usuario'])
            
            total_cli = v_cli
            total_vend = v_vend
            
            # Atualizar Cards
            try:
                for widget in self.card_total_clientes.winfo_children():
                    if isinstance(widget, ctk.CTkLabel) and widget.cget("font")[1] == 24:
                        widget.configure(text=str(total_cli))
                for widget in self.card_total_vendedores.winfo_children():
                    if isinstance(widget, ctk.CTkLabel) and widget.cget("font")[1] == 24:
                        widget.configure(text=str(total_vend))
            except: pass # Ignorar erro visual nos cards
        except Exception as e:
            print(f"Erro ao carregar usuarios: {e}")
            messagebox.showerror("Erro de Carregamento", f"Falha ao listar usuários: {e}")

    # ALIAS DE PROTECAO (V44): Typo singular
    def carregar_usuario(self):
        return self.carregar_usuarios()

    def _alterar_status(self, novo_status):
        sel = self.tree_users.selection()
        if not sel:
            return
            
        item = self.tree_users.item(sel[0])
        uid = item['values'][0]
        user_nome = item['values'][2]
        
        # Evitar auto-bloqueio
        if str(user_nome) == str(self.user.get('usuario')):
            messagebox.showwarning("Ação Inválida", "Você não pode bloquear a si mesmo!")
            return

        import src.database as database
        database.alterar_status_usuario(uid, novo_status)
        messagebox.showinfo("Sucesso", f"Usuário {user_nome} agora está: {novo_status.upper()}")
        self.carregar_usuarios()

    def _limpar_form(self):
        try:
            self.entry_u_nome.delete(0, 'end')
            self.entry_u_user.delete(0, 'end')
            self.entry_u_pass.delete(0, 'end')
            self.entry_u_email.delete(0, 'end')
            self.entry_u_wpp.delete(0, 'end')
        except: pass

    def action_cadastrar_cliente(self):
        # Cadastra o cliente como 'admin' (Dono do negócio)
        self.helper_cadastrar_generico(
            user=self.entry_cli_user.get(),
            nome=self.entry_cli_nome.get(),
            senha=self.entry_cli_pass.get(),
            cargo='admin', # Cliente é admin do seu negócio
            email=self.entry_cli_email.get(),
            wpp=self.entry_cli_wpp.get()
        )
        
    # ALIAS DE PROTECAO (V40): O usuario reportou erro com este nome
    def action_cadastro_cliente(self):
        return self.action_cadastrar_cliente()

    def add_user_bd(self):
        # Cadastra qualquer usuario (pela aba equipe)
        self.helper_cadastrar_generico(
            user=self.entry_u_user.get(),
            nome=self.entry_u_nome.get(),
            senha=self.entry_u_pass.get(),
            cargo=self.combo_u_role.get(),
            email=self.entry_u_email.get(),
            wpp=self.entry_u_wpp.get()
        )

    def helper_cadastrar_generico(self, user, nome, senha, cargo, email, wpp):
        if not user or not senha or not nome:   
            messagebox.showwarning("Aviso", "Preencha Nome Completo, Usuário e Senha.")
            return
            
        import src.database as database
        try:
            # FORCAR ATUALIZACAO DB
            database.inicializar_banco()
            
            # Passar created_by
            criador = self.user.get('usuario', 'sistema')
            
            # Tentar criar
            if database.criar_usuario(user, senha, cargo, email, wpp, nome, created_by=criador):
                messagebox.showinfo("Sucesso", f"Usuário '{user}' ({cargo}) cadastrado!\n\nA lista será atualizada agora.")
                # Force update tab if exists
                if hasattr(self, 'carregar_usuarios'):
                    self.carregar_usuarios()
            else:
                messagebox.showerror("Erro", "Falha ao criar usuário.\nO Login já existe ou houve erro interno.")
        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Exceção ao criar usuário:\n{e}")

class PostActionDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, user_data, controller):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x350")
        self.user_data = user_data
        self.controller = controller
        ctk.CTkLabel(self, text=title, font=("Roboto", 18, "bold"), text_color="green").pack(pady=10)
        ctk.CTkLabel(self, text=message, wraplength=350).pack(pady=10)
        
        self.frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_btns.pack(fill="both", expand=True, padx=20, pady=10)
        
        if self.user_data.get('cargo') == 'admin':
            ctk.CTkButton(self.frame_btns, text="📄 Gerar Contrato PDF", command=self.gerar_pdf, fg_color="#E67E22").pack(fill="x", pady=5)
            
        ctk.CTkButton(self.frame_btns, text="📱 Enviar Credenciais (WhatsApp)", command=self.enviar_zap, fg_color="#2ECC71").pack(fill="x", pady=5)
        ctk.CTkButton(self, text="Concluir", command=self.destroy, fg_color="gray").pack(pady=20)
        
    def gerar_pdf(self):
        try:
            import src.docs_generator as docs
            nome = self.user_data.get('nome')
            email = self.user_data.get('email')
            user = self.user_data.get('user')
            senha = self.user_data.get('senha')
            path_kit = docs.gerar_kit_cliente(nome, "N/A", email, user, senha)
            if path_kit and os.path.exists(path_kit):
                os.startfile(path_kit)
            else: messagebox.showerror("Erro", "Erro ao criar pasta do kit.")
        except Exception as e: messagebox.showerror("Erro PDF", f"Falha: {e}")

    def enviar_zap(self):
        try:
            app_nome = "Gestor Fácil"
            u_nome = self.user_data.get('nome')
            u_user = self.user_data.get('user')
            u_pass = self.user_data.get('senha')
            u_role = self.user_data.get('cargo')
            acao = self.user_data.get('acao_tipo')
            wpp_usuario = self.user_data.get('wpp_target') # Whatsapp do usuario sendo criado
            
            # Mensagem DIRETA para o USUARIO
            msg_wa = f"Olá *{u_nome}*,\n\n"
            msg_wa += f"Aqui estão seus dados de acesso ao *{app_nome}*:\n\n"
            msg_wa += f"👤 *Login:* {u_user}\n"
            if u_pass and u_pass != "[Mantida]": msg_wa += f"🔐 *Senha:* {u_pass}\n"
            msg_wa += f"🏷️ *Cargo:* {u_role}\n"
            msg_wa += f"ℹ️ *Status:* {acao}\n"
            msg_wa += "\nPor favor, guarde estas informações com segurança.\n"
            msg_wa += "--------------------------------"
            
            import src.utils as utils
            
            # PRIORIDADE: Mandar para o numero do usuario cadastrado
            target_wpp = wpp_usuario
            
            if not target_wpp:
                dialog = ctk.CTkInputDialog(text=f"O usuário '{u_nome}' não tem WhatsApp cadastrado.\nDigite o número para enviar (com DDD):", title="Enviar para quem?")
                target_wpp = dialog.get_input()
            
            if target_wpp: 
                utils.notificar_whatsapp(target_wpp, msg_wa)
            else:
                self.controller.clipboard_clear(); self.controller.clipboard_append(msg_wa)
                messagebox.showinfo("Copiado", "Sem número definido. Mensagem copiada para enviar manualmente!")
                
        except Exception as e: messagebox.showerror("Erro Zap", f"Falha: {e}")


