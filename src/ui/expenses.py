import customtkinter as ctk
from tkinter import ttk, messagebox
from src.ui.styles import *
import src.database as database
import src.utils as utils

class ExpensesFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Título
        self.label_titulo = ctk.CTkLabel(self, text="Gestão de Despesas", font=FONT_HEADER, text_color=COLOR_TEXT)
        self.label_titulo.pack(pady=10)

        # Container Principal
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # --- Formulário ---
        self.frame_form = ctk.CTkFrame(self.container, fg_color=COLOR_SURFACE, corner_radius=CORNER_RADIUS)
        self.frame_form.pack(side="top", fill="x", padx=10, pady=10)
        
        # Grid layout
        self.entry_desc = self._criar_campo(self.frame_form, "Descrição da Despesa", 0, 0, width=300)
        
        # Categoria (ComboBox)
        frame_cat = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        frame_cat.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(frame_cat, text="Categoria", font=FONT_SMALL, text_color=COLOR_TEXT).pack(anchor="w")
        self.combo_categoria = ctk.CTkComboBox(frame_cat, values=["Água/Luz", "Aluguel", "Salários", "Fornecedores", "Transporte", "Manutenção", "Outros"],
                                               width=150, fg_color=COLOR_ENTRY_BG, border_color=COLOR_ENTRY_BORDER, text_color=COLOR_TEXT)
        self.combo_categoria.pack()
        
        self.entry_valor = self._criar_campo(self.frame_form, "Valor (MT)", 0, 2)
        
        self.btn_adicionar = ctk.CTkButton(self.frame_form, text="Lançar Despesa", 
                                           command=self.adicionar_despesa, fg_color=COLOR_DANGER, 
                                           hover_color="#D50000", text_color=COLOR_TEXT_INVERSE)
        self.btn_adicionar.grid(row=0, column=3, padx=20, pady=15, sticky="ew")

        # --- Tabela ---
        self.frame_tabela = ctk.CTkFrame(self.container, fg_color=COLOR_SURFACE, corner_radius=CORNER_RADIUS)
        self.frame_tabela.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)
        
        columns = ("id", "data", "desc", "cat", "valor")
        self.tree = ttk.Treeview(self.frame_tabela, columns=columns, show="headings", height=15)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("data", text="Data/Hora")
        self.tree.heading("desc", text="Descrição")
        self.tree.heading("cat", text="Categoria")
        self.tree.heading("valor", text="Valor")
        
        self.tree.column("id", width=50)
        self.tree.column("data", width=150)
        self.tree.column("desc", width=250)
        self.tree.column("cat", width=150)
        self.tree.column("valor", width=100)
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(self.frame_tabela, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Botão Remover Selecionado
        self.btn_remover = ctk.CTkButton(self.frame_tabela, text="Remover Selecionada", 
                                         command=self.remover_despesa, fg_color=COLOR_DANGER, height=30)
        self.btn_remover.pack(side="bottom", pady=10)

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

    def adicionar_despesa(self):
        desc = self.entry_desc.get()
        cat = self.combo_categoria.get()
        val_str = self.entry_valor.get()
        
        if not desc or not val_str:
            messagebox.showwarning("Aviso", "Preencha a descrição e o valor.")
            return

        try:
            valor = float(val_str)
            database.adicionar_despesa(desc, cat, valor)
            self.entry_desc.delete(0, 'end')
            self.entry_valor.delete(0, 'end')
            self.carregar_dados()
            print("Despesa adicionada.")
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido.")
            
    def remover_despesa(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        if messagebox.askyesno("Confirmar", "Remover esta despesa?"):
            item = self.tree.item(selected)
            id_despesa = item['values'][0]
            database.remover_despesa(id_despesa)
            self.carregar_dados()

    def carregar_dados(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        despesas = database.listar_despesas()
        for d in despesas:
            self.tree.insert("", "end", values=(
                d['id'], d['data_hora'], d['descricao'], d['categoria'], f"{d['valor']:.2f}"
            ))
