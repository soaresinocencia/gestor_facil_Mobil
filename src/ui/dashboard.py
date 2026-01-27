import customtkinter as ctk
from src.ui.styles import *
import src.database as database
import src.utils as utils
import src.reports as reports
import src.charts as charts
from datetime import datetime
from tkinter import messagebox
import os

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.label_titulo = ctk.CTkLabel(self, text="Dashboard Financeiro", font=FONT_HEADER, text_color=COLOR_TEXT)
        self.label_titulo.pack(pady=20)

        self.container_scr = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.container_scr.pack(fill="both", expand=True, padx=0, pady=0)
        
        self.container_cards = ctk.CTkFrame(self.container_scr, fg_color="transparent")
        self.container_cards.pack(fill="x", padx=20, pady=20)
        
        # Cards
        self.card_vendas = self._criar_card(self.container_cards, "Vendas Hoje", "0")
        self.card_vendas.pack(side="left", fill="both", expand=True, padx=10)
        
        self.card_faturamento = self._criar_card(self.container_cards, "Faturamento Hoje", "0.00 MT")
        self.card_faturamento.pack(side="left", fill="both", expand=True, padx=10)
        
        self.card_lucro = self._criar_card(self.container_cards, "Lucro Líquido Hoje", "0.00 MT", destaque=True)
        self.card_lucro.pack(side="left", fill="both", expand=True, padx=10)

        
        # --- Área Principal (Split) ---
        # --- Área Principal (Split) ---
        self.frame_main = ctk.CTkFrame(self.container_scr, fg_color="transparent")
        self.frame_main.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Coluna Esquerda: Gráficos
        self.left_col = ctk.CTkFrame(self.frame_main, fg_color="transparent")
        self.left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Gráfico 1: Vendas 7 Dias
        self.frame_grafico = ctk.CTkFrame(self.left_col, fg_color=COLOR_SURFACE, corner_radius=CORNER_RADIUS) 
        self.frame_grafico.pack(fill="x", pady=(0, 10))
        self.lbl_grafico_img = ctk.CTkLabel(self.frame_grafico, text="")
        self.lbl_grafico_img.pack(padx=10, pady=10)

        # Gráfico 2: Top Produtos (NOVO)
        self.frame_top_prod = ctk.CTkFrame(self.left_col, fg_color=COLOR_SURFACE, corner_radius=CORNER_RADIUS)
        self.frame_top_prod.pack(fill="x", pady=(10, 0))
        self.lbl_grafico_top = ctk.CTkLabel(self.frame_top_prod, text="Carregando Produtos Mais Vendidos...")
        self.lbl_grafico_top.pack(padx=10, pady=10)


        # Coluna Direita: Alertas e Ações
        self.right_col = ctk.CTkFrame(self.frame_main, width=300, fg_color="transparent")
        self.right_col.pack(side="right", fill="y", padx=(10, 0))
        
        # Botões de Ação (Topo Direita)
        self.btn_atualizar = ctk.CTkButton(self.right_col, text="Atualizar Dados", command=self.atualizar_dashboard,
                                           fg_color=COLOR_SURFACE, hover_color=COLOR_SURFACE_HOVER, text_color=COLOR_TEXT)
        self.btn_atualizar.pack(fill="x", pady=(0, 10))

        self.btn_relatorio = ctk.CTkButton(self.right_col, text="📄 Relatório Mensal", 
                                           command=self.gerar_relatorio, 
                                           fg_color=COLOR_SECONDARY, hover_color="#1565C0", 
                                           text_color="white", font=FONT_BODY_BOLD, height=40)
        self.btn_relatorio.pack(fill="x", pady=(0, 20))
        
        # Alerta de Stock Baixo (NOVO)
        self.frame_alert = ctk.CTkFrame(self.right_col, fg_color=COLOR_SURFACE, corner_radius=CORNER_RADIUS)
        self.frame_alert.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(self.frame_alert, text="⚠️ Alerta de Stock", font=FONT_SUBHEADER, text_color=COLOR_DANGER).pack(pady=(15, 5))
        
        # Container scrolavel para a lista
        self.scroll_alert = ctk.CTkScrollableFrame(self.frame_alert, height=150, fg_color="transparent")
        self.scroll_alert.pack(fill="x", padx=10, pady=10)
        self.lbl_lista_alertas = ctk.CTkLabel(self.scroll_alert, text="Sem alertas.", font=FONT_SMALL, text_color=COLOR_TEXT_DIM)
        self.lbl_lista_alertas.pack()

        
        # --- Secção de Suporte (QR Code) ---
        self.frame_suporte = ctk.CTkFrame(self.right_col, fg_color=COLOR_SURFACE, corner_radius=CORNER_RADIUS)
        self.frame_suporte.pack(fill="x", pady=10)
        
        ctk.CTkLabel(self.frame_suporte, text="Suporte WhatsApp", font=FONT_BODY_BOLD, text_color=COLOR_TEXT).pack(pady=(10, 5))

        try:
            # QR Code pequeno para caber na coluna
            qr_path = utils.gerar_qr_suporte("258849343350")
            pil_qr = utils.Image.open(qr_path)
            self.qr_image = ctk.CTkImage(light_image=pil_qr, dark_image=pil_qr, size=(100, 100))
            self.lbl_qr = ctk.CTkLabel(self.frame_suporte, image=self.qr_image, text="")
            self.lbl_qr.pack(pady=5)
            
            self.lbl_num = ctk.CTkLabel(self.frame_suporte, text="+258 84 934 3350", font=FONT_SMALL, text_color=COLOR_SUCCESS)
            self.lbl_num.pack()
            
            self.btn_wpp = ctk.CTkButton(self.frame_suporte, text="Abrir no PC", 
                                         command=lambda: os.system("start https://wa.me/258849343350"),
                                         width=100, height=30, fg_color=COLOR_SUCCESS, hover_color=COLOR_PRIMARY_HOVER)
            self.btn_wpp.pack(pady=10)
            
        except Exception as e:
            print(f"Erro ao carregar QR Code: {e}")
        self.atualizar_dashboard()

    def gerar_relatorio(self):
        hoje = datetime.now()
        try:
            path = reports.gerar_relatorio_mensal(hoje.year, hoje.month)
            if path:
                messagebox.showinfo("Sucesso", f"Relatório gerado em:\n{path}")
                # Abrir automaticamente (Windows)
                try:
                    os.startfile(path)
                except:
                    pass
            else:
                messagebox.showwarning("Aviso", "Não foi possível gerar o relatório. Verifique se há vendas.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar relatório: {e}")

    def _criar_card(self, parent, titulo, valor_inicial, destaque=False):
        color = COLOR_PRIMARY if destaque else COLOR_SURFACE
        text_col = COLOR_TEXT_INVERSE if destaque else COLOR_TEXT
        
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=CORNER_RADIUS)
        
        lbl_titulo = ctk.CTkLabel(card, text=titulo, font=FONT_SMALL, text_color=text_col)
        lbl_titulo.pack(pady=(15, 5))
        
        # Usar fonte maior para o número
        lbl_valor = ctk.CTkLabel(card, text=valor_inicial, font=FONT_BIG_NUMBER, text_color=text_col)
        lbl_valor.pack(pady=(0, 15))
        
        # Armazenar referência para atualizar
        card.lbl_valor = lbl_valor
        return card

    def atualizar_dashboard(self):
        # 1. Atualizar Métricas
        fat, luc, num = database.get_resumo_hoje()
        
        self.card_vendas.lbl_valor.configure(text=str(num))
        self.card_faturamento.lbl_valor.configure(text=utils.formatar_moeda(fat))
        self.card_lucro.lbl_valor.configure(text=utils.formatar_moeda(luc))

        # 2. Atualizar Gráfico
        # 2. Atualizar Gráfico Vendas 7 Dias
        try:
            # Usar pasta temporária para garantir permissão de escrita
            grafico_path = utils.get_writable_path("dashboard_chart.png")
            
            sucesso = charts.gerar_grafico_vendas_7dias(grafico_path)
            
            if sucesso:
                pil_img = utils.Image.open(grafico_path)
                # FORNECER AMBAS AS IMAGENS (Light e Dark) para garantir visualização
                img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(500, 250))
                self.lbl_grafico_img.configure(image=img, text="")
                self.lbl_grafico_img.image = img 
            else:
                self.lbl_grafico_img.configure(text="Sem dados para gráfico", image=None)
                
        except Exception as e:
            err_msg = f"Erro no Gráfico 7 Dias: {e}"
            print(err_msg)
            self.lbl_grafico_img.configure(text=err_msg)
            # Mostrar popup apenas se for erro crítico (não sem dados)
            # messagebox.showerror("Erro Dashboard", err_msg)

        # 3. Atualizar Gráfico Top Produtos
        try:
            top_path = utils.get_writable_path("dashboard_top.png")
            sucesso_top = charts.gerar_grafico_top_produtos(top_path)
            
            if sucesso_top:
                pil_img_top = utils.Image.open(top_path)
                img_top = ctk.CTkImage(light_image=pil_img_top, dark_image=pil_img_top, size=(500, 300))
                self.lbl_grafico_top.configure(image=img_top, text="")
                self.lbl_grafico_top.image = img_top
            else:
                self.lbl_grafico_top.configure(text="Sem dados de produtos", image=None)
        except Exception as e:
            print(f"Erro ao atualizar gráfico top: {e}")
            self.lbl_grafico_top.configure(text=f"Erro Top: {e}")
            
        # 4. Atualizar Alertas de Stock
        try:
            # Limpar lista atual
            for widget in self.scroll_alert.winfo_children():
                widget.destroy()
                
            produtos_baixo = database.get_produtos_baixo_stock()
            
            if produtos_baixo:
                for p in produtos_baixo: # (nome, qtd, min)
                    frame_p = ctk.CTkFrame(self.scroll_alert, fg_color="transparent")
                    frame_p.pack(fill="x", pady=5)
                    
                    # Mensagem Descritiva
                    msg = f"⚠️ {p['nome']} está a acabar ({p['quantidade']} un.)!\nPrecisa adquirir mais."
                    
                    lbl_msg = ctk.CTkLabel(frame_p, text=msg, font=FONT_SMALL, text_color=COLOR_DANGER, anchor="w", justify="left")
                    lbl_msg.pack(fill="x")
            else:
                ctk.CTkLabel(self.scroll_alert, text="Nenhum alerta de stock.", text_color=COLOR_SUCCESS).pack()
                
        except Exception as e:
            print(f"Erro ao atualizar alertas: {e}")
