import flet as ft
from src import database

class DashboardView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/dashboard")
        self.page = page
        self.padding = 0
        self.primary_color = "#2196F3"
        
        # Carregar dados
        faturamento, lucro, num_vendas = database.get_resumo_hoje()
        baixo_stock = len(database.get_produtos_baixo_stock())
        
        # Formatar
        fat_str = f"{faturamento:,.2f} MT"
        lucro_str = f"{lucro:,.2f} MT"
        
        self.controls = [
            ft.Container(
                content=ft.Column([
                    # Header
                    ft.Container(
                        content=ft.Row([
                            ft.IconButton("menu", icon_color="white", on_click=lambda e: print("Menu")),
                            ft.Text("Dashboard", color="white", size=18, weight=ft.FontWeight.BOLD),
                            ft.IconButton("logout", icon_color="white", on_click=self.logout),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=20,
                        bgcolor=self.primary_color,
                        height=80,
                    ),
                    
                    # Conteúdo Scrollável
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Resumo do Dia", size=20, weight=ft.FontWeight.BOLD),
                            ft.Row([
                                self.card_info("Vendas", fat_str, "attach_money", "green"),
                                self.card_info("Lucro", lucro_str, "trending_up", "blue"),
                            ]),
                            ft.Row([
                                self.card_info("Nº Vendas", str(num_vendas), "shopping_cart", "orange"),
                                self.card_info("Stock Baixo", f"{baixo_stock} Items", "warning", "red"),
                            ]),
                            ft.Divider(height=20),
                            ft.Text("Ações Rápidas", size=16, weight=ft.FontWeight.BOLD),
                            self.action_button("Nova Venda", "add_shopping_cart", lambda e: self.page.go("/pos")),
                            self.action_button("Produtos", "inventory", lambda e: self.page.go("/products")),
                        ], scroll=ft.ScrollMode.AUTO),
                        padding=20,
                        expand=True
                    )
                ]),
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=["white", "#E3F2FD"],
                )
            )
        ]

    def logout(self, e):
        self.page.go("/login")

    def card_info(self, title, value, icon, icon_color):
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

    def action_button(self, text, icon, on_click=None):
        return ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(icon),
                ft.Text(text)
            ]),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=15,
                bgcolor=self.primary_color,
                color="white",
            ),
            width=300,
            on_click=on_click if on_click else lambda e: print(f"Clicked {text}")
        )
