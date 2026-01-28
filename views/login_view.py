import flet as ft
import database as database

class LoginView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/login")
        self.page = page
        self.padding = 0
        
        # Cores
        self.primary_color = "#2196F3"
        
        # Campos
        self.user_field = ft.TextField(
            label="Usuário", 
            prefix_icon="person", 
            border_radius=20,
            width=300
        )
        self.pass_field = ft.TextField(
            label="Senha", 
            password=True, 
            can_reveal_password=True, 
            prefix_icon="lock", 
            border_radius=20,
            width=300
        )
        
        # Conteúdo
        self.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Icon("storefront", size=80, color=self.primary_color),
                    ft.Text("Gestor Fácil", size=30, weight=ft.FontWeight.BOLD, color=self.primary_color),
                    ft.Text("Gestão na palma da mão", size=16, color="grey"),
                    ft.Divider(height=40, color="transparent"),
                    self.user_field,
                    self.pass_field,
                    ft.Divider(height=20, color="transparent"),
                    ft.ElevatedButton(
                        "Entrar", 
                        on_click=self.login_click,
                        width=300,
                        height=50,
                        style=ft.ButtonStyle(
                            bgcolor=self.primary_color,
                            color="white",
                            shape=ft.RoundedRectangleBorder(radius=20)
                        )
                    ),
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER
                ),
                padding=30,
                alignment=ft.alignment.center,
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=["white", "#E3F2FD"],
                )
            )
        ]

    def login_click(self, e):
        user = self.user_field.value
        password = self.pass_field.value
        
        if not user or not password:
            self.page.snack_bar = ft.SnackBar(ft.Text("Preencha todos os campos!"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()
            return

        # Verificar credenciais usando database.verificar_login
        # Retorna: user (Row/Dict), "BLOCKED", "EXPIRED", ou None
        result = database.verificar_login(user, password)
        
        if result == "BLOCKED":
            self.page.snack_bar = ft.SnackBar(ft.Text("Conta bloqueada! Contacte o suporte."), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()
        elif result == "EXPIRED":
             self.page.snack_bar = ft.SnackBar(ft.Text("Senha expirada. Altere no PC."), bgcolor="orange")
             self.page.snack_bar.open = True
             self.page.update()
        elif result:
            # Login Sucesso
            user_data = dict(result)
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Bem-vindo, {user}!"), bgcolor="green")
            self.page.snack_bar.open = True
            
            # Salvar dados
            self.page.client_storage.set("user_id", user_data['id'])
            self.page.client_storage.set("user_role", user_data['cargo'])
            self.page.go("/dashboard")
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("Usuário ou senha inválidos"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()
