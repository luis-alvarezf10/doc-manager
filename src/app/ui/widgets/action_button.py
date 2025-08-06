import flet as ft
from src.utils.colors import white

def action_button(*, text: str, icon:str, width: int = 200, height: int = 40, bgcolor: str = ft.Colors.ORANGE, on_click, visible: bool = True) -> ft.ElevatedButton:
    return ft.ElevatedButton(
        text= text,
        icon= icon,
        width= width,
        height= height,
        bgcolor=bgcolor,
        color=white,
        on_click=on_click, 
        visible=visible,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            text_style=ft.TextStyle(
            size=16, 
            weight="bold",
            ),
        )
    )