import flet as ft
import database

class POSView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/pos")
        self.page = page
        self.padding = 0
        self.primary_color = "#2196F3"
        
        # Estado do Carrinho
        self.cart = {} # {produto_id: {'obj': prod_dict, 'qtd': int}}
        self.products = []
        
        # Header
        header = ft.Container(
            content=ft.Row([
                ft.IconButton("arrow_back", icon_color="white", on_click=lambda e: self.page.go("/dashboard")),
                ft.Text("Nova Venda", color="white", size=18, weight=ft.FontWeight.BOLD),
                ft.IconButton("shopping_cart", icon_color="white", on_click=self.show_cart_dialog),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=20,
            bgcolor=self.primary_color,
            height=80,
        )
        
        # Product Grid
        self.grid = ft.GridView(
            expand=True,
            runs_count=2,
            max_extent=200,
            child_aspect_ratio=0.8,
            spacing=10,
            run_spacing=10,
        )
        
        self.load_products()
        
        self.controls = [
            ft.Container(
                content=ft.Column([
                    header,
                    ft.Container(
                        content=self.grid,
                        expand=True,
                        padding=10
                    ),
                    self.total_footer()
                ]),
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=["white", "#E3F2FD"],
                )
            )
        ]

    def load_products(self):
        self.products = database.listar_produtos()
        for p in self.products:
            self.grid.controls.append(self.product_card(p))
            
    def product_card(self, product):
        return ft.Container(
            content=ft.Column([
                ft.Icon("shopping_bag", size=40, color=self.primary_color),
                ft.Text(product['nome'], weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Text(f"{product['preco_venda']:,.2f} MT", size=12),
                ft.ElevatedButton("Add", on_click=lambda e: self.add_to_cart(product))
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="white",
            border_radius=10,
            padding=10,
            shadow=ft.BoxShadow(blur_radius=2, color="black12"),
            on_click=lambda e: self.add_to_cart(product)
        )

    def add_to_cart(self, product):
        pid = product['id']
        if pid in self.cart:
            self.cart[pid]['qtd'] += 1
        else:
            self.cart[pid] = {'obj': product, 'qtd': 1}
        
        # Feedback visual
        self.page.snack_bar = ft.SnackBar(ft.Text(f"{product['nome']} adicionado!"), duration=1000)
        self.page.snack_bar.open = True
        self.update_total()
        self.page.update()

    def update_total(self):
        total = sum(item['qtd'] * item['obj']['preco_venda'] for item in self.cart.values())
        self.total_text.value = f"Total: {total:,.2f} MT"
        
    def total_footer(self):
        self.total_text = ft.Text("Total: 0.00 MT", size=18, weight=ft.FontWeight.BOLD)
        return ft.Container(
            content=ft.Row([
                self.total_text,
                ft.ElevatedButton("Finalizar", on_click=self.checkout, bgcolor="green", color="white")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=20,
            bgcolor="white",
            border=ft.border.only(top=ft.border.BorderSide(1, "grey"))
        )

    def show_cart_dialog(self, e):
        # Simplificado para poupar tempo: Apenas mostra lista
        items_view = ft.Column()
        for item in self.cart.values():
            items_view.controls.append(ft.Text(f"{item['qtd']}x {item['obj']['nome']}"))
            
        dialog = ft.AlertDialog(
            title=ft.Text("Carrinho"),
            content=items_view,
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def checkout(self, e):
        if not self.cart:
            self.page.snack_bar = ft.SnackBar(ft.Text("Carrinho vazio!"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()
            return
            
        # Preparar dados para registar_venda
        itens_venda = []
        total_venda = 0.0
        lucro_total = 0.0
        
        for pid, item in self.cart.items():
            qtd = item['qtd']
            prod = item['obj']
            preco = prod['preco_venda']
            custo = prod['preco_custo']
            
            itens_venda.append((pid, qtd, preco))
            total_venda += (qtd * preco)
            lucro_total += (qtd * (preco - custo))
            
        # Pegar ID do vendedor da sessão (armazenado no LoginView)
        vendedor_id = self.page.client_storage.get("user_id")
        
        # Registar no Banco
        try:
            venda_id = database.registar_venda(
                itens=itens_venda,
                total=total_venda,
                lucro=lucro_total,
                cliente="Mobile Cliente",
                vendedor_id=vendedor_id,
                vendedor_nome="Mobile User" # Simplificado, ideal seria buscar nome
            )
            
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Venda {venda_id} realizada com sucesso!"), bgcolor="green")
            self.page.snack_bar.open = True
            self.cart = {}
            self.update_total()
            self.page.go("/dashboard")
            
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao vender: {str(ex)}"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()
