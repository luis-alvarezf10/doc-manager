import flet as ft
from src.app.utils.colors import *

def action_button(*, text: str, on_click) -> ft.ElevatedButton:
    return ft.ElevatedButton(
        content= ft.Text(
            text,
            size=20,
            weight=ft.FontWeight.W_600,
        ),
        width=400,
        height=50,
        bgcolor=blue,
        color=white,
        on_click=on_click
    )