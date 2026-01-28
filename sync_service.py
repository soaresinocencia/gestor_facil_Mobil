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

    def download_vendas(self):
        """Baixa vendas da nuvem que não existem localmente (Importante para o PC ver vendas do Mobile)."""
        if not self.connected: return 0
        
        try:
            # Pegar últimas 50 vendas da nuvem
            res = self.supabase.table("vendas").select("*").order("created_at", desc=True).limit(50).execute()
            vendas_remotas = res.data
            count = 0
            
            for vr in vendas_remotas:
                # Verifica se já temos essa venda pelo UUID ou ID Remoto?
                # O ID local deles não bate com o nosso.
                # O ideal seria ter um UUID. Como não temos, vamos usar uma heurística ou criar tabela de mapeamento.
                # Simplificação V1: Se a data_hora + total + vendedor for igual, é a mesma venda.
                
                existe = database.verificar_se_venda_existe(vr['data_hora'], vr['total_venda'], vr['vendedor_nome'])
                
                if not existe:
                    # Inserir localmente
                    database.registar_venda_importada(vr)
                    count += 1
            
            if count > 0:
                print(f"Sync DOWN: {count} vendas importadas da nuvem.")
            return count
        except Exception as e:
            print(f"Erro ao baixar vendas: {e}")
            return 0

    def sync_tudo(self, is_desktop=False):
        """Executa ciclo completo de sincronização."""
        if not self.connected: return "Offline"
        
        print("--- Iniciando Sincronização ---")
        
        # 1. Enviar minhas vendas locais
        vendas_up = self.upload_vendas_pendentes()
        
        # 2. Baixar produtos atualizados (Preços novos, Stock atualizado por outros)
        prods_down = self.download_produtos()
        
        # 3. Se for Desktop, eu quero ver as vendas que fizeram no celular
        vendas_down = 0
        if is_desktop:
            vendas_down = self.download_vendas()
            # E no desktop, também deveriamos subir atualizacoes de produtos (precos).
            # Por enquanto, assumimos que o Seed Inicial fez isso, ou criar funcao especifica.
        
        print("--- Sincronização Finalizada ---")
        
        return f"UP: {vendas_up} vendas | DOWN: {prods_down} prods, {vendas_down} vendas"

    def verificar_licenca(self, cliente_id):
        """Verifica se a licença do cliente está ativa e válida."""
        if not self.connected:
            # Se offline, permite acesso (famoso 'grace period' ou cache local necessária)
            # Por segurança MVP: Se offline, deixa entrar.
            print("Offline: Permitindo acesso temporário.")
            return {"status": "ativo", "validade": "2099-12-31", "offline": True}
        
        try:
            # Buscar licença pelo ID (ex: numero de telefone ou email)
            res = self.supabase.table("licencas").select("*").eq("cliente_id", cliente_id).execute()
            
            if not res.data:
                # Não tem licença cadastrada.
                # Opção A: Bloquear
                # Opção B: Dar Trial
                # Vamos retornar 'sem_licenca' para a UI decidir.
                return {"status": "sem_licenca", "validade": None}
            
            licenca = res.data[0]
            # Verificar data
            import datetime
            hoje = datetime.date.today()
            validade = datetime.datetime.strptime(licenca['data_validade'], "%Y-%m-%d").date()
            
            if hoje > validade:
                 return {"status": "expirado", "validade": licenca['data_validade']}
            
            if licenca['status'] != 'ativo':
                return {"status": "bloqueado", "validade": licenca['data_validade']}
                
            return {"status": "ativo", "validade": licenca['data_validade']}

        except Exception as e:
            print(f"Erro ao verificar licença: {e}")
            # Em caso de erro (ex: tabela nao existe), libera.
            return {"status": "erro_verificacao", "msg": str(e)}
