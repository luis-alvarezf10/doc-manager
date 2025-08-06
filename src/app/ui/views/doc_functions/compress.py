import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import subprocess
import tempfile
import io
import base64

import flet as ft
from pypdf import PdfReader, PdfWriter
from PIL import Image
import fitz  # PyMuPDF

from src.utils.colors import *
from src.app.ui.widgets.custom_app_bar import custom_app_bar
from src.app.ui.widgets.info_selected_mode import info_text
from src.app.ui.widgets.action_button import action_button
from src.app.ui.widgets.show_snackbar import show_snackbar
from src.app.ui.widgets.gradient_button import gradient_button
from src.utils.colors import main_gradient_color

def compress_view(page: ft.Page, back_callback=None):
    def handle_close(e):
        if back_callback:
            back_callback()
    
    app_bar = custom_app_bar(
        text="Comprimir Archivo PDF",
        on_click=handle_close
    )
    
    info = ft.Column(
        controls=[
            ft.Text("Selecciona archivos PDF para comprimir", size=25, text_align=ft.TextAlign.CENTER, style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight="bold"),
            info_text(text="1. Click al boton Seleccionar PDF"),
            info_text(text="2. Selecciona los archivos PDF que deseas comprimir"),
            info_text(text="3. Click en el boton Unir PDFs"),
            info_text(text="4. El archivo PDF resultante se guardará en la carpeta de -> PDFs Coprimidos"),
        ],
        width=800
    )
    
    def pick_files_result(e: ft.FilePickerResultEvent):
        nonlocal selected_pdf_files
        if e.files:
            new_pdf_files = [f for f in e.files if f.name.lower().endswith(".pdf")]
            if new_pdf_files:
                # Agregar archivos nuevos evitando duplicados
                for new_file in new_pdf_files:
                    if not any(f.path == new_file.path for f in selected_pdf_files):
                        selected_pdf_files.append(new_file)
                
                update_pdf_list()
                status_text.value = ""
        else:
            page.open(show_snackbar(content="No se seleccionaron archivos", type="error"))
        page.update()

    # Lista de archivos seleccionados
    selected_pdf_files = []
    
    # Definir elementos de UI
    pdf_list= ft.Column(scroll=ft.ScrollMode.AUTO)
    def get_file_size(file_path):
        try:
            size_bytes = os.path.getsize(file_path)
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        except:
            return "? MB"
    
    def remove_pdf_from_list(file_to_remove):
        nonlocal selected_pdf_files
        selected_pdf_files = [f for f in selected_pdf_files if f.path != file_to_remove.path]
        update_pdf_list()
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
            compress_button.disabled = True
        else:
            for i, file in enumerate(selected_pdf_files):
                file_size = get_file_size(file.path)
                pdf_list.controls.append(
                    ft.Card(
                        ft.Container(
                            content= ft.Row([
                                ft.Text(f"{i+1}", weight=ft.FontWeight.BOLD, size=16),
                                ft.Icon(ft.Icons.PICTURE_AS_PDF, color="red"),
                                ft.Column([
                                    ft.Text(file.name, size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(file_size, size=12, color=ft.Colors.GREY_600)
                                ], spacing=2, expand=True),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color="red",
                                    on_click=lambda e, file=file: remove_pdf_from_list(file),
                                    tooltip="Eliminar archivo"
                                )
                                
                            ]),
                            padding=10
                        )
                    )
                )
            
            compress_button.disabled = False
            compress_button.on_click = lambda _: compress_pdfs(selected_pdf_files)
            
    status_text = ft.Text("", size=14, text_align= "center", weight= "bold")
    
    progress = ft.ProgressRing(
        visible= False,
        width=20,
        height=20
    )
    
    # Selector de nivel de compresión
    compression_level = ft.Dropdown(
        label="Nivel de compresión",
        value="normal",
        options=[
            ft.dropdown.Option(key="normal", text="Normal (Recomendada)"),
            ft.dropdown.Option(key="extrema", text="Extrema (Máxima reducción)")
        ],
        filled=True,
        width=300,
        border_radius=8,
        border_width=0,
        border_color="transparent",
        focused_border_width=0,
        text_size=16
    )
    
    results_container = ft.Column([], visible=False, spacing=5, scroll=ft.ScrollMode.AUTO)
    
    compress_button = gradient_button(
        text="Comprimir PDFs",
        width=200,
        height=40,
        gradient=main_gradient_color,
        on_click=lambda _: compress_pdfs(selected_pdf_files)
    )
    
    
    open_output_folder_button = ft.ElevatedButton(
        text="Abrir carpeta de salida",
        bgcolor=blue,
        color=white,
        visible=False,
    )
    

    
    file_picker = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(file_picker)

    # Función para comprimir los PDFs
    def compress_pdfs(files):
        status_text.value = "Comprimiendo PDFs... Esto puede tardar un momento."
        progress.visible = True
        status_text.color = ft.Colors.BLUE_800
        results_container.visible = False
        results_container.controls.clear()
        page.update()

        desktop_path = os.path.join(os.path.expanduser("~"), "Documents")
        plaf_system_path = os.path.join(desktop_path, "Axiology Document Manager")
        output_dir = os.path.join(plaf_system_path, "PDFs Comprimidos")
        os.makedirs(output_dir, exist_ok=True)

        compressed_count = 0
        failed_count = 0
        compression_results = []
        
        for file in files:
            input_path = file.path
            file_name_without_ext = os.path.splitext(file.name)[0]
            
            # Lógica para evitar sobrescritura
            base_filename = f"{file_name_without_ext} comprimido.pdf"
            output_path = os.path.join(output_dir, base_filename)
            
            cont = 1
            while os.path.exists(output_path):
                filename = f"{file_name_without_ext} comprimido ({cont}).pdf"
                output_path = os.path.join(output_dir, filename)
                cont += 1

            try:
                reader = PdfReader(input_path)
                writer = PdfWriter()
                
                for page_num, pdf_page in enumerate(reader.pages):
                    # Extraer y comprimir imágenes
                    if '/XObject' in pdf_page['/Resources']:
                        xObject = pdf_page['/Resources']['/XObject']
                        for obj_name in xObject:
                            obj = xObject[obj_name]
                            if obj.get('/Subtype') == '/Image':
                                try:
                                    # Extraer datos de imagen
                                    width = obj.get('/Width')
                                    height = obj.get('/Height')
                                    
                                    # Configurar parámetros según nivel de compresión
                                    if compression_level.value == "extrema":
                                        min_size = 200  # Comprimir imágenes más pequeñas
                                        max_dimension = 800  # Redimensionar más agresivo
                                        quality = 40  # Menor calidad
                                    else:  # normal
                                        min_size = 300
                                        max_dimension = 1200
                                        quality = 60
                                    
                                    if width and height and width > min_size and height > min_size:
                                        # Comprimir imágenes según configuración
                                        img_data = obj.get_data()
                                        img = Image.open(io.BytesIO(img_data))
                                        
                                        # Redimensionar si es muy grande
                                        if max(img.size) > max_dimension:
                                            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                                        
                                        # Comprimir
                                        output_buffer = io.BytesIO()
                                        if img.mode in ('RGBA', 'LA'):
                                            img = img.convert('RGB')
                                        img.save(output_buffer, format='JPEG', quality=quality, optimize=True)
                                        
                                        # Actualizar objeto
                                        obj._data = output_buffer.getvalue()
                                        obj['/Length'] = len(output_buffer.getvalue())
                                        obj['/Filter'] = '/DCTDecode'
                                        obj['/Width'] = img.width
                                        obj['/Height'] = img.height
                                        obj['/BitsPerComponent'] = 8
                                        obj['/ColorSpace'] = '/DeviceRGB'
                                        
                                except Exception as img_error:
                                    page.open(show_snackbar(content=f"Error al procesar imagen en página {page_num + 1}: {img_error}", type="error"))
                                    continue
                    
                    writer.add_page(pdf_page)
                
                # Aplicar compresión adicional
                for pdf_page in writer.pages:
                    try:
                        pdf_page.compress_content_streams()
                    except:
                        pass
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                # Verificar compresión
                original_size = os.path.getsize(input_path)
                compressed_size = os.path.getsize(output_path)
                reduction = ((original_size - compressed_size) / original_size) * 100
                
                # Guardar resultado para mostrar en UI
                compression_results.append({
                    'name': file.name,
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'reduction': reduction
                })
                
                compressed_count += 1

            except Exception as e:
                print(f"Error al comprimir {file.name}: {e}")
                failed_count += 1

        if compressed_count > 0:
            page.open(show_snackbar(content=f"¡Compresión completada! \n archivos guardados en {output_dir}", type="success"))
            progress.visible = False
            
            # Mostrar resultados detallados
            results_container.controls.clear()
            
            for i, result in enumerate(compression_results):
                original_mb = result['original_size'] / (1024*1024)
                compressed_mb = result['compressed_size'] / (1024*1024)
                
                results_container.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content= ft.Row(
                                controls=[
                                    ft.Text(f"{i+1}", weight=ft.FontWeight.BOLD, size=16),
                                    ft.Column(
                                        controls=[
                                            ft.Text(result['name'], size=16, weight=ft.FontWeight.BOLD),
                                            ft.Row([
                                                ft.Text(f"Original: {original_mb:.2f} MB", size=12, color=ft.Colors.GREY_600),
                                                ft.Text(f"Comprimido: {compressed_mb:.2f} MB", size=12, color=ft.Colors.GREY_600)
                                            ])
                                        ],
                                        spacing=2,
                                        expand=True
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                    f"{result['reduction']:.1f}%",
                                                    size=14,
                                                    color=ft.Colors.GREEN,
                                                    weight=ft.FontWeight.BOLD,
                                                    text_align=ft.TextAlign.CENTER
                                            ),
                                            ft.Text(
                                                "Reducción",
                                                size=12,
                                                color=ft.Colors.GREY_600
                                            )
                                        ]
                                    ),
                                ]),
                                padding=10
                            ),
                        )
                    )
            
            results_container.visible = True
            
            # Abrir la carpeta de salida
            open_output_folder_button.visible = True
            open_output_folder_button.on_click = lambda _: page.launch_url(f"file:///{output_dir}")
            status_text.value = f"¡Compresión completada!"
        else:
            page.open(show_snackbar(content=f"No se pudo comprimir ningún PDF. Errores: {failed_count}", type="error"))
            progress.visible = False
            open_output_folder_button.visible = False
            results_container.visible = False
        
        page.update()
    
    pick_files_button = action_button(
        text= "Seleccionar PDF",
        icon=ft.Icons.FOLDER_OPEN,
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=True,
            allowed_extensions=["pdf"]
        )
    )
    
    # Mostrar mensaje inicial
    update_pdf_list()
    
    first_step = ft.Row(
        controls= [
            pick_files_button,
            compression_level,
            compress_button
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )
    
    container_lists = ft.Row(
        controls=[
                ft.Container(
                    content=pdf_list,
                    padding=10,
                    expand=True
                ),
                ft.VerticalDivider(),
                ft.Container(
                    content=results_container,
                    expand=True
                ),
        ],
        width=1000,
        spacing=10,
    )
    
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
                container_lists  
            ], 
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(height=50)
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )