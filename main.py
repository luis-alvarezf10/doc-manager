import flet as ft
import os
from src.app.ui.views.home import HomeView

def main(page: ft.Page):
    page.title = "Lexis Nova"
    page.window_full_screen = True
    
    def route_change(route):
        page.views.clear()
        if page.route == "/home":
            page.views.append(HomeView(page))
        page.update()
    
    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/home")
    

ft.app(target=main, view=ft.AppView.FLET_APP)
        
        