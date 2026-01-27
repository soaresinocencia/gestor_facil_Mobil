import shutil
import os
from datetime import datetime
import textwrap
import qrcode
from PIL import Image

import sys

import tempfile

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS (OneFile)
        base_path = sys._MEIPASS
    except Exception:
        # Em OneDir ou Dev, usar o diretório do executável/script
        if getattr(sys, 'frozen', False):
             base_path = os.path.dirname(sys.executable)
        else:
             base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_writable_path(filename):
    """Retorna um caminho seguro para CRIAR arquivos (temp)"""
    temp_dir = tempfile.gettempdir()
    return os.path.join(temp_dir, filename)

def get_documents_path(filename):
    """Retorna caminho na pasta Documentos do usuário (para relatórios)"""
    docs = os.path.join(os.path.expanduser("~"), "Documents", "GestorFacil")
    if not os.path.exists(docs):
        os.makedirs(docs)
    return os.path.join(docs, filename)

# Configurar caminhos seguros em Documentos
DOCS_ROOT = os.path.join(os.path.expanduser("~"), "Documents", "GestorFacil")
BACKUP_DIR = os.path.join(DOCS_ROOT, "Backups")
DOCS_DIR = DOCS_ROOT # Manual vai na raiz de GestorFacil nos documentos
ASSETS_DIR = resource_path("assets")

import src.database as database # Importar para pegar DB_NAME

def realizar_backup():
    """Cria uma cópia de segurança da base de dados."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"gestor_backup_{timestamp}.db")
    
    try:
        # DB_NAME já é absoluto e trata o frozen corretamente (feito no passo anterior)
        db_origem = database.DB_NAME
        
        if os.path.exists(db_origem):
            shutil.copy2(db_origem, backup_file)
            print(f"Backup realizado com sucesso: {backup_file}")
            return backup_file

        if os.path.exists(db_origem):
            shutil.copy2(db_origem, backup_file)
            print(f"Backup realizado com sucesso: {backup_file}")
            return backup_file # Retornar caminho para confirmar sucesso na UI
            
            # Manter apenas os últimos 30 backups
            # ... (logica de limpeza mantida se quiser)
        else:
            print(f"Base de dados não encontrada em: {db_origem}")
            return None
    except Exception as e:
        print(f"Erro ao realizar backup: {e}")
        return None

def gerar_qr_suporte(numero_whatsapp):
    """Gera um QR Code para o WhatsApp de suporte."""
    # Salvar em temp para evitar erro de permissão na pasta de instalação
    path = get_writable_path("qr_suporte.png")
    
    link = f"https://wa.me/{numero_whatsapp}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H, 
        box_size=12, 
        border=4,
    )
    qr.add_data(link)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(path)
    return path

def gerar_manual_tecnico():
    """Gera o arquivo Manual_Tecnico.txt para suporte."""
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
    
    arquivo_manual = os.path.join(DOCS_DIR, "Manual_Tecnico.txt")
    
    manual_content = """
    ============================================================
                        GESTOR FÁCIL - MANUAL TÉCNICO
    ============================================================
    
    1. ARQUIVOS E PASTAS
    Seus relatórios, backups e este manual estão salvos na pasta:
    Documentos -> GestorFacil
    
    2. BACKUP
    O sistema realiza backups automáticos para a pasta 'Backups'
    dentro de Documents/GestorFacil.
    
    3. SUPORTE TÉCNICO
    Em caso de falhas, contacte o desenvolvedor:
    Soares Inocencia Massaete (+258 84 934 3350)
    
    4. FUNCIONALIDADES
    - Diferenciação de Stock (Nome + Detalhes)
    - Ponto de Venda com atualização rápida
    - Gestão de Vendedores (Email/WhatsApp)
    
    ============================================================
    """
    
    try:
        with open(arquivo_manual, "w", encoding="utf-8") as f:
            f.write(textwrap.dedent(manual_content))
        print(f"Manual Técnico atualizado em: {arquivo_manual}")
        return arquivo_manual
    except Exception as e:
        print(f"Erro ao gerar manual: {e}")
        return None

def formatar_moeda(valor):
    """Formata valor numérico para Metical (MT)."""
    return f"{valor:,.2f} MT"

import urllib.parse
import webbrowser

def notificar_whatsapp(numero, mensagem):
    """Abre o WhatsApp Web/App com a mensagem pré-preenchida."""
    if not numero: return
    
    # Limpar numero (manter apenas digitos)
    num_clean = "".join(filter(str.isdigit, str(numero)))
    
    msg_encoded = urllib.parse.quote(mensagem)
    link = f"https://wa.me/{num_clean}?text={msg_encoded}"
    
    try:
        webbrowser.open(link)
    except Exception as e:
        print(f"Erro ao abrir WhatsApp: {e}")

def notificar_email(email, assunto, corpo):
    """Abre o cliente de email padrão."""
    if not email: return
    
    assunto_enc = urllib.parse.quote(assunto)
    corpo_enc = urllib.parse.quote(corpo)
    
    link = f"mailto:{email}?subject={assunto_enc}&body={corpo_enc}"
    
    try:
        webbrowser.open(link)
    except Exception as e:
        print(f"Erro ao abrir Email: {e}")
