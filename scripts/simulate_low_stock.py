
import sys
import os

# Adicionar root path
sys.path.append(os.getcwd())

import src.database as db

def simular_stock_baixo():
    print("Simulando stock baixo...")
    conn = db.conectar()
    cursor = conn.cursor()
    
    # Atualizar "Arroz 1kg" (id 1) para 5 unidades (minimo 10)
    cursor.execute("UPDATE produtos SET quantidade = 5 WHERE nome LIKE 'Arroz%'")
    
    # Atualizar "Oleo 1L" (id 2) para 2 unidades (minimo 5)
    cursor.execute("UPDATE produtos SET quantidade = 2 WHERE nome LIKE 'Óleo%'")
    
    conn.commit()
    conn.close()
    print("Stock atualizado! Arroz e Óleo devem aparecer no alerta.")

if __name__ == "__main__":
    simular_stock_baixo()
