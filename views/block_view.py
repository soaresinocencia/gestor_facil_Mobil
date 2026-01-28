import flet as ft

class BlockView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/blocked")
        self.page = page
        self.bgcolor = "#D32F2F" # Vermelho alerta
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.padding = 20
        
        self.controls = [
            ft.Icon(ft.icons.LOCK_CLOCK, size=80, color="white"),
            ft.Text("Acesso Bloqueado", size=30, weight=ft.FontWeight.BOLD, color="white"),
            ft.Text("Sua licença expirou.", size=18, color="white"),
            
            ft.Container(height=20),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("Pague para continuar usando:", color="black", weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Row([
                        ft.Icon(ft.icons.PHONE_ANDROID, color="red"),
                        ft.Text("M-Pesa: 84 123 4567", size=16, color="black"),
                    ]),
                    ft.Row([
                        ft.Icon(ft.icons.attach_money, color="orange"), # Usando attach_money pois phone_iphone pode nao existir em versoes antigas
                        ft.Text("e-Mola: 87 123 4567", size=16, color="black"),
                    ]),
                    ft.Text("Referência: GESTOR-01", size=14, color="grey"),
                ]),
                bgcolor="white",
                padding=20,
                border_radius=10,
                width=300
            ),
            
            ft.Container(height=20),
            
            ft.ElevatedButton(
                "Já paguei (Verificar Novamente)",
                icon="refresh",
                color="red",
                bgcolor="white",
                on_click=self.verificar_pagamento
            )
        ]

    def verificar_pagamento(self, e):
        self.page.snack_bar = ft.SnackBar(ft.Text("Verificando conexão..."))
        self.page.snack_bar.open = True
        self.page.update()
        
        try:
            from sync_service import SyncService
            import database
            
            # Precisamos do ID do cliente. Vamos pegar do usuario 'admin' local.
            # Em app real, o cliente estaria logado ou salvo em config.
            # Hardcoded simulation
            cliente_id = '258849343350' 
            
            service = SyncService()
            status = service.verificar_licenca(cliente_id)
            
            if status['status'] == 'ativo':
                self.page.go("/login")
            else:
                 self.page.snack_bar = ft.SnackBar(ft.Text(f"Ainda bloqueado: {status['status']}"))
                 self.page.snack_bar.open = True
                 self.page.update()
                 
        except Exception as ex:
             self.page.snack_bar = ft.SnackBar(ft.Text(f"Erro: {ex}"))
             self.page.snack_bar.open = True
             self.page.update()
