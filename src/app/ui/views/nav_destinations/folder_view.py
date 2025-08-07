import flet as ft
import os
from src.utils.colors import *
from src.app.ui.widgets.action_button import action_button
from src.app.ui.widgets.show_snackbar import show_snackbar
from src.app.ui.widgets.email_form import email_form

try:
    from docx2pdf import convert as docx_convert  # type: ignore
except ImportError:
    docx_convert = None

def folder_view(page: ft.Page, chat_instance=None):
    documents_path = os.path.join(os.path.expanduser("~"), "Documents")
    axiology_path = os.path.join(documents_path, "Axiology Document Manager")
    current_path = axiology_path
    folders_list = ft.Column()
    status_text = ft.Text("", size=14, weight="bold")
    path_text = ft.Text("", size=12, color="grey")

    selection_mode = False
    selected_files = set()
    file_checkboxes = {}

    def update_status(msg, color="blue"):
        status_text.value = msg
        status_text.color = color
        page.update()

    def create_plaf_system():
        try:
            os.makedirs(axiology_path, exist_ok=True)
            return True
        except Exception as ex:
            update_status(f"Error al crear PLAF_system: {ex}", "red")
            return False

    def navigate_to(folder=None):
        nonlocal current_path
        current_path = os.path.join(current_path, folder) if folder else os.path.dirname(current_path)
        scan_folders()

    def open_path(path, is_file=False):
        try:
            os.startfile(path)
            name = os.path.basename(path)
            msg = f"Abriendo archivo: {name}" if is_file else f"Abriendo: {name}"
            page.open(show_snackbar(content=msg, type="success"))
        except Exception as ex:
            msg = f"Error al abrir: {ex}"
            page.open(show_snackbar(content=msg, type="success"))

    def send_selected_files(_):
        if not selected_files:
            page.open(show_snackbar(content="No hay archivos seleccionados", type="error"))
            return
        
        file_paths = list(selected_files)
        file_names = [os.path.basename(path) for path in file_paths]
        form_email = email_form(page, file_paths, file_names)
        page.open(form_email)
    
    def convert_to_pdf(_):
        if not selected_files:
            page.open(show_snackbar(content="No hay archivos seleccionados", type="error"))
            return
        
        # Filtrar solo archivos DOCX
        docx_files = [f for f in selected_files if f.lower().endswith(('.docx', '.doc'))]
        
        if not docx_files:
            page.open(show_snackbar(content="No hay archivos DOCX seleccionados", type="error"))
            return
        
        if docx_convert is None:
            page.open(show_snackbar(content="Instala docx2pdf: pip install docx2pdf", type="error"))
            return
        
        try:
            
            # Crear carpeta de salida
            desktop_path = os.path.join(os.path.expanduser("~"), "Documents")
            manager_path = os.path.join(desktop_path, "Axiology Document Manager")
            output_dir = os.path.join(manager_path, "PDFs Convertidos")
            os.makedirs(output_dir, exist_ok=True)
            
            converted_count = 0
            for docx_path in docx_files:
                try:
                    file_name = os.path.splitext(os.path.basename(docx_path))[0]
                    pdf_path = os.path.join(output_dir, f"{file_name}.pdf")
                    
                    # Evitar sobrescritura
                    cont = 1
                    while os.path.exists(pdf_path):
                        pdf_path = os.path.join(output_dir, f"{file_name} ({cont}).pdf")
                        cont += 1
                    
                    docx_convert(docx_path, pdf_path)
                    converted_count += 1
                    
                except Exception as ex:
                    page.open(show_snackbar(content=f"Error convirtiendo {os.path.basename(docx_path)}: {ex}", type="error"))
            
            if converted_count > 0:
                page.open(show_snackbar(content=f"{converted_count} archivos convertidos a PDF", type="success"))
                selected_files.clear()
                toggle_selection_mode(None)
                scan_folders()
            

        except Exception as ex:
            page.open(show_snackbar(content=f"Error: {ex}", type="error"))
    
    def delete_selected_files(_):
        if not selected_files:
            page.open(show_snackbar(content="No hay archivos seleccionados", type="error"))
            return
        
        def confirm_delete(e):
            try:
                deleted_count = 0
                for file_path in selected_files:
                    os.remove(file_path)
                    deleted_count += 1
                
                page.open(show_snackbar(content=f"{deleted_count} archivos eliminados", type="success"))
                selected_files.clear()
                toggle_selection_mode(None)  
                scan_folders()
                page.close(confirm_dialog)
            except Exception as ex:
                page.open(show_snackbar(content=f"Error al eliminar: {ex}", type="error"))
        
        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Estás seguro de eliminar {len(selected_files)} archivos?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.close(confirm_dialog)),
                ft.ElevatedButton("Eliminar", bgcolor="red", color="white", on_click=confirm_delete)
            ]
        )
        page.open(confirm_dialog)
    
    def toggle_selection_mode(_):
        nonlocal selection_mode
        selection_mode = not selection_mode
        selected_files.clear()

        for c in file_checkboxes.values():
            c.visible = selection_mode
            c.value = False

        select_btn.text = "Cancelar Selección" if selection_mode else "Seleccionar Archivos"
        select_btn.bgcolor = "red" if selection_mode else "purple"
        
        send_multiple_btn.visible = selection_mode
        convert_btn.visible = selection_mode
        delete_multiple_btn.visible = selection_mode

        scan_folders()

    def toggle_file_selection(path, selected):
        if selected: selected_files.add(path)
        else: selected_files.discard(path)
        update_status(f"Archivos seleccionados: {len(selected_files)}")

    # def send_selected_files(_):
    #     if not selected_files:
    #         return update_status("No hay archivos seleccionados", "red")
    #     if not chat_instance:
    #         return update_status("Chat no disponible", "red")
    #     if not getattr(chat_instance, "is_connected", False):
    #         return update_status("No hay conexión de chat activa", "red")

    #     for i, path in enumerate(selected_files, 1):
    #         try:
    #             chat_instance.send_file_direct(path)
    #             update_status(f"Enviando {i}/{len(selected_files)}...", "green")
    #         except Exception as ex:
    #             return update_status(f"Error enviando {os.path.basename(path)}: {ex}", "red")

    #     update_status(f"✅ Enviados {len(selected_files)} archivos")
    #     selected_files.clear()
    #     toggle_selection_mode(None)

    def make_file_icon(name):
        if name.endswith(('.doc', '.docx')): return ft.Icons.DESCRIPTION
        if name.endswith('.pdf'): return ft.Icons.PICTURE_AS_PDF
        if name.endswith(('.xls', '.xlsx')): return ft.Icons.TABLE_VIEW
        return ft.Icons.DESCRIPTION
    
    def make_file_color(name):
        if name.endswith(('.doc', '.docx')): return "blue"
        if name.endswith('.pdf'): return "red"
        if name.endswith(('.xls', '.xlsx')): return "green"
        return "black"
    
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
    
    def get_file_date(file_path):
        try:
            import datetime
            timestamp = os.path.getmtime(file_path)
            date = datetime.datetime.fromtimestamp(timestamp)
            return date.strftime("%d/%m/%Y %H:%M")
        except:
            return "?"

    def make_folder_card(name):
        return ft.Card(
            content=ft.Container(
                ft.Row([
                    ft.Icon(ft.Icons.FOLDER, color="orange"),
                    ft.Text(name, size=16, expand=True, weight="bold"),
                    ft.IconButton(
                        icon=ft.Icons.OPEN_IN_NEW,
                        tooltip="Abrir en explorador",
                        on_click=lambda e: open_path(os.path.join(current_path, name))
                    )
                ]),
                padding=15,
                on_click=lambda e: navigate_to(name)
            )
        )

    def make_file_card(name):
        path = os.path.join(current_path, name)
        checkbox = ft.Checkbox(
            value=path in selected_files,
            visible=selection_mode,
            on_change=lambda e: toggle_file_selection(path, e.control.value)
        )
        file_checkboxes[path] = checkbox
        
        def show_context_menu(e):
            def close_menu():
                page.close(context_menu)
            
            def send_file():
                close_menu()
                form_email = email_form(page, path, name)
                page.open(form_email)
                return
                
              
            
            def rename_file():
                close_menu()
                
                # Separar nombre y extensión
                file_name, file_ext = os.path.splitext(name)
                
                def do_rename(e):
                    new_name = rename_field.value.strip()
                    if not new_name:
                        page.open(show_snackbar(content="El nombre no puede estar vacío", type="error"))
                        return
                    
                    try:
                        # Agregar la extensión original
                        full_new_name = new_name + file_ext
                        new_path = os.path.join(current_path, full_new_name)
                        os.rename(path, new_path)
                        page.open(show_snackbar(content=f"Archivo renombrado a {full_new_name}", type="success"))
                        page.close(rename_dialog)
                        scan_folders()
                    except Exception as ex:
                        page.open(show_snackbar(content=f"Error al renombrar: {ex}", type="error"))
                
                rename_field = ft.TextField(
                    label=f"Nuevo nombre",
                    value=file_name,
                    filled=True,
                    expand=True,
                    border_radius=8,
                    border_width=0,
                    border_color="transparent",
                    focused_border_width=0,
                    text_size=16,
                    width=300
                )
                
                rename_dialog = ft.AlertDialog(
                    title= ft.Row([
                        ft.Text("Renombrar archivo"),
                        ft.IconButton(icon=ft.Icons.CLOSE, icon_color="grey", on_click=lambda _: page.close(rename_dialog)),
                        ],
                        alignment = ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    content=rename_field,
                    actions= [action_button(text="Renombrar",icon=ft.Icons.DRIVE_FILE_RENAME_OUTLINE, on_click=do_rename, width=150, height=35)],
                    shape=ft.RoundedRectangleBorder(radius=10),
                    elevation=8,  
                )
                page.open(rename_dialog)
            
            def convert_single_file():
                close_menu()
                if not name.lower().endswith(('.docx', '.doc')):
                    page.open(show_snackbar(content="Solo se pueden convertir archivos DOCX", type="error"))
                    return
                
                if docx_convert is None:
                    page.open(show_snackbar(content="Instala docx2pdf: pip install docx2pdf", type="error"))
                    return
                
                try:
                    # Crear carpeta de salida
                    desktop_path = os.path.join(os.path.expanduser("~"), "Documents")
                    manager_path = os.path.join(desktop_path, "Axiology Document Manager")
                    output_dir = os.path.join(manager_path, "PDFs Convertidos")
                    os.makedirs(output_dir, exist_ok=True)
                    
                    file_name = os.path.splitext(name)[0]
                    pdf_path = os.path.join(output_dir, f"{file_name}.pdf")
                    
                    # Evitar sobrescritura
                    cont = 1
                    while os.path.exists(pdf_path):
                        pdf_path = os.path.join(output_dir, f"{file_name} ({cont}).pdf")
                        cont += 1
                    
                    docx_convert(path, pdf_path)
                    page.open(show_snackbar(content=f"Archivo convertido a PDF: {os.path.basename(pdf_path)}", type="success"))
                    scan_folders()
                    
                except Exception as ex:
                    page.open(show_snackbar(content=f"Error al convertir: {ex}", type="error"))
            
            def delete_file():
                close_menu()
                try:
                    os.remove(path)
                    page.open(show_snackbar(content=f"Archivo {name} eliminado", type="success"))
                    scan_folders()
                except Exception as ex:
                    page.open(show_snackbar(content=f"Error al eliminar: {ex}", type="error"))
            
            context_menu = ft.AlertDialog(
                title= ft.Row([
                    ft.Text(f"Opciones: {name[:20]}{'...' if len(name) > 20 else ''}", size=14, weight="bold"),
                    ft.IconButton(icon=ft.Icons.CLOSE, icon_color="grey", on_click=lambda _: close_menu())
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.SEND),
                        title=ft.Text("Enviar"),
                        on_click=lambda _: send_file()
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.EDIT),
                        title=ft.Text("Cambiar nombre"),
                        on_click=lambda _: rename_file()
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.PICTURE_AS_PDF),
                        title=ft.Text("Covertir a PDF"),
                        on_click=lambda _: convert_single_file()
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.DELETE),
                        title=ft.Text("Eliminar"),
                        on_click=lambda _: delete_file()
                    ),
                ], 
                tight=True,
                width=250,
                ),
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=8,
            )
            page.open(context_menu)
        
        return ft.Card(
            content=ft.GestureDetector(
                content=ft.Container(
                    ft.Row([
                        checkbox,
                        ft.Icon(make_file_icon(name), color= make_file_color(name)),
                        ft.Column([
                            ft.Text(name, size=16, weight="bold"),
                            ft.Text(f"{get_file_size(path)} • {get_file_date(path)} ", size=12, color=ft.Colors.GREY_600)
                        ], expand=True, spacing=2),
                    ]),
                    padding=15
                ),
                on_tap=lambda e: open_path(path, True),
                on_secondary_tap=show_context_menu,
                mouse_cursor=ft.MouseCursor.CLICK
            )
        )

    def scan_folders():
        folders_list.controls.clear()
        if not os.path.exists(current_path) and not create_plaf_system():
            return

        path_text.value = f"Ruta: {current_path}"
        if current_path != axiology_path:
            folders_list.controls.append(ft.Card(
                content=ft.Container(
                    ft.Row([ft.Icon(ft.Icons.ARROW_BACK, color="blue"), ft.Text(f".. (volver)", size=16, weight=ft.FontWeight.BOLD)]),
                    padding=15,
                    on_click=lambda e: navigate_to()
                )
            ))

        try:
            items = os.listdir(current_path)
            folders = sorted([f for f in items if os.path.isdir(os.path.join(current_path, f))])
            files = sorted([f for f in items if os.path.isfile(os.path.join(current_path, f))])

            folders_list.controls.extend([make_folder_card(f) for f in folders])
            folders_list.controls.extend([make_file_card(f) for f in files])

            if not folders and not files:
                folders_list.controls.append(
                    ft.Container(ft.Text("Esta carpeta está vacía", size=16, color="grey"),
                                 alignment=ft.alignment.center, padding=20)
                )

            update_status(f"Carpetas: {len(folders)} | Archivos: {len(files)}")
        except Exception as ex:
            update_status(f"Error al escanear carpetas: {ex}", "red")


    refresh_btn = ft.IconButton(tooltip="Actualizar", on_click=lambda e: scan_folders(), bgcolor="blue", icon=ft.Icons.REFRESH, icon_color="white")
    open_folder_btn = action_button(text="Abrir carpeta",on_click= lambda e: open_path(axiology_path), bgcolor="green", icon=ft.Icons.FOLDER_OPEN)
    select_btn = action_button(text="Seleccionar Archivos", on_click=toggle_selection_mode, bgcolor="purple", icon=ft.Icons.CHECK_BOX)
    send_multiple_btn = ft.IconButton(tooltip="Enviar por correo", icon=ft.Icons.EMAIL, bgcolor="orange", icon_color="white", on_click=send_selected_files, visible=False)
    convert_btn = ft.IconButton(tooltip="Convertir DOCX a PDF", icon=ft.Icons.PICTURE_AS_PDF, bgcolor="blue", icon_color="white", on_click=convert_to_pdf, visible=False)
    delete_multiple_btn = ft.IconButton(tooltip="Eliminar", icon=ft.Icons.DELETE, bgcolor="red", icon_color="white", on_click=delete_selected_files, visible=False)
    scan_folders()

    return ft.Column(
        controls=[
            ft.Column([
                ft.Container(height=20),
                ft.Text("Explorador de Archivos", size=25, weight=ft.FontWeight.BOLD),
                path_text, 
                ft.Divider(),
                ft.Row([
                    open_folder_btn, 
                    select_btn,
                    send_multiple_btn,
                    delete_multiple_btn
                    ], 
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER
                    ),
                ft.Row([
                    ft.Row([
                        refresh_btn, 
                        status_text,                
                    ]),
                    ft.Row([
                        convert_btn,
                        send_multiple_btn,
                        delete_multiple_btn        
                        ],
                    )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    width=1000,
                    height=50
                ),
                ft.Container(content=ft.Column([folders_list]), width=1000),
            ], 
            spacing=15, 
            scroll=ft.ScrollMode.AUTO, 
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        ],
        expand=True
    )
