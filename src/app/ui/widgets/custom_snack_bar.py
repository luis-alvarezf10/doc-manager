import flet as ft

def custom_snack_bar(*, content: str) -> ft.SnackBar:
    return ft.SnackBar(
        bgcolor= "#70d35d",
        content=ft.Text(content)
    )