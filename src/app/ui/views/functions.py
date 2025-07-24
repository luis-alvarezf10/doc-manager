import flet as ft

from src.app.utils.colors import dark_grey
from src.app.ui.widgets.action_button import action_button
from src.app.ui.views.doc_functions.document_generation_view import document_generation_view
from src.app.ui.views.doc_functions.compress_view import compress_view
from src.app.ui.views.doc_functions.unify_pdf_view import pdf_convert_view

def functions_page(page: ft.Page, change_content_callback=None):
    def back_to_functions():
        if change_content_callback:
            change_content_callback(functions_page(page, change_content_callback))

    actions = [
        (" 📄 Generacion de documento", document_generation_view),
        ("📄 Juntar PDFs", pdf_convert_view),
        ("💾 Comprimir documento", compress_view),
    ]

    def make_handler(view_func):
        return lambda e: change_content_callback(view_func(page, back_to_functions)) if change_content_callback else None

    return ft.Column(
        controls=[
            ft.Text(
                "Elige una de las siguientes opciones",
                size=30,
                weight=ft.FontWeight.BOLD,
                color=dark_grey,
            ),
            *[action_button(text=label, on_click=make_handler(view)) for label, view in actions],
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
    )
