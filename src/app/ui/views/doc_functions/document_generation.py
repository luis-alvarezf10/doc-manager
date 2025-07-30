import flet as ft 
from src.app.ui.widgets.custom_app_bar import custom_app_bar
from src.app.ui.views.doc_generation.buy_and_sell import compraventa_contract_view
from src.utils.colors import grey


def document_generation_view(page: ft.Page, back_callback: callable = None) -> ft.View:
    title = "Generación de Documentos Automatizado"
    def handle_close(e):
        if back_callback:
            back_callback()
    
    app_bar = custom_app_bar(
        text=title, 
        on_click=handle_close
    )

    # Contenedor donde se mostrará el contenido dinámico
    content_area = ft.Column(
        controls=[], 
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )

    # Función para cambiar el contenido
    def change_content(new_content):
        content_area.controls.clear()
        content_area.controls.append(new_content)
        page.update()

    # Vista inicial (puedes cambiarla por lo que necesites)
    initial_content = ft.Column([
        ft.Text("Selecciona un tipo de contrato para comenzar", 
               size=20, weight="bold"),
        ft.Icon(ft.Icons.EDIT_DOCUMENT, size=50, color=grey),
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    content_area.controls.append(initial_content)

    # Menú de tipos de contrato
    buttons = [
        ("Compra Venta", compraventa_contract_view(page)),
        ("Constitutivo", "Contrato: Constitutivo de empresa"),
        ("Trabajo", "Contrato: Trabajo")
    ]

    menu = ft.Row(
        controls=[
            ft.ElevatedButton(
                text.upper(),
                on_click=lambda e, c=content: change_content(
                    c if isinstance(c, ft.Control) else ft.Text(c)
                ), 
                bgcolor=grey,
                color=ft.Colors.WHITE,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                )
            ) for text, content in buttons
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
        wrap=True
    )

    return ft.Column(
        controls=[
            app_bar,
            ft.Text(title, size=25, weight="bold", color=grey),
            ft.Text("Selecciona el tipo de documento que deseas generar.", size=16, color=grey),
            menu,
            ft.Divider(), 
            content_area
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
