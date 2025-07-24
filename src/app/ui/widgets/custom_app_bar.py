import flet as ft
from src.app.utils.colors import *

def custom_app_bar(*, text, on_click) -> ft.Container:
    return ft.Container(
        content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_color=white,
                        on_click= on_click
                    ),
                    ft.Text(text, size=20, 
                            weight=ft.FontWeight.BOLD,
                            color=white),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
        padding=10,
        gradient=ft.LinearGradient(
            colors=[dark_blue, blue],
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right
        )
    )