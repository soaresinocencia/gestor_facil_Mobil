import customtkinter as ctk
from tkinter import ttk, messagebox
from src.ui.styles import *
import src.database as database

class StockFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Título
        self.label_titulo = ctk.CTkLabel(self, text="Gestão de Stock", font=FONT_HEADER, text_color=COLOR_TEXT)
        self.label_titulo.pack(pady=10)

        # Container do Formulário e da Tabela
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # --- Formulário de Cadastro ---
        self.frame_form = ctk.CTkFrame(self.container, fg_color=COLOR_SURFACE, corner_radius=CORNER_RADIUS)
        self.frame_form.pack(side="top", fill="x", padx=10, pady=10)
        
        # Grid layout para o form - Reorganizado
        self.entry_nome = self._criar_campo(self.frame_form, "Nome do Produto", 0, 0, width=250)
        
        # Categoria (ComboBox)
        frame_cat = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        frame_cat.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(frame_cat, text="Categoria", font=FONT_SMALL, text_color=COLOR_TEXT).pack(anchor="w")
        self.combo_categoria = ctk.CTkComboBox(frame_cat, values=["Geral", "Alimentação", "Bebidas", "Limpeza", "Higiene", "Eletrônicos", "Outros"],
                                               width=150, fg_color=COLOR_ENTRY_BG, border_color=COLOR_ENTRY_BORDER, text_color=COLOR_TEXT)
        self.combo_categoria.pack()
        
        self.entry_custo = self._criar_campo(self.frame_form, "Preço Custo (MT)", 0, 2)
        self.entry_qtd = self._criar_campo(self.frame_form, "Quantidade", 0, 3)

        self.entry_detalhes = self._criar_campo(self.frame_form, "Detalhes (Marca, Validade...)", 1, 0, width=250)
        self.entry_venda = self._criar_campo(self.frame_form, "Preço Venda (MT)", 1, 1)
        self.entry_min = self._criar_campo(self.frame_form, "Alerta Mínimo", 1, 2)
        
        # Botões
        self.frame_btns = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        self.frame_btns.grid(row=2, column=0, columnspan=4, pady=10, sticky="ew")
        
        self.btn_adicionar = ctk.CTkButton(self.frame_btns, text="Adicionar", 
                                           command=self.adicionar_produto, fg_color=COLOR_PRIMARY, 
                                           hover_color=COLOR_PRIMARY_HOVER, text_color=COLOR_TEXT_INVERSE, width=100)
        self.btn_adicionar.pack(side="left", padx=5)

        self.btn_atualizar = ctk.CTkButton(self.frame_btns, text="Atualizar", 
                                           command=self.atualizar_produto, fg_color=COLOR_WARNING, width=100)
        self.btn_atualizar.pack(side="left", padx=5)

        self.btn_remover = ctk.CTkButton(self.frame_btns, text="Remover", 
                                           command=self.remover_produto, fg_color=COLOR_DANGER, width=100)
        self.btn_remover.pack(side="left", padx=5)

        self.btn_limpar = ctk.CTkButton(self.frame_btns, text="Limpar", 
                                           command=self.limpar_form, fg_color=COLOR_SECONDARY, width=100)
        self.btn_limpar.pack(side="left", padx=5)

        # Variável para controlar edição
        self.produto_selecionado_id = None

        # --- Tabela de Listagem ---
        self.frame_tabela = ctk.CTkFrame(self.container, fg_color=COLOR_SURFACE, corner_radius=CORNER_RADIUS)
        self.frame_tabela.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)
        
        # Treeview Style
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background=COLOR_SURFACE, 
                        foreground="white", 
                        fieldbackground=COLOR_SURFACE,
                        rowheight=30)
        style.map("Treeview", background=[("selected", COLOR_PRIMARY)])
        
        columns = ("id", "nome", "cat", "detalhes", "custo", "venda", "qtd", "min")
        self.tree = ttk.Treeview(self.frame_tabela, columns=columns, show="headings", height=15)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Produto")
        self.tree.heading("cat", text="Categoria")
        self.tree.heading("detalhes", text="Detalhes")
        self.tree.heading("custo", text="Custo")
        self.tree.heading("venda", text="Venda")
        self.tree.heading("qtd", text="Qtd")
        self.tree.heading("min", text="Min")
        
        self.tree.column("id", width=40)
        self.tree.column("nome", width=180)
        self.tree.column("cat", width=100)
        self.tree.column("detalhes", width=120)
        self.tree.column("custo", width=70)
        self.tree.column("venda", width=70)
        self.tree.column("qtd", width=60)
        self.tree.column("min", width=50)
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.frame_tabela, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.bind("<<TreeviewSelect>>", self.selecionar_produto)

        # Lista de sugestões
        self.lista_sugestoes = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, width=300, height=0)
        
        # Binding para autocomplete
        self.entry_nome.bind("<KeyRelease>", self.on_key_release)
        self.entry_nome.bind("<FocusOut>", lambda e: self.esconder_sugestoes())
        
        # Permissões: Se for vendedor, esconder botões de ação (somente leitura)
        is_admin = True
        if hasattr(self.master, 'usuario_atual') and self.master.usuario_atual:
             if self.master.usuario_atual['cargo'] == 'vendedor':
                 is_admin = False
        
        if not is_admin:
            self.frame_btns.grid_remove() # Remove botões de Adicionar/Editar
            ctk.CTkLabel(self.frame_form, text="Modo Visualização (Vendedor)", text_color=COLOR_WARNING).grid(row=2, column=0, columnspan=4)
        
        self.carregar_dados()

    def _criar_campo(self, parent, label_text, row, col, width=150):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, padx=10, pady=5, sticky="w")
        
        lbl = ctk.CTkLabel(frame, text=label_text, font=FONT_SMALL, text_color=COLOR_TEXT)
        lbl.pack(anchor="w")
        
        entry = ctk.CTkEntry(frame, width=width, 
                             fg_color=COLOR_ENTRY_BG, border_color=COLOR_ENTRY_BORDER, 
                             text_color=COLOR_TEXT, placeholder_text_color=COLOR_PLACEHOLDER)
        entry.pack()
        return entry

    def on_key_release(self, event):
        typed = self.entry_nome.get()
        if len(typed) < 2:
            self.esconder_sugestoes()
            return
            
        conn = database.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM produtos WHERE lower(nome) LIKE ? LIMIT 5", (f"{typed.lower()}%",))
        matches = [r['nome'] for r in cursor.fetchall()]
        conn.close()
        
        if matches:
            self.mostrar_sugestoes(matches)
        else:
            self.esconder_sugestoes()

    def mostrar_sugestoes(self, matches):
        if not hasattr(self, 'sugestao_window') or not self.sugestao_window:
            self.sugestao_window = ctk.CTkToplevel(self)
            self.sugestao_window.wm_overrideredirect(True)
            self.sugestao_window.attributes("-topmost", True)
            self.frame_matches = ctk.CTkFrame(self.sugestao_window, fg_color=COLOR_SURFACE, border_width=1, border_color=COLOR_BORDER)
            self.frame_matches.pack(fill="both", expand=True)

        # Atualizar posição
        x = self.entry_nome.winfo_rootx()
        y = self.entry_nome.winfo_rooty() + self.entry_nome.winfo_height()
        self.sugestao_window.wm_geometry(f"300x{len(matches)*35}+{x}+{y}")

        # Limpar anteriores
        for widget in self.frame_matches.winfo_children():
            widget.destroy()

        for nome in matches:
            btn = ctk.CTkButton(self.frame_matches, text=nome, anchor="w", fg_color="transparent", 
                                hover_color=COLOR_PRIMARY, height=30, text_color=COLOR_TEXT,
                                command=lambda n=nome: self.selecionar_sugestao(n))
            btn.pack(fill="x")

    def esconder_sugestoes(self):
        self.after(200, self._destruir_janela_sugestao)
        
    def _destruir_janela_sugestao(self):
        if hasattr(self, 'sugestao_window') and self.sugestao_window:
            self.sugestao_window.destroy()
            self.sugestao_window = None

    def selecionar_sugestao(self, nome):
        prod = database.get_produto_por_nome(nome)
        if prod:
            self.preencher_formulario(prod)

    def preencher_formulario(self, prod):
        self.produto_selecionado_id = prod['id']
        self.entry_nome.delete(0, 'end')
        self.entry_nome.insert(0, prod['nome'])
        
        self.entry_custo.delete(0, 'end')
        self.entry_custo.insert(0, str(prod['preco_custo']))
        
        self.entry_venda.delete(0, 'end')
        self.entry_venda.insert(0, str(prod['preco_venda']))
        
        self.entry_qtd.delete(0, 'end')
        self.entry_qtd.insert(0, str(prod['quantidade'])) 
        
        self.entry_min.delete(0, 'end')
        self.entry_min.insert(0, str(prod['minimo_alerta']))

        self.entry_detalhes.delete(0, 'end')
        # Verificar se chave 'detalhes' existe (backward compatibility)
        if 'detalhes' in prod.keys() and prod['detalhes']:
            self.entry_detalhes.insert(0, prod['detalhes'])

        if 'categoria' in prod.keys() and prod['categoria']:
            self.combo_categoria.set(prod['categoria'])
        else:
            self.combo_categoria.set("Geral")

    def adicionar_produto(self):
        nome = self.entry_nome.get()
        detalhes = self.entry_detalhes.get()
        
        # Verificar existência por Nome E Detalhes para permitir variações
        existe = database.get_produto_unico(nome, detalhes)
        
        if existe:
            # Se for EXATAMENTE o mesmo produto (mesmo nome e detalhes), pergunta se quer atualizar
            if messagebox.askyesno("Duplicado", f"O produto '{nome}' com detalhes '{detalhes}' já existe.\nDeseja ATUALIZAR este item específico?"):
                self.produto_selecionado_id = existe['id']
                self.atualizar_produto()
            return
            
        try:
            custo = float(self.entry_custo.get())
            venda = float(self.entry_venda.get())
            qtd = int(self.entry_qtd.get())
            min_alerta = int(self.entry_min.get())
            # detalhes pegamos no inicio
            categoria = self.combo_categoria.get()
            
            database.adicionar_produto(nome, custo, venda, qtd, min_alerta, detalhes, categoria)
            self.limpar_form()
            self.carregar_dados()
            print("Produto adicionado.")
        except ValueError:
            messagebox.showerror("Erro", "Verifique os números inseridos.")

    def atualizar_produto(self):
        if not self.produto_selecionado_id:
            messagebox.showwarning("Aviso", "Selecione um produto para atualizar.")
            return

        try:
            nome = self.entry_nome.get()
            custo = float(self.entry_custo.get())
            venda = float(self.entry_venda.get())
            qtd = int(self.entry_qtd.get())
            min_alerta = int(self.entry_min.get())
            detalhes = self.entry_detalhes.get()
            categoria = self.combo_categoria.get()
            
            database.atualizar_produto(self.produto_selecionado_id, nome, custo, venda, qtd, min_alerta, detalhes, categoria)
            self.limpar_form()
            self.carregar_dados()
            print("Produto atualizado.")
        except ValueError:
            messagebox.showerror("Erro", "Verifique os números inseridos.")

    def remover_produto(self):
        if not self.produto_selecionado_id:
            messagebox.showwarning("Aviso", "Selecione um produto para remover.")
            return

        if messagebox.askyesno("Confirmar", "Tem certeza que deseja remover este produto?"):
            database.remover_produto(self.produto_selecionado_id)
            self.limpar_form()
            self.carregar_dados()
            print("Produto removido.")

    def selecionar_produto(self, event):
        selected_item = self.tree.selection()
        if not selected_item: return
        
        item = self.tree.item(selected_item)
        values = item['values'] 
        # (id, nome, cat, detalhes, custo, venda, qtd, min)
        
        self.produto_selecionado_id = values[0]
        
        self.entry_nome.delete(0, 'end')
        self.entry_nome.insert(0, values[1])
        
        self.combo_categoria.set(values[2])
        
        self.entry_detalhes.delete(0, 'end')
        self.entry_detalhes.insert(0, values[3])

        self.entry_custo.delete(0, 'end')
        self.entry_custo.insert(0, values[4])
        
        self.entry_venda.delete(0, 'end')
        self.entry_venda.insert(0, values[5])
        
        self.entry_qtd.delete(0, 'end')
        self.entry_qtd.insert(0, values[6])
        
        self.entry_min.delete(0, 'end')
        self.entry_min.insert(0, values[7])

    def limpar_form(self):
        self.produto_selecionado_id = None
        self.entry_nome.delete(0, 'end')
        self.entry_custo.delete(0, 'end')
        self.entry_venda.delete(0, 'end')
        self.entry_qtd.delete(0, 'end')
        self.entry_min.delete(0, 'end')
        self.entry_detalhes.delete(0, 'end')
        self.combo_categoria.set("Geral")
        
    def carregar_dados(self):
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        produtos = database.listar_produtos()
        for p in produtos:
            # Check alerta de stock
            tags = ()
            if p['quantidade'] <= p['minimo_alerta']:
                tags = ('alerta',)
            
            # Handle backward compatibility for new columns
            cat = p['categoria'] if 'categoria' in p.keys() and p['categoria'] else "Geral"
            det = p['detalhes'] if 'detalhes' in p.keys() and p['detalhes'] else ""

            self.tree.insert("", "end", values=(
                p['id'], p['nome'], cat, det,
                f"{p['preco_custo']:.2f}", 
                f"{p['preco_venda']:.2f}", 
                p['quantidade'], 
                p['minimo_alerta']
            ), tags=tags)
        
        # Configurar cor de alerta
        self.tree.tag_configure('alerta', foreground=COLOR_DANGER)
