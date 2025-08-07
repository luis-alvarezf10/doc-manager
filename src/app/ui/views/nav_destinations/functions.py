import flet as ft

from src.utils.colors import grey, main_gradient_color, blue
from src.app.ui.widgets.gradient_text import gradient_text
from src.app.ui.widgets.gradient_button import gradient_button
from src.app.ui.views.doc_functions.document_generation import document_generation_view
from src.app.ui.views.doc_functions.compress import compress_view
from src.app.ui.views.doc_functions.unify_pdf import pdf_convert_view
from src.app.ui.widgets.show_snackbar import show_snackbar

def functions_page(page: ft.Page, change_content_callback=None):
    def back_to_functions():
        if change_content_callback:
            change_content_callback(functions_page(page, change_content_callback))

    actions = [
        ("Generar documentos", document_generation_view),
        ("Unir PDFs", pdf_convert_view),
        ("Comprimir PDFs", compress_view),
    ]

    def make_handler(view_func):
        return lambda e: change_content_callback(view_func(page, back_to_functions)) if change_content_callback else None

    def open_gemini(e):
        page.launch_url("https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwjP8evEw_eOAxUzVzABHW6dDaAQFnoECAwQAQ&url=https%3A%2F%2Fgemini.google.com%2F%3Fhl%3Des&usg=AOvVaw2TPryCJcTmCeFmmiqqwBRa&opi=89978449")
        page.open(show_snackbar(content="Abriendo Gemini AI", type="success"))

    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text("Bienvenido Usuario! a", size=40, weight=ft.FontWeight.BOLD),
                    gradient_text(
                        text="Axiology",
                        size=50,
                        gradient= main_gradient_color
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
            *[gradient_button(text=label,gradient=main_gradient_color, on_click=make_handler(view)) for label, view in actions],
            ft.Text(
                "O puedes abrir la herramienta de IA de Google Gemini AI",
                size=16,
                color=grey,
            ),
            ft.OutlinedButton(
                content= gradient_text(text="Abrir Gemini AI", gradient=main_gradient_color, size=20),
                on_click= open_gemini,
                width= 350,
                height= 48,
                style= ft.ButtonStyle( 
                                      side= ft.BorderSide(1, blue),
                                      shape= ft.RoundedRectangleBorder(radius=10),
                                      )
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
    )
