import sqlite3
import os

DB_NAME = os.path.join("db", "gestor_facil.db")

def inspect():
    if not os.path.exists(DB_NAME):
        print(f"ERRO: Banco de dados '{DB_NAME}' não encontrado.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Listar Tabelas
    print("--- TABELAS ---")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for t in tables:
        print(t[0])

    # 2. Verificar Tabela usuarios
    print("\n--- SCHEMA USUARIOS ---")
    try:
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = cursor.fetchall()
        for c in columns:
            print(c)
    except Exception as e:
        print(f"Erro ao ler schema: {e}")

    # 3. Listar Usuários
    print("\n--- USUARIOS CADASTRADOS ---")
    try:
        cursor.execute("SELECT * FROM usuarios")
        users = cursor.fetchall()
        for u in users:
            print(u)
    except Exception as e:
        print(f"Erro ao listar usuários: {e}")

    conn.close()

if __name__ == "__main__":
    inspect()
