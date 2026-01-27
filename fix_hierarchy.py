
import src.database as db
import sqlite3

def fix_hierarchy():
    conn = db.conectar()
    c = conn.cursor()
    
    print("Fixing Hierarchy...")
    
    # 1. Smassaete (Super Admin) - Criador Supremo (None)
    # Ensure smassaete exists or use whatever ID is there.
    
    # 2. Admin (Cliente) -> Criado por Smassaete (simulado)
    c.execute("UPDATE usuarios SET created_by = 'smassaete' WHERE usuario = 'admin'")
    
    # 3. Vendedores -> Criado por Admin
    c.execute("UPDATE usuarios SET created_by = 'admin' WHERE cargo = 'vendedor'")
    
    conn.commit()
    conn.close()
    print("Hierarchy updated. 'admin' is child of 'smassaete'. Vendors are children of 'admin'.")

if __name__ == "__main__":
    fix_hierarchy()
