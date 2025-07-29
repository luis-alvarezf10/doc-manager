import flet as ft

def show_snackbar(*, content:str, type: str = "success") -> ft.SnackBar:
    color_map = {
        "success": ft.Colors.GREEN,
        "error": ft.Colors.RED,
        "warning": ft.Colors.YELLOW,
        "info": ft.Colors.BLUE,
    }
    emoji = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
    }
    return ft.SnackBar(
        bgcolor=color_map.get(type, ft.Colors.GREEN),
        behavior= ft.SnackBarBehavior.FLOATING,
        content= ft.Text(
            value= f"{emoji.get(type, '')}{content}",
            color= ft.Colors.WHITE,
            weight="bold"
        )
    )