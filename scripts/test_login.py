import sys
import os

# Adicionar root ao path para imports funcionarem
sys.path.append(os.getcwd())

import src.database as database

def test_login():
    print("Testando login com admin/admin...")
    try:
        user = database.verificar_login('admin', 'admin')
        if user:
            print("SUCESSO: Usuario encontrado!")
            print(dict(user))
        else:
            print("FALHA: Usuario nao encontrado ou senha incorreta.")
            
        # Testar falha
        print("\nTestando login invalido...")
        bad_user = database.verificar_login('admin', 'errada')
        if not bad_user:
            print("SUCESSO: Login invalido bloqueado corretamente.")
        else:
            print("FALHA: Login invalido permitiu acesso!")
            
    except Exception as e:
        print(f"ERRO DE EXECUCAO: {e}")

if __name__ == "__main__":
    test_login()
