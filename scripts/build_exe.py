
import PyInstaller.__main__
import os
import shutil

# Limpeza completa da pasta dist
# Limpeza corrigida para evitar erros no script Python também
dist_path = 'dist'
if os.path.exists(dist_path):
    print("!!! LIMPEZA DA PASTA DIST !!!")
    try:
        shutil.rmtree(dist_path)
    except Exception as e:
        print(f"Aviso: Limpeza via Python falhou ({e}). O PowerShell deve ter resolvido.")

print("Iniciando build do Gestor Facil...")

import customtkinter

ctk_path = os.path.dirname(customtkinter.__file__)

print(f"Incluindo CustomTkinter de: {ctk_path}")

PyInstaller.__main__.run([
    'main.py',
    '--name=GestorFacil_Release',
    '--noconfirm',
    '--onedir', 
    '--windowed',
    '--add-data=assets;assets',
    #'--add-data=src;src', # REMOVIDO
    '--add-data=docs;docs', 
    f'--add-data={ctk_path};customtkinter',
    '--hidden-import=babel.numbers',
    '--hidden-import=win32timezone',
    '--hidden-import=qrcode',
    '--hidden-import=PIL',
    '--clean',
])

# Copiar a pasta 'db' usando comando do sistema
# IMPORTANTE: Forcar copia do db do projeto para garantir que as funcoes novas existam no SQLite se necessario (mas aqui eh codigo python)
# O codigo python ja foi atualizado no passo anterior. O DB (arquivo .db) se tiver tabela users, ok.
src_db = 'db'
dst_db = os.path.join('dist', 'GestorFacil_Release', 'db')

print(f"Copiando banco de dados para: {dst_db}")
try:
    if not os.path.exists(dst_db):
        shutil.copytree(src_db, dst_db)
    else:
        # Se ja existe, tentar atualizar arquivos
        import glob
        for file in glob.glob(os.path.join(src_db, "*")):
            shutil.copy2(file, dst_db)
            
except Exception as e:
    print(f"Aviso: Cópia via Python falhou ({e}). Tentando XCOPY...")
    os.system(f'xcopy "{src_db}" "{dst_db}" /E /I /Y')

print("Build concluído! Pasta: dist/GestorFacil_Release")
