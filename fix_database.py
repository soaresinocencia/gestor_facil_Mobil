
import sqlite3
import os

DB_FILE = "db/gestor_facil.db"

def fix_and_reset():
    print(f"Opening database: {DB_FILE}")
    if not os.path.exists(DB_FILE):
        print("Database file not found!")
        return

    try:
        conn = sqlite3.connect(DB_FILE, timeout=10)
        cursor = conn.cursor()
        
        # 1. Apply Migrations Manually
        print("Checking schema...")
        
        # Usuarios table columns
        cols_to_add = [
            ("usuarios", "email", "TEXT"),
            ("usuarios", "whatsapp", "TEXT"),
            ("usuarios", "nome_completo", "TEXT"),
            ("vendas", "cliente", "TEXT"),
            ("produtos", "detalhes", "TEXT"),
            ("produtos", "categoria", "TEXT DEFAULT 'Geral'")
        ]
        
        for table, col, type_def in cols_to_add:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {type_def}")
                print(f"Added column {col} to {table}")
            except sqlite3.OperationalError as e:
                if "duplicate column" in str(e).lower() or "exists" in str(e).lower():
                    print(f"Column {col} already exists in {table}")
                else:
                    print(f"Could not add {col} to {table}: {e}")

        conn.commit()

        # 2. Reset Admin
        print("Resetting admin credentials...")
        
        # Check if admin exists
        cursor.execute("SELECT id FROM usuarios WHERE usuario = 'admin'")
        exists = cursor.fetchone()
        
        if exists:
            # Update
            cursor.execute("""
                UPDATE usuarios 
                SET senha = 'admin', 
                    cargo = 'super_admin', 
                    nome_completo = 'Soares Inocencia Massaete',
                    whatsapp = '258849343350'
                WHERE usuario = 'admin'
            """)
            print("Admin updated.")
        else:
            # Insert
            cursor.execute("""
                INSERT INTO usuarios (usuario, senha, cargo, nome_completo, whatsapp) 
                VALUES (?, ?, ?, ?, ?)
            """, ('admin', 'admin', 'super_admin', 'Soares Inocencia Massaete', '258849343350'))
            print("Admin inserted.")
            
        conn.commit()
        conn.close()
        print("\nSUCCESS: Database repaired and admin reset.")
        print("Login: admin / admin")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")

if __name__ == "__main__":
    fix_and_reset()
