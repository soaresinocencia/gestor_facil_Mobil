import flet as ft
from src import database

class ProductsView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/products")
        self.page = page
        self.padding = 0
        self.primary_color = "#2196F3"
        
        # Header
        header = ft.Container(
            content=ft.Row([
                ft.IconButton("arrow_back", icon_color="white", on_click=lambda e: self.page.go("/dashboard")),
                ft.Text("Produtos", color="white", size=18, weight=ft.FontWeight.BOLD),
                ft.IconButton("tune", icon_color="white"),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=20,
            bgcolor=self.primary_color,
            height=80,
        )
        
        # Lista de Produtos
        self.products_list = ft.Column(scroll=ft.ScrollMode.AUTO)
        self.load_products()
        
        # Search Bar
        search_bar = ft.Container(
            content=ft.TextField(
                label="Buscar Produto...",
                on_change=self.filter_products,
                prefix_icon="search",
                border_radius=20,
                bgcolor="white"
            ),
            padding=ft.padding.only(left=20, right=20, top=10, bottom=10)
        )

        self.controls = [
            ft.Container(
                content=ft.Column([
                    header,
                    search_bar,
                    ft.Container(
                        content=self.products_list,
                        expand=True,
                        padding=10
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

    def load_products(self, filter_text=""):
        self.products_list.controls.clear()
        
        # Buscar do banco
        all_products = database.listar_produtos()
        
        for prod in all_products:
            # prod é Row/Dict: {'nome':..., 'preco_venda':..., 'quantidade':...}
            p_nome = prod['nome']
            
            # Filtro
            if filter_text.lower() not in p_nome.lower():
                continue
                
            p_preco = f"{prod['preco_venda']:,.2f} MT"
            p_qtd = prod['quantidade']
            
            # Cor do stock
            stock_color = "green" if p_qtd > 10 else "red"
            
            # Item da Lista
            item = ft.Container(
                content=ft.Row([
                    ft.Icon("shopping_bag", color=self.primary_color),
                    ft.Column([
                        ft.Text(p_nome, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Stock: {p_qtd}", color=stock_color, size=12)
                    ], expand=True),
                    ft.Text(p_preco, weight=ft.FontWeight.BOLD, size=16)
                ]),
                padding=10,
                bgcolor="white",
                border_radius=10,
                shadow=ft.BoxShadow(blur_radius=2, color="black12"),
                margin=ft.margin.only(bottom=5)
            )
            self.products_list.controls.append(item)
            
        self.page.update()

    def filter_products(self, e):
        self.load_products(e.control.value)
