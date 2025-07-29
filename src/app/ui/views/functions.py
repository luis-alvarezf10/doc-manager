import flet as ft

from src.utils.colors import grey, gradient_color
from src.app.ui.widgets.gradient_text import gradient_text
from src.app.ui.widgets.action_button import action_button
from src.app.ui.views.document_generation import document_generation_view
from src.app.ui.views.doc_functions.compress_view import compress_view
from src.app.ui.views.doc_functions.unify_pdf_view import pdf_convert_view

def functions_page(page: ft.Page, change_content_callback=None):
    def back_to_functions():
        if change_content_callback:
            change_content_callback(functions_page(page, change_content_callback))

    actions = [
        ("Generacion de documento", document_generation_view),
        ("Juntar PDFs", pdf_convert_view),
        ("Comprimir archivo", compress_view),
    ]

    def make_handler(view_func):
        return lambda e: change_content_callback(view_func(page, back_to_functions)) if change_content_callback else None

    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text("Bienvenido Usuario! a", size=40, weight=ft.FontWeight.BOLD),
                    gradient_text(
                        text="Axiology",
                        size=50,
                        gradient= gradient_color
                    ),
                    ft.Text("Document Manager", size=30, weight=ft.FontWeight.BOLD, color=grey),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            ft.Container(
                content=ft.Divider(thickness=2, color= grey),
                width=500,  # Ancho del divider
                padding=ft.padding.only(top=4, bottom=10)
            ),
            ft.Text(
                "En esta sección podras realizar acciones de manejo de documentos, en cada vista verás información referida para mayor comprensión.",
                size=20,
                text_align= ft.TextAlign.CENTER,
                width=700,
            ),
            ft.Text(
                "Elige una de las siguientes opciones: ",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=grey,
            ),
            *[action_button(text=label, on_click=make_handler(view)) for label, view in actions],
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
    )
