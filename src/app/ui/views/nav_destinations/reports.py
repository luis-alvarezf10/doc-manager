import flet as ft

from src.app.ui.widgets.info_selected_mode import info_text
from src.app.ui.widgets.gradient_button import gradient_button
from src.app.ui.widgets.show_snackbar import show_snackbar
from src.utils.colors import main_gradient_color
from src.utils.email_sender import send_email

def handle_send_email(page, subject_field, description_field):
    """Maneja el envío del email de reporte"""
    if not subject_field.value or not description_field.value:
        page.open(show_snackbar(content="Por favor, completa todos los campos.", type="warning"))
        return
    
    success, message = send_email("luigisystems10@gmail.com",subject_field.value, description_field.value)
    
    if success:
        subject_field.value = ""
        description_field.value = ""
        page.open(show_snackbar(content="Correo enviado correctamente, ¡muchas gracias por su comentario!", type="success"))
    else:
        page.open(show_snackbar(content="Problemas con mandar el correo: error", type="error"))
    
    page.update()

def create_report_view(page):
    
    info = ft.Column(
        controls=[
            ft.Text("Sistema de Gestión de Reportes y Sugerencias", size=25, text_align=ft.TextAlign.CENTER, style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight="bold"),
            info_text(text="¿Presentantes un problema con el sistema o tienes alguna sugerencia a mejorar?"),
            info_text(text="1. Ingresa el asunto del mensaje."),
            info_text(text="2. Escribe el cuerpo del mensaje."),
            info_text(text="3. Haz clic en 'Enviar'."),
            info_text(text="¡Gracias por tu apoyo! te responderé lo antes posible")
        ],
        width=800
    )

    subject = ft.TextField(
        label="Asunto", 
        width=400,
        border_width=0,
        border_color="transparent",
        focused_border_width=0,
        text_size=16,
        border_radius=8,
        filled=True,
        prefix_icon=ft.Icons.SUBJECT
    )

    description = ft.TextField(
        label="Descripción",
        multiline=True,
        width=400,
        min_lines=3,
        max_lines=5,
        border_width=0,
        border_color="transparent",
        focused_border_width=0,
        text_size=16,
        border_radius=8,
        filled=True,
        prefix_icon=ft.Icons.DESCRIPTION
    )

    email_form = ft.Card(
        content=ft.Container(
            content=  ft.Column(
                controls=[
                    ft.Text("Formulario de Email de Reporte", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(height=20),
                    subject,
                    description,    
                    ft.Container(height=20),
                    gradient_button(text="Enviar",
                                    gradient=main_gradient_color,
                                    on_click=lambda e: handle_send_email(page, subject, description)
                                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=20,
            width=500
        ),
        elevation=8
    )
    
    return ft.Column([
        ft.Container(height=20),
        info,
        ft.Divider(),
        email_form,
        ft.Text("Este mensaje será enviado al corre: luigisystems10@gmail.com", size=12, text_align=ft.TextAlign.CENTER, color="grey")
    ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,  
        scroll=ft.ScrollMode.AUTO, 
        expand=True
    )