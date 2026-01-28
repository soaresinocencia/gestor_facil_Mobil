from sync_service import SyncService
import database

def main():
    print("Iniciando Seed de Licença (SaaS)...")
    sync = SyncService()
    
    if not sync.connected:
        print("Erro: Não foi possível conectar ao Supabase.")
        return

    # Pegar telefone do admin
    # Hardcoded do database.py: '258849343350'
    cliente_id = '258849343350'
    
    data = {
        "cliente_id": cliente_id,
        "data_validade": "2026-12-31", # Validade longa para teste
        "status": "ativo",
        "plano": "pro",
        "ultimo_pagamento": "2026-01-28"
    }
    
    try:
        # Check se existe
        res = sync.supabase.table("licencas").select("*").eq("cliente_id", cliente_id).execute()
        if res.data:
            print(f"Licença já existe para {cliente_id}. Atualizando...")
            sync.supabase.table("licencas").update(data).eq("cliente_id", cliente_id).execute()
        else:
            print(f"Criando nova licença para {cliente_id}...")
            sync.supabase.table("licencas").insert(data).execute()
            
        print("Sucesso! Licença criada/atualizada.")
        
    except Exception as e:
        print(f"Erro ao criar licença: {e}")

if __name__ == "__main__":
    main()
