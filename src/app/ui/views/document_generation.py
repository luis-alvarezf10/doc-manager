import flet as ft 
from src.app.ui.widgets.custom_app_bar import custom_app_bar
from src.app.ui.views.doc_functions.buy_and_sell import compraventa_contract_view

def document_generation_view(page: ft.Page, back_callback: callable = None) -> ft.View:
    def handle_close(e):
        if back_callback:
            back_callback()
    
    app_bar = custom_app_bar(
        text="Generación de Documentos",  # Cambiado para que coincida con la funcionalidad
        on_click=handle_close
    )

    # Contenedor donde se mostrará el contenido dinámico
    content_area = ft.Column(
        controls=[], 
        expand=True,
        scroll=ft.ScrollMode.AUTO,
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
        ft.Image(src="/assets/document_icon.png", width=200, height=200)
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    content_area.controls.append(initial_content)

    # Menú de tipos de contrato
    menu = ft.Row(
        controls=[
            ft.ElevatedButton(
                "Compra Venta de inmueble", 
                on_click=lambda e: change_content(compraventa_contract_view(page))
            ),
            ft.ElevatedButton(
                "Constitutivo de empresa", 
                on_click=lambda e: change_content(ft.Text("Contrato: Constitutivo de empresa"))
            ),
            ft.ElevatedButton(
                "Contrato de trabajo", 
                on_click=lambda e: change_content(ft.Text("Contrato: Trabajo"))
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
        wrap=True
    )

    return ft.Column(
        controls=[
            app_bar,
            ft.Text("Generación de documentos"),
            ft.Text("Selecciona el tipo de documento que deseas generar."),
            menu,
            content_area
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
