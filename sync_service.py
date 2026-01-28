import os
from supabase import create_client, Client
import database
import json

# Configurações do Supabase (Hardcoded para facilitar protótipo, ideal mover para .env)
SUPABASE_URL = "https://depwcrvavhrrecvgkouy.supabase.co"
SUPABASE_KEY = "sb_publishable_4ZKRweyzxtDV-FEWqFTlTA_kAQqyBJG" # Anon key

class SyncService:
    def __init__(self):
        try:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            self.connected = True
            print("Conectado ao Supabase com sucesso!")
        except Exception as e:
            self.connected = False
            print(f"Erro ao conectar Supabase: {e}")

    def upload_produtos_iniciais(self):
        """Envia todos os produtos locais para a nuvem (Seed inicial)."""
        if not self.connected: return
        
        produtos = database.listar_produtos()
        # produtos é lista de Row/dict
        
        count = 0
        for p in produtos:
            # Preparar payload
            data = {
                "nome": p['nome'],
                "preco_custo": p['preco_custo'],
                "preco_venda": p['preco_venda'],
                "quantidade": p['quantidade'],
                "minimo_alerta": p['minimo_alerta'],
                "detalhes": p['detalhes'],
                "categoria": p['categoria']
            }
            
            # Upsert (Inserir ou Atualizar se existir?)
            # Como não temos ID remoto ainda, vamos tentar inserir.
            # Se já existir nome igual, pode duplicar se não tratarmos.
            # Vamos verificar antes.
            
            try:
                # Check se existe
                res = self.supabase.table("produtos").select("*").eq("nome", p['nome']).execute()
                if not res.data:
                    self.supabase.table("produtos").insert(data).execute()
                    count += 1
            except Exception as e:
                print(f"Erro ao subir produto {p['nome']}: {e}")
                
        print(f"Upload concluído: {count} novos produtos enviados.")

    def upload_vendas_pendentes(self):
        """Sobe vendas locais pendentes para a nuvem."""
        if not self.connected: return
        
        vendas = database.get_vendas_nao_sincronizadas()
        count = 0
        
        for v in vendas:
            try:
                # Prepara Payload
                # Converter datetime string local para ISO ou enviar como string mesmo 
                # (Postgres aceita YYYY-MM-DD HH:MM:SS)
                
                payload = {
                    "local_id": v['id'],
                    "data_hora": v['data_hora'],
                    "total_venda": v['total_venda'],
                    "lucro_total": v['lucro_total'],
                    "cliente": v['cliente'],
                    "vendedor_nome": v.get('vendedor_nome'), # Pode ser None
                    "itens": v['itens'] # Lista de dicts (JSONB)
                }
                
                # Insert na Nuvem
                self.supabase.table("vendas").insert(payload).execute()
                
                # Marca como syncado localmente
                database.marcar_venda_como_sincronizada(v['id'])
                count += 1
                
            except Exception as e:
                print(f"Erro ao subir venda ID {v['id']}: {e}")
                
        if count > 0:
            print(f"Sync UP: {count} vendas enviadas.")
        return count

    def download_produtos(self):
        """Baixa produtos da nuvem e atualiza localmente."""
        if not self.connected: return
        
        try:
            # Pega todos produtos da nuvem
            # Se tiver muitos, precisaria de paginação. Por enquanto assumimos < 1000.
            res = self.supabase.table("produtos").select("*").execute()
            produtos_remotos = res.data
            
            count = 0
            for p in produtos_remotos:
                # Atualiza local
                database.upsert_produto_from_cloud(p)
                count += 1
                
            print(f"Sync DOWN: {count} produtos atualizados.")
            return count
        except Exception as e:
            print(f"Erro ao baixar produtos: {e}")
            return 0

    def sync_tudo(self):
        """Executa ciclo completo de sincronização."""
        if not self.connected: return "Offline"
        
        print("--- Iniciando Sincronização ---")
        vendas = self.upload_vendas_pendentes()
        prods = self.download_produtos()
        print("--- Sincronização Finalizada ---")
        
        return f"Enviados: {vendas or 0} vendas | Baixados: {prods or 0} produtos"
