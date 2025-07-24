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

from src.app.utils.colors import *
from src.app.ui.widgets.custom_app_bar import custom_app_bar

def compress_view(page: ft.Page, back_callback=None):
    def handle_close(e):
        if back_callback:
            back_callback()
    
    app_bar = custom_app_bar(
        text="Comprimir Documento",
        on_click=handle_close
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
                status_text.value = "Ningún archivo PDF válido seleccionado."
        else:
            status_text.value = "Selección de archivos cancelada."
        page.update()

    # Lista de archivos seleccionados
    selected_pdf_files = []
    
    # Definir elementos de UI
    pdf_list_container = ft.Column([], 
                                   spacing=5,
                                   scroll=ft.ScrollMode.AUTO,
                                   )
    preview_container = ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.UPLOAD_FILE, size=60, color=ft.Colors.GREY_400),
            ft.Text("Selecciona un PDF", size=12, text_align=ft.TextAlign.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=8,
        padding=10,
        width=200,
        height=150,
        alignment=ft.alignment.center
    )
    
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
        pdf_list_container.controls.clear()
        
        if not selected_pdf_files:
            pdf_list_container.controls.append(
                ft.Text("No hay archivos seleccionados", 
                        size=14, 
                        color=dark_grey)
            )
            compress_button.disabled = True
            preview_container.content = ft.Column([
                ft.Icon(ft.Icons.UPLOAD_FILE, 
                        size=60, 
                        color=ft.Colors.GREY_400),
                ft.Text("Selecciona un PDF", 
                        size=12, 
                        text_align=dark_grey)
            ], 
            alignment=ft.MainAxisAlignment.CENTER, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        else:
            for pdf_file in selected_pdf_files:
                file_size = get_file_size(pdf_file.path)
                file_row = ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PICTURE_AS_PDF, size=20, color=ft.Colors.RED_400),
                        ft.Column([
                            ft.Text(pdf_file.name, size=12, weight=ft.FontWeight.NORMAL),
                            ft.Text(file_size, size=10, color=ft.Colors.GREY_600)
                        ], spacing=2, expand=True),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            icon_color=ft.Colors.RED,
                            on_click=lambda e, file=pdf_file: remove_pdf_from_list(file),
                            tooltip="Eliminar archivo"
                        )
                    ], 
                    spacing=5
                    ),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=4,
                    bgcolor=ft.Colors.GREY_50
                )
                pdf_list_container.controls.append(file_row)
            
            compress_button.disabled = False
            compress_button.on_click = lambda _: compress_pdfs(selected_pdf_files)
            
            # Actualizar preview
            file_info = ft.Column([
                ft.Icon(ft.Icons.PICTURE_AS_PDF, size=80, color=ft.Colors.RED_400),
                ft.Text(f"PDFs seleccionados", size=14, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Text(f"{len(selected_pdf_files)} archivo(s)", size=12, text_align=ft.TextAlign.CENTER)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            preview_container.content = file_info
    status_text = ft.Text("", size=14)
    
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
        width=300,
        border_radius=20,
        border_color=blue,
        text_size=12
    )
    
    results_container = ft.Column([], visible=False, spacing=5, scroll=ft.ScrollMode.AUTO)
    compress_button = ft.ElevatedButton(
        text="Comprimir PDFs",
        bgcolor=blue,
        color=white,
        disabled=True
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

        # Guardar en PLAF_system
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        plaf_system_path = os.path.join(desktop_path, "PLAF_system")
        output_dir = os.path.join(plaf_system_path, "PDFs_comprimidos")
        os.makedirs(output_dir, exist_ok=True)

        compressed_count = 0
        failed_count = 0
        compression_results = []
        
        for file in files:
            input_path = file.path
            file_name_without_ext = os.path.splitext(file.name)[0]
            output_path = os.path.join(output_dir, f"{file_name_without_ext}_compressed.pdf")

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
                                    print(f"Error procesando imagen en página {page_num + 1}: {img_error}")
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
            status_text.value = (
                f"¡Compresión completada! Se comprimieron {compressed_count} PDF(s)."
                f" Los archivos guardados en: {output_dir}"
            )
            status_text.color = ft.Colors.GREEN_800
            progress.visible = False
            
            # Mostrar resultados detallados
            results_container.controls.clear()
            results_container.controls.append(
                ft.Text("Resultados de compresión:", 
                        size=14, 
                        weight=ft.FontWeight.BOLD,
                        color=dark_grey)
            )
            
            for result in compression_results:
                original_mb = result['original_size'] / (1024*1024)
                compressed_mb = result['compressed_size'] / (1024*1024)
                
                result_row = ft.Container(
                    content=ft.Column([
                        ft.Text(result['name'], size=12, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Text(f"Original: {original_mb:.2f} MB", size=10),
                            ft.Text(f"Comprimido: {compressed_mb:.2f} MB", size=10),
                            ft.Text(f"Reducción: {result['reduction']:.1f}%", 
                                   size=10, 
                                   color=ft.Colors.GREEN_600 if result['reduction'] > 0 else ft.Colors.ORANGE_600)
                        ], spacing=15)
                    ], spacing=2),
                    padding=ft.padding.all(8),
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=4,
                    bgcolor=ft.Colors.GREEN_50
                )
                results_container.controls.append(result_row)
            
            results_container.visible = True
            
            # Abrir la carpeta de salida
            open_output_folder_button.visible = True
            open_output_folder_button.on_click = lambda _: page.launch_url(f"file:///{output_dir}")
        else:
            status_text.value = f"No se pudo comprimir ningún PDF. Errores: {failed_count}"
            status_text.color = ft.Colors.RED_800
            progress.visible = False
            open_output_folder_button.visible = False
            results_container.visible = False
        
        page.update()
    
    pick_files_button = ft.ElevatedButton(
        text="Seleccionar PDFs",
        bgcolor=blue,
        color=white,
        icon=ft.Icons.UPLOAD_FILE,
        on_click=lambda e: file_picker.pick_files(
            allow_multiple=True,
            allowed_extensions=["pdf"]
        )
    )
    
    return ft.Column(
        controls=[
            app_bar,
            ft.Container(
                content=ft.Column([
                    ft.Text("Comprimir Documentos PDF", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    pick_files_button,
                    ft.Row([
                        ft.Column([
                            ft.Text("Archivos seleccionados:", size=16, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Column([
                                    pdf_list_container
                                ], scroll=ft.ScrollMode.AUTO),
                                height=200,
                                border=ft.border.all(1, ft.Colors.GREY_300),
                                border_radius=8,
                                padding=10
                            ),
                            compression_level,
                            compress_button,
                            ft.Row([
                                status_text,
                                progress
                            ], spacing=10),
                            ft.Container(
                                content=results_container,
                                height=150
                            ),
                            open_output_folder_button
                        ], expand=True),
                        preview_container
                    ], spacing=20)
                ], 
                spacing=20, 
                scroll=ft.ScrollMode.AUTO),
                padding=20,
                expand=True
            )
        ],
        expand=True
    )