import flet as ft
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.products_view import ProductsView
from views.pos_view import POSView

def main(page: ft.Page):
    page.title = "Gestor Fácil"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Configurações para simular mobile no PC
    page.window_width = 375
    page.window_height = 812
    page.padding = 0
    
    # Cores do Tema
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#2196F3",
            primary_container="#E3F2FD",
            secondary="#03DAC6",
        )
    )

    def route_change(route):
        page.views.clear()
        
        # Rota de Login
        if page.route == "/login":
            page.views.append(LoginView(page))
            
        # Rota Dashboard
        elif page.route == "/dashboard":
            page.views.append(DashboardView(page))
            
        # Rota Produtos
        elif page.route == "/products":
            page.views.append(ProductsView(page))
            
        # Rota POS
        elif page.route == "/pos":
            page.views.append(POSView(page))
            
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Iniciar na tela de login
    page.go("/login")

if __name__ == "__main__":
    ft.app(target=main)
