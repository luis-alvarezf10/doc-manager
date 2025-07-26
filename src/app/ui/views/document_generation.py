import flet as ft 
from src.app.ui.widgets.custom_app_bar import custom_app_bar
# Asegúrate de importar functions_page si lo usas
# from src.app.ui.views.doc_functions.functions_page import functions_page

from src.app.ui.views.doc_functions.buy_and_sell import compraventa_contract_view

def document_generation_view(page: ft.Page, back_callback: callable = None) -> ft.View:
    def handle_close(e):
        if back_callback:
            back_callback()
    
    app_bar = custom_app_bar(
        text="Gestión de Empleados",
        on_click=handle_close
    )

    # Contenedor donde se mostrará el contenido dinámico
    content_area = ft.Column(
        controls=[], 
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )

    # Esta función actualiza el contenido dinámico
    def change_content(new_content):
        content_area.controls.clear()
        content_area.controls.append(new_content)
        page.update()

    # Asegúrate de tener esta función definida e importada correctamente
    # Por ahora te dejo un placeholder de ejemplo:
    def functions_page(page, change_cb):
        return ft.Text("Aquí iría la vista de funciones")

    # Cargar contenido inicial
    functions_view = functions_page(page, change_content)
    content_area.controls.append(functions_view)

    # Menú de tipos de contrato
    menu = ft.Row(
        controls=[
            ft.ElevatedButton("Compra Venta de inmueble", on_click=lambda e: change_content(
            compraventa_contract_view(change_content)
            )),
            ft.ElevatedButton("Constitutivo de empresa", on_click=lambda e: change_content(ft.Text("Contrato: Constitutivo de empresa"))),
            ft.ElevatedButton("Contrato de trabajo", on_click=lambda e: change_content(ft.Text("Contrato: Trabajo"))),
        ]
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
