import flet as ft
from src.utils.colors import *
from src.app.ui.widgets.custom_app_bar import custom_app_bar
from PyPDF2 import PdfMerger
import os

def pdf_convert_view(page: ft.Page, back_callback=None):
    def handle_close(e):
        if back_callback:
            back_callback()
    
    app_bar = custom_app_bar(
        text="Convertir PDF",
        on_click=handle_close
    )
    
    def pick_files_result(e: ft.FilePickerResultEvent):
        nonlocal selected_pdf_files
        if e.files:
            new_pdf_files = [f for f in e.files if f.name.lower().endswith(".pdf")]
            if new_pdf_files:
                for new_file in new_pdf_files:
                    if not any(f.path == new_file.path for f in selected_pdf_files):
                        selected_pdf_files.append(new_file)
                update_pdf_list()
                status_text.value = ""
            else:
                status_text.value = "Ningún archivo PDF válido seleccionado."
        else:
            status_text.value = "Selección de archivos cancelada."
        page.update()
    
    def update_pdf_list():
        pdf_list.controls.clear()
        for i, file in enumerate(selected_pdf_files):
            pdf_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PICTURE_AS_PDF, color="red"),
                            ft.Text(file.name, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.ARROW_UPWARD,
                                on_click=lambda e, idx=i: move_file_up(idx),
                                disabled=i == 0
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ARROW_DOWNWARD,
                                on_click=lambda e, idx=i: move_file_down(idx),
                                disabled=i == len(selected_pdf_files) - 1
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                on_click=lambda e, idx=i: remove_file(idx),
                                icon_color="red"
                            )
                        ]),
                        padding=10
                    )
                )
            )
        merge_button.disabled = len(selected_pdf_files) < 2
        page.update()
    
    def move_file_up(index):
        if index > 0:
            selected_pdf_files[index], selected_pdf_files[index-1] = selected_pdf_files[index-1], selected_pdf_files[index]
            update_pdf_list()
    
    def move_file_down(index):
        if index < len(selected_pdf_files) - 1:
            selected_pdf_files[index], selected_pdf_files[index+1] = selected_pdf_files[index+1], selected_pdf_files[index]
            update_pdf_list()
    
    def remove_file(index):
        selected_pdf_files.pop(index)
        update_pdf_list()
    
    def merge_pdfs(e):
        if len(selected_pdf_files) < 2:
            status_text.value = "Selecciona al menos 2 archivos PDF"
            page.update()
            return
        
        progress.visible = True
        merge_button.disabled = True
        status_text.value = "Unificando PDFs..."
        page.update()
        
        try:
            merger = PdfMerger()
            for file in selected_pdf_files:
                merger.append(file.path)
            
            # Obtener nombre personalizado o usar por defecto
            pdf_name = name_pdf.value.strip() if name_pdf.value.strip() else "PDF_Unificado"
            if not pdf_name.endswith(".pdf"):
                pdf_name += ".pdf"
            
            # Crear carpeta PDFs_unificados en PLAF_system
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            plaf_system_path = os.path.join(desktop_path, "PLAF_system")
            output_dir = os.path.join(plaf_system_path, "PDFs_unificados")
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, pdf_name)
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)
            merger.close()
            
            nonlocal output_folder_path
            output_folder_path = output_dir
            status_text.value = f"PDF unificado guardado en: {output_path}"
            status_text.color = "green"
            open_output_folder_button.visible = True
        except Exception as ex:
            status_text.value = f"Error al unificar PDFs: {str(ex)}"
            status_text.color = "red"
            open_output_folder_button.visible = False
        finally:
            progress.visible = False
            merge_button.disabled = False
            page.update()
    
    selected_pdf_files = []
    output_folder_path = None
    
    status_text = ft.Text("", size=14)
    
    progress = ft.ProgressRing(
        visible=False,
        width=20,
        height=20
    )
    
    pdf_list = ft.Column(scroll=ft.ScrollMode.AUTO)
    
    file_picker = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(file_picker)
    
    pick_files_button = ft.ElevatedButton(
        text="Seleccionar archivos PDF",
        bgcolor=dark_grey,
        color="white",
        icon=ft.Icons.UPLOAD_FILE,
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=True,
            allowed_extensions=["pdf"]
        )
    )
    
    name_pdf = ft.TextField(label="Nombre de nuevo PDF",
                            border_radius=20,
                            border_color=grey)
    
    first_step = ft.Row(
        controls= [
            pick_files_button,
            name_pdf
        ]
    )
    
    merge_button = ft.ElevatedButton(
        text="Unificar PDFs",
        bgcolor="green",
        color="white",
        icon=ft.Icons.MERGE,
        disabled=True,
        on_click=merge_pdfs
    )
    
    def open_folder(e):
        try:
            print(f"Intentando abrir: {output_folder_path}")
            if output_folder_path and os.path.exists(output_folder_path):
                os.startfile(output_folder_path)
                status_text.value = "Carpeta abierta correctamente"
                status_text.color = "blue"
            else:
                status_text.value = "La carpeta no existe"
                status_text.color = "red"
        except Exception as ex:
            status_text.value = f"Error al abrir carpeta: {str(ex)}"
            status_text.color = "red"
        page.update()
    
    open_output_folder_button = ft.ElevatedButton(
        text="Abrir carpeta de salida",
        bgcolor=blue,
        color=white,
        icon=ft.Icons.FOLDER_OPEN,
        visible=False,
        on_click=open_folder
    )
    
    return ft.Column(
        controls=[
            app_bar,
            ft.Container(
                content=ft.Column([
                    ft.Text("Selecciona archivos PDF para unificar", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    first_step,
                    ft.Container(
                        content=pdf_list,
                        height=300,
                        border=ft.border.all(1, ft.Colors.GREY_400),
                        border_radius=8,
                        padding=10
                    ),
                    ft.Row([
                        merge_button,
                        progress
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    status_text,
                    open_output_folder_button
                ], spacing=20),
                padding=20,
                expand=True
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )