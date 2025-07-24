import flet as ft

from src.app.utils.colors import *


def input_form(*, label: str, icon: str) -> ft.TextField:
    return ft.TextField(
        width=400,
        label = label,
        label_style = ft.TextStyle(
            color = grey,
            weight= ft.FontWeight.W_600,
            size = 15
        ),
        
        
        border_color= grey,
        border_radius=10,
        border_width=1,
        
        bgcolor = white,
        color = dark_grey,
        
        text_size=15,
        text_style=ft.TextStyle(
            weight=ft.FontWeight.W_600,
            color=dark_grey
        ),
        
        prefix_icon=icon,
        
        can_reveal_password=True if label == "Contraseña" else False,
        password = True if label == "Contraseña" else False
        
    )