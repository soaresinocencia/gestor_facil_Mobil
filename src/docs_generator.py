from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import os
import shutil
from datetime import datetime
import textwrap

import src.utils as utils

# Garantir que achamos a pasta docs tanto em DEV quanto em EXE
DOCS_DIR = utils.resource_path("docs")
# Debug: Imprimir caminho
print(f"DOCS_DIR resolved to: {DOCS_DIR}")
# OUTPUTS continua fora do executável para persistencia
import sys
# Definir onde salvar outputs (perto do executável)
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
    OUTPUTS_DIR = os.path.join(APP_DIR, "outputs")
else:
    OUTPUTS_DIR = "outputs"

def gerar_kit_cliente(nome_cliente, nuit, email="", username="", password=""):
    """
    Gera uma pasta com o Contrato, Manual e Plano para o cliente.
    """
    # 1. Preparar Pasta
    data_hoje = datetime.now().strftime("%Y_%m_%d")
    nome_sanitizado = nome_cliente.replace(" ", "_")
    kit_dir = os.path.join(OUTPUTS_DIR, f"Kit_{nome_sanitizado}_{data_hoje}")
    
    if not os.path.exists(kit_dir):
        os.makedirs(kit_dir)
        
    # 2. Gerar Contrato PDF
    _gerar_contrato_pdf(kit_dir, nome_cliente, nuit, email, username, password)
    
    # 3. Copiar Outros Documentos
    docs_to_copy = ["Manual_Tecnico.txt", "plano_sustentabilidade.md"]
    for doc in docs_to_copy:
        src = os.path.join(DOCS_DIR, doc)
        dst = os.path.join(kit_dir, doc)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            
    return kit_dir

    return kit_dir

def _gerar_contrato_pdf(output_dir, nome_cliente, nuit, email="", username="", password=""):
    """Lê o template Markdown e gera um PDF simples."""
    template_path = os.path.join(DOCS_DIR, "contrato_subscricao.md")
    output_path = os.path.join(output_dir, f"Contrato_{nome_cliente.replace(' ', '_')}.pdf")
    
    if not os.path.exists(template_path):
        print("Template de contrato não encontrado.")
        from tkinter import messagebox
        messagebox.showerror("Erro de Arquivo", f"Template de contrato não encontrado em:\n{template_path}")
        return

    # Ler conteúdo e substituir placeholders
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.readlines()
    except Exception:
        content = ["# Contrato de Subscrição\n", "Erro ao carregar template."]
        
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    y = height - 25*mm
    x = 25*mm
    
    # Adicionar Logotipo
    # Adicionar Logotipo
    try:
        from src.utils import ASSETS_DIR # Importar diretório de assets
        # O arquivo correto é logotipo.png (verificado no diretorio)
        logo_path = os.path.join(ASSETS_DIR, "logotipo.png")
        if os.path.exists(logo_path):
            # Desenhar logo centralizado
            # Imagem de 3cm width (30mm)
            # A4 Width = width (210mm)
            logo_width = 30*mm
            logo_height = 30*mm
            x_centered = (width - logo_width) / 2
            
            c.drawImage(logo_path, x_centered, height - 35*mm, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
            y -= 40*mm # Descer cursor
        else:
            print(f"Logo não encontrado em: {logo_path}")
    except Exception as e:
        print(f"Erro ao adicionar logo: {e}")

    # Configuração Fonte
    c.setFont("Helvetica", 11)
    
    for line in content:
        # Substituições
        line = line.replace("[Nome da Empresa/Comerciante]", nome_cliente)
        line = line.replace("[Número]", nuit)
        
        # Limpar Markdown Básico (Simples)
        line = line.replace("**", "").replace("\\", "")
        
        # Títulos
        if line.strip().startswith("#") or "Contrato de Subscrição" in line:
             c.setFont("Helvetica-Bold", 14)
             y -= 5*mm
        elif line.strip() and line[0].isdigit(): # Numeros de clausulas
             c.setFont("Helvetica-Bold", 11)
             y -= 2*mm
        else:
             c.setFont("Helvetica", 11)
        
        # Quebra de linhas longas
        wrapped_lines = textwrap.wrap(line.strip(), width=80) 
        
        for w_line in wrapped_lines:
            if y < 25*mm: # Nova Página
                c.showPage()
                y = height - 25*mm
                c.setFont("Helvetica", 11)
            
            c.drawString(x, y, w_line)
            y -= 5*mm
            
        y -= 2*mm # Espaço extra entre parágrafos
        
    # Rodapé com Assinaturas
    y -= 10*mm
    if y < 60*mm: # Mais espaco para credenciais
        c.showPage()
        y = height - 40*mm
    
    c.line(x, y, x + 70*mm, y)
    c.drawString(x, y - 5*mm, "Assinatura do Cliente")
    
    c.line(x + 90*mm, y, x + 160*mm, y)
    c.drawString(x + 90*mm, y - 5*mm, "Assinatura do Gestor")
    
    # Credenciais
    # Credenciais - Garantir visibilidade
    # Se tiver pouco espaço (< 60mm), criar nova página
    if y < 60*mm:
        c.showPage()
        y = height - 40*mm
        # Re-setar fonte se nova pagina
        c.setFont("Helvetica-Bold", 12)

    y -= 20*mm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, "DADOS DE ACESSO AO SISTEMA")
    
    y -= 10*mm
    c.setFont("Helvetica", 12)
    c.drawString(x, y, "O Usuário abaixo tem permissão de acesso conforme níveis contratados.")
    
    y -= 10*mm
    c.setFillColorRGB(0.9, 0.9, 0.9) # Fundo cinza claro
    c.rect(x-2*mm, y-25*mm, 170*mm, 30*mm, fill=1, stroke=0)
    c.setFillColorRGB(0, 0, 0) # Texto preto
    
    c.setFont("Courier-Bold", 14)
    # Ajuste de posição dentro do retângulo
    c.drawString(x + 5*mm, y - 8*mm, f"USUÁRIO:  {username if username else email}")
    c.drawString(x + 5*mm, y - 18*mm, f"SENHA:    {password if password else 'Defina no primeiro acesso'}")

    y -= 35*mm
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(x, y, "* O sistema solicitará a troca desta senha após 45 dias para sua segurança.")
    c.drawString(x, y-5*mm, "* Estas credenciais são pessoais e intransferíveis.")
    
    c.save()

