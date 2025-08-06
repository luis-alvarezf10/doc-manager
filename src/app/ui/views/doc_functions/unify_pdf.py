import flet as ft
from src.utils.colors import *
from src.app.ui.widgets.custom_app_bar import custom_app_bar
from src.app.ui.widgets.info_selected_mode import info_text
from src.app.ui.widgets.show_snackbar import show_snackbar
from src.app.ui.widgets.action_button import action_button
from src.app.ui.widgets.gradient_button import gradient_button
from src.utils.colors import main_gradient_color
from src.app.ui.widgets.show_snackbar import show_snackbar
from PyPDF2 import PdfMerger
import os

def pdf_convert_view(page: ft.Page, back_callback=None):
    def handle_close(e):
        if back_callback:
            back_callback()
    
    app_bar = custom_app_bar(
        text="Unir PDFs",
        on_click=handle_close
    )
    
    info = ft.Column(
        controls=[
            ft.Text("Selecciona archivos PDF para unificar", size=25, text_align=ft.TextAlign.CENTER, style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight="bold"),
            info_text(text="1. Click al boton Seleccionar PDF"),
            info_text(text="2. Selecciona los archivos PDF que deseas unir"),
            info_text(text="3. Click en el boton Unir PDFs"),
            info_text(text="4. El archivo PDF resultante se guardará en la carpeta de -> PDFs Unificados"),
        ],
        width=800
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
            else:
                page.open(show_snackbar(content="No se encontraron archivos PDF válidos", type="error"))
        else:
            page.open(show_snackbar(content="No se seleccionaron archivos", type="error"))
        page.update()
    
    def update_pdf_list():
        pdf_list.controls.clear()
        
        if not selected_pdf_files:
            pdf_list.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Sin archivos seleccionados actualmente",
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.GREY_600,
                        size=16
                    ),
                    expand=True,
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
        else:
            for i, file in enumerate(selected_pdf_files):
                pdf_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Row([
                                ft.Text(f"{i+1}", weight=ft.FontWeight.BOLD, size=16),
                                ft.Icon(ft.Icons.PICTURE_AS_PDF, color="red"),
                                ft.Text(file.name, expand=True, size=16),
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
                                    icon_color="red",
                                    tooltip="Eliminar archivo"
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
            page.open(show_snackbar(content="Selecciona al menos 2 archivos PDF", type="error"))
            return
        
        progress.visible = True
        merge_button.disabled = True
        page.update()
        
        try:
            merger = PdfMerger()
            for file in selected_pdf_files:
                merger.append(file.path)
            
            desktop_path = os.path.join(os.path.expanduser("~"), "Documents")
            manager_path = os.path.join(desktop_path, "Axiology Document Manager")
            output_dir = os.path.join(manager_path, "PDFs Unificados")
            os.makedirs(output_dir, exist_ok=True)

            # Lógica de nombres para evitar sobrescritura
            if name_pdf.value.strip():
                base_name = name_pdf.value.strip().upper()
                filename = f"{base_name}.pdf"
            else:
                base_name = "PDF UNIFICADO"
                filename = f"{base_name}.pdf"
            
            # Evitar sobrescritura
            cont = 1
            while os.path.exists(os.path.join(output_dir, filename)):
                if name_pdf.value.strip():
                    filename = f"{base_name} ({cont}).pdf"
                else:
                    filename = f"{base_name} ({cont}).pdf"
                cont += 1

            # Guardar PDF
            output_path = os.path.join(output_dir, filename)
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)
            merger.close()

            # Guardar ruta final
            nonlocal output_folder_path
            output_folder_path = output_dir
            page.open(show_snackbar(content=f"PDF unificado guardado en: {output_path}", type="success"))
        except Exception as ex:
            page.open(show_snackbar(content=f"Error al unificar PDFs: {str(ex)}", type="error"))
        finally:
            progress.visible = False
            merge_button.disabled = False
            page.update()
    status_text = ft.Text("", size=14, text_align= "center", weight= "bold")
    selected_pdf_files = []
    output_folder_path = None
    
    progress = ft.ProgressRing(
        visible=False,
        width=20,
        height=20
    )
    
    pdf_list = ft.Column(scroll=ft.ScrollMode.AUTO)
    
    file_picker = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(file_picker)
    
    pick_files_button = action_button(
        text="Seleccionar PDF",
        icon=ft.Icons.FOLDER_OPEN,
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=True,
            allowed_extensions=["pdf"]
        )
    )
    
    name_pdf = ft.TextField(
            label="Nombre de nuevo PDF",
            filled=True,
            width=400,
            border_radius=8,
            border_width=0,
            border_color="transparent",
            focused_border_width=0,
            text_size=16,
    )
    
    
    merge_button = gradient_button(
        text="Unir PDFs",
        width=200,
        height=40,
        gradient=main_gradient_color,
        on_click=merge_pdfs,
    )
    
    first_step = ft.Row(
        controls= [
            pick_files_button,
            name_pdf,
            merge_button,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )
    
    # Mostrar mensaje inicial después de definir merge_button
    update_pdf_list()
    return ft.Column(
        controls=[
            app_bar,
            ft.Column([
                info,
                ft.Divider(),
                first_step,
                ft.Row([
                        status_text,
                        progress
                    ], 
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    width=1000
                ),
                ft.Container(
                    content=pdf_list,
                    padding=10,
                    width=1000
                ),
            ], 
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,   
            ),
            ft.Container(height=30)
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )