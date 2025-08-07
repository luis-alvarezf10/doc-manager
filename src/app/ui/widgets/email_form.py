import flet as ft
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
from src.app.ui.widgets.show_snackbar import show_snackbar
from src.app.ui.widgets.action_button import action_button
from src.utils.colors import *

def email_form(page: ft.Page, file_paths, file_names=None):
    # Manejar tanto archivo único como múltiples
    if isinstance(file_paths, str):
        file_paths = [file_paths]
        file_names = [file_names] if file_names else [file_paths[0].split('\\')[-1]]
    elif not file_names:
        file_names = [path.split('\\')[-1] for path in file_paths]
    def close_dialog():
        page.close(email_dialog)
    
    def send_email(e):
        email_to = email_field.value.strip()
        subject = subject_field.value.strip()
        message = message_field.value.strip()
        
        if not email_to or "@" not in email_to:
            page.open(show_snackbar(content="Ingresa un email válido", type="error"))
            return
        
        if not subject:
            subject = f"Archivo: {file_name}"
        
        if not message:
            if len(file_names) == 1:
                message = f"Te envío el archivo {file_names[0]}"
            else:
                message = f"Te envío {len(file_names)} archivos"
        
        # Mostrar loading
        send_btn.disabled = True
        send_btn.text = "Enviando..."
        progress_ring.visible = True
        page.update()
        
        try:
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = "axiologia.plaf@gmail.com" 
            sender_password = "tewg jtor ljze qjkj"      
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email_to
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            # Adjuntar archivos
            for file_path, file_name in zip(file_paths, file_names):
                with open(file_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {file_name}'
                )
                msg.attach(part)
            
            # Enviar email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email_to, msg.as_string())
            server.quit()
            
            page.open(show_snackbar(content=f"Archivo enviado a {email_to}", type="success"))
            close_dialog()
            
        except smtplib.SMTPAuthenticationError:
            page.open(show_snackbar(content="Error de autenticación. Verifica email y contraseña", type="error"))
        except smtplib.SMTPConnectError:
            page.open(show_snackbar(content="No se puede conectar al servidor. Verifica tu conexión a internet", type="error"))
        except Exception as ex:
            if "getaddrinfo failed" in str(ex):
                page.open(show_snackbar(content="Sin conexión a internet o servidor bloqueado", type="error"))
            else:
                page.open(show_snackbar(content=f"Error: {ex}", type="error"))
        finally:
            send_btn.disabled = False
            send_btn.text = "Enviar"
            progress_ring.visible = False
            page.update()
    
    # Campos del formulario
    email_field = ft.TextField(
        label="Email destinatario",
        prefix_icon=ft.Icons.EMAIL,
        value="axiologia.plaf@gmail.com",
        filled=True,
        border_radius=8,
        border_width=0,
        border_color="transparent",
        focused_border_width=1,
        text_size=16,
    )
    
    subject_field = ft.TextField(
        label="Asunto",
        prefix_icon=ft.Icons.SUBJECT,
        value= f"Mensaje de axiología PLAF",
        filled=True,
        border_radius=8,
        border_width=0,
        border_color="transparent",
        focused_border_width=1,
        text_size=16,
    )
    
    message_field = ft.TextField(
        label="Mensaje",
        prefix_icon=ft.Icons.MESSAGE,
        multiline=True,
        min_lines=3,
        max_lines=5,
        value=f"Te envío {len(file_names)} archivo{'s' if len(file_names) > 1 else ''}",
        filled=True,
        border_radius=8,
        border_width=0,
        border_color="transparent",
        focused_border_width=1,
        text_size=16,
    )
    
    progress_ring = ft.ProgressRing(
        width=20,
        height=20,
        visible=False
    )
    
    send_btn = action_button(text="Enviar", icon=ft.Icons.SEND, width=150, height=40, on_click=send_email)

    
    # Información de los archivos
    files_info = ft.Column([
        ft.Card(
            content=ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.ATTACH_FILE, color=ft.Colors.ORANGE),
                    ft.Column([
                        ft.Text(name, weight=ft.FontWeight.BOLD, size=14),
                    ], spacing=2, expand=True)
                ]),
                padding=10
            ),
            elevation=2
        ) for name in file_names
    ], spacing=5)
    
    files_container = ft.Container(
        content=ft.Column([
            ft.Text(f"{len(file_names)} archivo{'s' if len(file_names) > 1 else ''} adjunto{'s' if len(file_names) > 1 else ''}", 
                   weight=ft.FontWeight.BOLD, size=16),
            files_info
        ],
        scroll= ft.ScrollMode.AUTO,
        expand=True
        ),
        border_radius=10,
        height=200,
        padding=15,
        width=400,
    )
    
    email_dialog = ft.AlertDialog(
        title=ft.Row([
            ft.Text("Enviar por Email", size=20, weight=ft.FontWeight.BOLD),
            ft.IconButton(
                icon=ft.Icons.CLOSE,
                icon_color=ft.Colors.GREY_600,
                on_click=lambda _: close_dialog()
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        
        content=ft.Column([
            email_field,
            subject_field,
            message_field,
            files_container,
        ], 
        tight=True, 
        width=450,
        alignment=ft.alignment.center,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        
        actions=[
            ft.Row([
                ft.Container(width=10),
                ft.Row([
                    progress_ring,
                    ft.Container(width=10),
                    send_btn
                ])
            ], alignment=ft.MainAxisAlignment.END)
        ],
        
        shape=ft.RoundedRectangleBorder(radius=15),
        elevation=10
    )
    
    return email_dialog