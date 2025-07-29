import flet as ft
from src.utils.colors import dark_grey

def info_text(*, text: str, size: int = 16) -> ft.Text:
    return ft.Text(
        value=text,
        size=size,
    )
