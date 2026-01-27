import customtkinter as ctk
from tkinter import ttk, messagebox
from src.ui.styles import *
import src.database as database
import src.utils as utils
import src.reports as reports
import os

class POSFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.carrinho = [] # Lista de dicts
        self.produtos_cache = []

        # Título
        self.label_titulo = ctk.CTkLabel(self, text="Ponto de Venda", font=FONT_HEADER, text_color=COLOR_TEXT)
        self.label_titulo.pack(pady=10)

        # Layout Split: Esquerda (Produtos), Direita (Carrinho)
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Grid Configuration for Split
        self.container.grid_columnconfigure(0, weight=3) # 60%aprox
        self.container.grid_columnconfigure(1, weight=2) # 40%aprox
        self.container.grid_rowconfigure(0, weight=1)

        # --- Esquerda: Lista de Produtos ---
        self.frame_left = ctk.CTkFrame(self.container, fg_color=COLOR_SURFACE, corner_radius=CORNER_RADIUS)
        self.frame_left.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.filtrar_produtos)
        self.entry_search = ctk.CTkEntry(self.frame_left, placeholder_text="Buscar produto...", 
                                         textvariable=self.search_var, height=40, font=FONT_BODY,
                                         fg_color=COLOR_ENTRY_BG, border_color=COLOR_ENTRY_BORDER, 
                                         text_color=COLOR_TEXT, placeholder_text_color=COLOR_PLACEHOLDER)
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=15)
        
        # Botão Atualizar (Refresh)
        self.btn_refresh = ctk.CTkButton(self.frame_left, text="🔄", width=40, height=40,
                                         fg_color=COLOR_SECONDARY, command=self.carregar_produtos)
        self.btn_refresh.pack(side="right", padx=(0, 10), pady=15)

        # Treeview Produtos
        self.tree_prod = self._criar_treeview(self.frame_left, ("id", "nome", "preco", "estoque"))
        self.tree_prod.heading("id", text="ID")
        self.tree_prod.heading("nome", text="Produto")
        self.tree_prod.heading("preco", text="Preço")
        self.tree_prod.heading("estoque", text="Qtd")
        self.tree_prod.column("id", width=40)
        self.tree_prod.column("nome", width=150)
        self.tree_prod.column("preco", width=80)
        self.tree_prod.column("estoque", width=50)
        self.tree_prod.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Duplo clique para adicionar
        self.tree_prod.bind("<Double-1>", self.adicionar_ao_carrinho)

        # --- Direita: Carrinho ---
        self.frame_right = ctk.CTkFrame(self.container, width=400, fg_color=COLOR_SURFACE, corner_radius=CORNER_RADIUS)
        self.frame_right.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        
        # 1. Topo: Cliente e Titulo
        self.frame_cart_top = ctk.CTkFrame(self.frame_right, fg_color="transparent")
        self.frame_cart_top.pack(side="top", fill="x", padx=10, pady=10)
        
        # Input de Cliente
        ctk.CTkLabel(self.frame_cart_top, text="Cliente (Opcional):", font=FONT_BODY, text_color=COLOR_TEXT).pack(anchor="w")
        self.entry_cliente = ctk.CTkEntry(self.frame_cart_top, placeholder_text="Nome / Nuit do Cliente",
                                          fg_color=COLOR_ENTRY_BG, border_color=COLOR_ENTRY_BORDER, 
                                          text_color=COLOR_TEXT, placeholder_text_color=COLOR_PLACEHOLDER)
        self.entry_cliente.pack(fill="x", pady=2)

        ctk.CTkLabel(self.frame_cart_top, text="Carrinho", font=FONT_SUBHEADER, text_color=COLOR_TEXT).pack(pady=(10, 0))
        
        # 2. Rodapé: Ações e Total (PINNED BOTTOM)
        self.frame_cart_actions = ctk.CTkFrame(self.frame_right, fg_color="transparent")
        self.frame_cart_actions.pack(side="bottom", fill="x", padx=10, pady=10)
        
        self.lbl_total = ctk.CTkLabel(self.frame_cart_actions, text="TOTAL: 0.00 MT", font=FONT_BIG_NUMBER, text_color=COLOR_SUCCESS)
        self.lbl_total.pack(pady=5)
        
        self.btn_limpar = ctk.CTkButton(self.frame_cart_actions, text="Limpar", fg_color=COLOR_DANGER, hover_color="#D50000",
                                        command=self.limpar_carrinho, height=35)
        self.btn_limpar.pack(fill="x", pady=5)
        
        self.btn_finalizar = ctk.CTkButton(self.frame_cart_actions, text="FINALIZAR VENDA", fg_color=COLOR_PRIMARY, 
                                           hover_color=COLOR_PRIMARY_HOVER, height=60, font=FONT_HEADER, 
                                           text_color=COLOR_TEXT_INVERSE, command=self.finalizar_venda)
        self.btn_finalizar.pack(fill="x", pady=(5, 10))
        
        self.btn_cotacao = ctk.CTkButton(self.frame_cart_actions, text="📄 Gerar Cotação", 
                                          fg_color=COLOR_WARNING, hover_color="#F57F17",
                                          command=self.gerar_cotacao_pdf, height=40)
        self.btn_cotacao.pack(fill="x", pady=(5, 0))

        self.btn_imprimir = ctk.CTkButton(self.frame_cart_actions, text="🖨️ Imprimir Último Recibo", 
                                          fg_color=COLOR_SECONDARY, hover_color="#1565C0",
                                          command=self.imprimir_recibo, height=40)
        self.btn_imprimir.pack(fill="x", pady=5)

        # 3. Meio: Treeview (EXPAND)
        self.frame_cart_list = ctk.CTkFrame(self.frame_right, fg_color="transparent")
        self.frame_cart_list.pack(side="top", fill="both", expand=True, padx=10, pady=0)
        
        # Treeview Carrinho
        self.tree_cart = self._criar_treeview(self.frame_cart_list, ("nome", "qtd", "total"))
        self.tree_cart.heading("nome", text="Produto")
        self.tree_cart.heading("qtd", text="Qtd")
        self.tree_cart.heading("total", text="Total")
        self.tree_cart.column("nome", width=150)
        self.tree_cart.column("qtd", width=50)
        self.tree_cart.column("total", width=80)
        self.tree_cart.pack(fill="both", expand=True)
        
        # Binding para editar quantidade
        self.tree_cart.bind("<Double-1>", self.editar_item_carrinho)

        # Carregar inicial
        self.carregar_produtos()
        
        self.ultimo_recibo = None

    def _criar_treeview(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        return tree

    def carregar_produtos(self):
        self.produtos_cache = database.listar_produtos()
        self.atualizar_lista_prod(self.produtos_cache)

    def atualizar_lista_prod(self, produtos):
        for item in self.tree_prod.get_children():
            self.tree_prod.delete(item)
        for p in produtos:
            if p['quantidade'] > 0: # Só mostra com stock
                self.tree_prod.insert("", "end", values=(p['id'], p['nome'], f"{p['preco_venda']:.2f}", p['quantidade']))

    def filtrar_produtos(self, *args):
        termo = self.search_var.get().lower()
        if not termo:
            self.atualizar_lista_prod(self.produtos_cache)
        else:
            filtrados = [p for p in self.produtos_cache if termo in p['nome'].lower()]
            self.atualizar_lista_prod(filtrados)

    def adicionar_ao_carrinho(self, event):
        selected_item = self.tree_prod.selection()
        if not selected_item: return
        
        item_vals = self.tree_prod.item(selected_item)['values']
        prod_id = item_vals[0]
        
        # Encontrar produto completo no cache
        produto_real = next((p for p in self.produtos_cache if p['id'] == prod_id), None)
        if not produto_real: return

        # Verificar se já está no carrinho
        for item in self.carrinho:
            if item['id'] == prod_id:
                if item['qtd'] < produto_real['quantidade']:
                    item['qtd'] += 1
                    item['total'] = item['qtd'] * item['preco_venda']
                    self.atualizar_carrinho()
                return

        # Novo item
        self.carrinho.append({
            'id': prod_id,
            'nome': produto_real['nome'],
            'preco_custo': produto_real['preco_custo'],
            'preco_venda': produto_real['preco_venda'],
            'qtd': 1,
            'total': produto_real['preco_venda']
        })
        self.atualizar_carrinho()
    
    def editar_item_carrinho(self, event):
        selected_item = self.tree_cart.selection()
        if not selected_item: return
        
        idx = self.tree_cart.index(selected_item)
        item = self.carrinho[idx]
        
        # Popup Simples para quantidade
        dialog = ctk.CTkInputDialog(text=f"Nova quantidade para '{item['nome']}':", title="Editar Carrinho")
        nova_qtd_str = dialog.get_input()
        
        if nova_qtd_str:
            try:
                nova_qtd = int(nova_qtd_str)
                # Validar estoque
                produto_real = next((p for p in self.produtos_cache if p['id'] == item['id']), None)
                if produto_real:
                    if nova_qtd <= 0:
                        # Remover
                        del self.carrinho[idx]
                    elif nova_qtd <= produto_real['quantidade']:
                        item['qtd'] = nova_qtd
                        item['total'] = nova_qtd * item['preco_venda']
                    else:
                        messagebox.showwarning("Stock Insuficiente", f"Só existem {produto_real['quantidade']} unidades disponíveis.")
                
                self.atualizar_carrinho()
            except ValueError:
                messagebox.showerror("Erro", "Quantidade inválida.")

    def atualizar_carrinho(self):
        for item in self.tree_cart.get_children():
            self.tree_cart.delete(item)
        
        total_geral = 0
        for item in self.carrinho:
            self.tree_cart.insert("", "end", values=(item['nome'], item['qtd'], f"{item['total']:.2f}"))
            total_geral += item['total']
            
        self.lbl_total.configure(text=f"TOTAL: {utils.formatar_moeda(total_geral)}")

    def limpar_carrinho(self):
        self.carrinho = []
        self.atualizar_carrinho()
        self.entry_cliente.delete(0, ctk.END) # Clear client input

    def finalizar_venda(self):
        # PASSO 1: Verificar se há itens no carrinho
        if not self.carrinho:
            return

        # PASSO 2: Calcular Totais Matemáticos
        total_venda = sum(i['total'] for i in self.carrinho)
        total_custo = sum(i['qtd'] * i['preco_custo'] for i in self.carrinho)
        lucro = total_venda - total_custo
        
        # PASSO 3: Identificar Cliente e Vendedor
        cliente = self.entry_cliente.get().strip() or "Consumidor Final"
        
        # Preparar lista apenas com IDs para o Banco de Dados
        itens_db = [(i['id'], i['qtd'], i['preco_venda']) for i in self.carrinho]
        
        try:
            # PASSO 4: Identificar QUEM está vendendo (Segurança/Rastreio)
            v_id = None
            v_nome = None
            if hasattr(self.master, 'usuario_atual') and self.master.usuario_atual:
                v_id = self.master.usuario_atual.get('id')
                v_nome = self.master.usuario_atual.get('usuario') 
                if self.master.usuario_atual.get('nome_completo'):
                     v_nome = self.master.usuario_atual.get('nome_completo')
            
            # PASSO 5: Gravar no Banco de Dados (Database.py faz o trabalho pesado)
            venda_id = database.registar_venda(itens_db, total_venda, lucro, cliente, vendedor_id=v_id, vendedor_nome=v_nome)
            print("Venda registada com sucesso!") # Log no terminal
            
            # Preparar info do vendedor
            vendedor_info = None
            if hasattr(self.master, 'usuario_atual') and self.master.usuario_atual:
                nome_exib = self.master.usuario_atual.get('nome_completo')
                if not nome_exib:
                     nome_exib = self.master.usuario_atual['usuario']
                     
                vendedor_info = {
                   'nome': nome_exib,
                   'email': self.master.usuario_atual.get('email', ''),
                   'whatsapp': self.master.usuario_atual.get('whatsapp', '')
                }
            
            # Gerar Recibo
            path = reports.gerar_recibo(venda_id, vendedor_info)
            self.ultimo_recibo = path
            
            # Perguntar se quer imprimir
            if path:
                if messagebox.askyesno("Venda Sucesso", "Venda finalizada! Deseja imprimir/abrir o recibo?"):
                    self.imprimir_recibo()
            
            # Reset
            self.limpar_carrinho()
            self.carregar_produtos() # Reload stock
            
        except Exception as e:
            print(f"Erro ao finalizar venda: {e}")
            messagebox.showerror("Erro", f"Falha na venda: {e}")

    def gerar_cotacao_pdf(self):
        if not self.carrinho:
            messagebox.showwarning("Vazio", "Adicione itens ao carrinho para gerar cotação.")
            return

        total = sum(i['total'] for i in self.carrinho)
        cliente = self.entry_cliente.get().strip() or "Consumidor Final"
        
        # Preparar info do vendedor
        vendedor_info = None
        if hasattr(self.master, 'usuario_atual') and self.master.usuario_atual:
             nome_exib = self.master.usuario_atual.get('nome_completo')
             if not nome_exib:
                 nome_exib = self.master.usuario_atual['usuario']
                 
             vendedor_info = {
               'nome': nome_exib,
               'email': self.master.usuario_atual.get('email', ''),
               'whatsapp': self.master.usuario_atual.get('whatsapp', '')
            }

        # Chamada ao report sem gravar no banco
        path = reports.gerar_cotacao(self.carrinho, total, cliente, vendedor_info)
        
        if path:
            if messagebox.askyesno("Cotação Gerada", "Cotação gerada com sucesso!\nDeseja abrir o arquivo PDF?"):
                try:
                    os.startfile(path)
                except:
                    pass
        else:
            messagebox.showerror("Erro", "Falha ao gerar cotação.")

    def imprimir_recibo(self):
        if self.ultimo_recibo and os.path.exists(self.ultimo_recibo):
            try:
                os.startfile(self.ultimo_recibo)
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível abrir o recibo: {e}")
        else:
            messagebox.showinfo("Aviso", "Nenhum recibo recente disponível.")
