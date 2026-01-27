import database
import utils
import reports
import os
import time

print("Iniciando Verificação de Lógica...")

# 1. Inicializar Banco
print("[1] Inicializando Banco de Dados...")
database.inicializar_banco()
if os.path.exists("gestor.db"):
    print(" -> gestor.db ok")
else:
    print(" -> ERRO: gestor.db não criado")

# 2. Gerar Manual
print("\n[2] Gerando Manual Técnico...")
utils.gerar_manual_tecnico()
if os.path.exists("Manual_Tecnico.txt"):
    print(" -> Manual_Tecnico.txt ok")
else:
    print(" -> ERRO: Manual_Tecnico.txt não criado")

# 3. Adicionar Produto Teste
print("\n[3] Adicionando Produto de Teste...")
database.adicionar_produto("Produto Teste", 100, 150, 50, 5)
produtos = database.listar_produtos()
prod = next((p for p in produtos if p['nome'] == "Produto Teste"), None)
if prod:
    print(f" -> Produto criado: ID {prod['id']}")
else:
    print(" -> ERRO: Produto não encontrado")

# 4. Registar Venda
print("\n[4] Registando Venda...")
itens = [(prod['id'], 2, 150.0)] # 2 unidades a 150
venda_id = database.registar_venda(itens, 300.0, 100.0) # Total 300, Lucro 100
print(f" -> Venda ID: {venda_id}")

# 5. Gerar Recibo
print("\n[5] Gerando Recibo PDF...")
reports.gerar_recibo(venda_id)
pdf_name = f"recibo_venda_{venda_id}.pdf"
if os.path.exists(pdf_name):
    print(f" -> {pdf_name} ok")
else:
    print(" -> ERRO: PDF não criado")

# 6. Verificar Baixa de Stock
print("\n[6] Verificando Baixa de Stock...")
produtos_pos = database.listar_produtos()
prod_pos = next((p for p in produtos_pos if p['id'] == prod['id']), None)
if prod_pos['quantidade'] == 48:
    print(f" -> Stock atualizado corretamente: 48")
else:
    print(f" -> ERRO: Stock incorreto: {prod_pos['quantidade']}")

# 7. Backup
print("\n[7] Testando Backup...")
utils.realizar_backup()
backups = os.listdir("backups")
if len(backups) > 0:
    print(f" -> Backup encontrado: {backups[0]}")
else:
    print(" -> ERRO: Pasta backups vazia")

print("\nVerificação Concluída.")
