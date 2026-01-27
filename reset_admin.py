
import sqlite3
import os

DB_FILE = "db/gestor_facil.db"

def reset_admin():
    print(f"Connecting to {DB_FILE}...")
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        if not cursor.fetchone():
            print("Table 'usuarios' does not exist! Database might be empty.")
            return

        # Try to insert or update
        print("Resetting admin user...")
        try:
            cursor.execute("INSERT INTO usuarios (usuario, senha, cargo, nome_completo, whatsapp) VALUES (?, ?, ?, ?, ?)", 
                          ('admin', 'admin', 'super_admin', 'Soares Inocencia Massaete', '258849343350'))
            print("Admin user created.")
        except sqlite3.IntegrityError:
            cursor.execute("UPDATE usuarios SET senha = 'admin', cargo = 'super_admin' WHERE usuario = 'admin'")
            print("Admin user updated.")
            
        conn.commit()
        
        # Verify
        cursor.execute("SELECT usuario, senha, cargo FROM usuarios WHERE usuario = 'admin'")
        user = cursor.fetchone()
        print(f"Verified User: {user}")
        
        conn.close()
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if not os.path.exists("db"):
        os.makedirs("db")
    reset_admin()
