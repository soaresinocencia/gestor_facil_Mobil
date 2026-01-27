import flet as ft

def main(page: ft.Page):
    page.title = "Gestor Fácil Mobile"
    # Mobile dimensions for preview on PC
    page.window_width = 375
    page.window_height = 812
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    # Cores do Gestor Fácil (Exemplo)
    primary_color = "#2196F3"
    secondary_color = "#E3F2FD"

    def login_click(e):
        page.snack_bar = ft.SnackBar(ft.Text("Login Simulado com Sucesso!"))
        page.snack_bar.open = True
        page.update()
        page.clean()
        show_dashboard()

    def show_dashboard():
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon("menu", color="white"),
                            ft.Text("Gestor Fácil Dashboard", color="white", size=18, weight=ft.FontWeight.BOLD),
                            ft.Icon("notifications", color="white"),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=20,
                        bgcolor=primary_color,
                        height=80,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Resumo do Dia", size=20, weight=ft.FontWeight.BOLD),
                            ft.Row([
                                card_info("Vendas", "15,400 MT", "attach_money", "green"),
                                card_info("Lucro", "4,200 MT", "trending_up", "blue"),
                            ]),
                             ft.Row([
                                card_info("Clientes", "12", "people", "orange"),
                                card_info("Stock Baixo", "3 Items", "warning", "red"),
                            ]),
                        ]),
                        padding=20
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Ações Rápidas", size=16, weight=ft.FontWeight.BOLD),
                            action_button("Nova Venda", "add_shopping_cart"),
                            action_button("Consultar Stock", "inventory"),
                            action_button("Relatórios", "bar_chart"),
                        ]),
                        padding=20,
                        expand=True
                    )
                ]),
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=["white", secondary_color],
                ),
                expand=True
            )
        )
        page.update()

    def card_info(title, value, icon, icon_color):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=icon_color, size=30),
                ft.Text(value, size=18, weight=ft.FontWeight.BOLD),
                ft.Text(title, size=12, color="grey"),
            ], alignment=ft.MainAxisAlignment.CENTER),
            width=150,
            height=100,
            bgcolor="white",
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=5, color="black12"),
            padding=10
        )

    def action_button(text, icon):
        return ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(icon),
                ft.Text(text)
            ]),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=15,
                bgcolor=primary_color,
                color="white",
            ),
            width=300,
            on_click=lambda e: print(f"Clicked {text}")
        )

    # Tela de Login
    login_screen = ft.Container(
        content=ft.Column([
            ft.Icon("storefront", size=80, color=primary_color),
            ft.Text("Gestor Fácil", size=30, weight=ft.FontWeight.BOLD, color=primary_color),
            ft.Text("Gestão na palma da mão", size=16, color="grey"),
            ft.Divider(height=40, color="transparent"),
            ft.TextField(label="Usuário", prefix_icon="person", border_radius=20),
            ft.TextField(label="Senha", password=True, can_reveal_password=True, prefix_icon="lock", border_radius=20),
            ft.Divider(height=20, color="transparent"),
            ft.ElevatedButton(
                "Entrar", 
                on_click=login_click,
                width=300,
                height=50,
                style=ft.ButtonStyle(
                    bgcolor=primary_color,
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
            colors=["white", secondary_color],
        )
    )

    page.add(login_screen)

ft.app(target=main)
