import time
import schedule
from sync_service import SyncService
from datetime import datetime

def job():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Verificando sincronização...")
    try:
        service = SyncService()
        if service.connected:
            # 1. Baixar produtos novos/atualizados da nuvem (criados no Mobile ou outro PC)
            # Para desktop, queremos baixar VENDAS do mobile também?
            # Sim, para o relatório consolidado.
            msg = service.sync_tudo(is_desktop=True)
            print(f"   Status: {msg}")
        else:
            print("   Sem conexão com internet.")
    except Exception as e:
        print(f"   Erro no job: {e}")

def main():
    print("=== Gestor Fácil: Agente de Sincronização (Desktop) ===")
    print("Este programa roda em segundo plano para conectar seu PC à Nuvem.")
    print("Pressione Ctrl+C para parar.")
    print("---------------------------------------------------------")
    
    # Rodar imediatamente ao abrir
    job()
    
    # Agendar para cada 5 minutos
    schedule.every(5).minutes.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Agente de sincronização parado pelo usuário. Até logo!")
