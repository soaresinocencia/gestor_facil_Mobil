from sync_service import SyncService

def main():
    print("Iniciando Seed Inicial (Upload de Produtos)...")
    sync = SyncService()
    sync.upload_produtos_iniciais()
    print("Processo finalizado.")

if __name__ == "__main__":
    main()
