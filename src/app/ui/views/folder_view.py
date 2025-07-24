import flet as ft
from src.app.utils.colors import *
from src.app.ui.widgets.custom_app_bar import custom_app_bar
import os
import subprocess

def folder_view(page: ft.Page, back_callback=None, chat_instance=None):
    def handle_close(e):
        if back_callback:
            back_callback()
    
    app_bar = custom_app_bar(
        text="Explorador PLAF System",
        on_click=handle_close
    )
    
    # Ruta base del sistema
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    plaf_system_path = os.path.join(desktop_path, "PLAF_system")
    
    current_path = plaf_system_path
    folders_list = ft.Column()
    status_text = ft.Text("", size=14)
    path_text = ft.Text("", size=12, color="grey")
    
    # Variables para selección múltiple
    selection_mode = False
    selected_files = set()
    file_checkboxes = {}
    
    def create_plaf_system():
        """Crear la estructura de carpetas PLAF_system si no existe"""
        try:
            os.makedirs(plaf_system_path, exist_ok=True)
            return True
        except Exception as ex:
            status_text.value = f"Error al crear PLAF_system: {str(ex)}"
            status_text.color = "red"
            return False
    
    def scan_folders():
        """Escanear carpetas en la ruta actual"""
        folders_list.controls.clear()
        
        if not os.path.exists(current_path):
            if not create_plaf_system():
                page.update()
                return
        
        try:
            path_text.value = f"Ruta: {current_path}"
            
            # Botón para volver atrás si no estamos en la raíz
            if current_path != plaf_system_path:
                back_btn = ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ARROW_BACK, color="blue"),
                            ft.Text(".. (Volver)", size=16, weight=ft.FontWeight.BOLD)
                        ]),
                        padding=15,
                        on_click=lambda e: navigate_back()
                    )
                )
                folders_list.controls.append(back_btn)
            
            # Listar carpetas
            items = os.listdir(current_path)
            folders = [item for item in items if os.path.isdir(os.path.join(current_path, item))]
            files = [item for item in items if os.path.isfile(os.path.join(current_path, item))]
            
            # Mostrar carpetas
            for folder in sorted(folders):
                folder_card = ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.FOLDER, color="orange"),
                            ft.Text(folder, size=16, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.OPEN_IN_NEW,
                                tooltip="Abrir en explorador",
                                on_click=lambda e, path=os.path.join(current_path, folder): open_in_explorer(path)
                            )
                        ]),
                        padding=15,
                        on_click=lambda e, folder_name=folder: navigate_to_folder(folder_name)
                    )
                )
                folders_list.controls.append(folder_card)
            
            # Mostrar archivos
            for file in sorted(files):
                file_icon = ft.Icons.DESCRIPTION
                if file.endswith('.pdf'):
                    file_icon = ft.Icons.PICTURE_AS_PDF
                elif file.endswith(('.xlsx', '.xls')):
                    file_icon = ft.Icons.TABLE_VIEW
                elif file.endswith(('.docx', '.doc')):
                    file_icon = ft.Icons.DESCRIPTION
                
                file_path = os.path.join(current_path, file)
                
                # Checkbox para selección (solo visible en modo selección)
                checkbox = ft.Checkbox(
                    value=file_path in selected_files,
                    on_change=lambda e, path=file_path: toggle_file_selection(path, e.control.value),
                    visible=selection_mode
                )
                file_checkboxes[file_path] = checkbox
                
                file_card = ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            checkbox,
                            ft.Icon(file_icon, color="green"),
                            ft.Text(file, size=14, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.OPEN_IN_NEW,
                                tooltip="Abrir archivo",
                                on_click=lambda e, file_path=file_path: open_file(file_path)
                            )
                        ]),
                        padding=10
                    )
                )
                folders_list.controls.append(file_card)
            
            if not folders and not files:
                folders_list.controls.append(
                    ft.Container(
                        content=ft.Text("Esta carpeta está vacía", size=16, color="grey"),
                        alignment=ft.alignment.center,
                        padding=20
                    )
                )
            
            status_text.value = f"Carpetas: {len(folders)} | Archivos: {len(files)}"
            status_text.color = "blue"
            
        except Exception as ex:
            status_text.value = f"Error al escanear carpetas: {str(ex)}"
            status_text.color = "red"
        
        page.update()
    
    def navigate_to_folder(folder_name):
        nonlocal current_path
        current_path = os.path.join(current_path, folder_name)
        scan_folders()
    
    def navigate_back():
        nonlocal current_path
        current_path = os.path.dirname(current_path)
        scan_folders()
    
    def open_in_explorer(path):
        try:
            os.startfile(path)
            status_text.value = f"Abriendo: {os.path.basename(path)}"
            status_text.color = "green"
        except Exception as ex:
            status_text.value = f"Error al abrir: {str(ex)}"
            status_text.color = "red"
        page.update()
    
    def open_file(file_path):
        try:
            os.startfile(file_path)
            status_text.value = f"Abriendo archivo: {os.path.basename(file_path)}"
            status_text.color = "green"
        except Exception as ex:
            status_text.value = f"Error al abrir archivo: {str(ex)}"
            status_text.color = "red"
        page.update()
    
    def refresh_folders(e):
        scan_folders()
    
    def open_plaf_system(e):
        open_in_explorer(plaf_system_path)
    
    def toggle_selection_mode(e):
        nonlocal selection_mode
        selection_mode = not selection_mode
        selected_files.clear()
        
        # Actualizar visibilidad de checkboxes
        for checkbox in file_checkboxes.values():
            checkbox.visible = selection_mode
            checkbox.value = False
        
        # Actualizar texto del botón
        select_btn.text = "Cancelar Selección" if selection_mode else "Seleccionar Archivos"
        select_btn.bgcolor = "red" if selection_mode else "purple"
        
        # Mostrar/ocultar botón de envío y actualizar estado
        chat_connected = chat_instance and hasattr(chat_instance, 'is_connected') and chat_instance.is_connected
        send_btn.visible = selection_mode and chat_instance is not None
        
        if selection_mode:
            if chat_connected:
                send_btn.text = "Enviar por Chat ✅"
                send_btn.bgcolor = "orange"
            else:
                send_btn.text = "Chat Desconectado ❌"
                send_btn.bgcolor = "grey"
        
        scan_folders()
    
    def toggle_file_selection(file_path, is_selected):
        if is_selected:
            selected_files.add(file_path)
        else:
            selected_files.discard(file_path)
        
        # Actualizar contador
        status_text.value = f"Archivos seleccionados: {len(selected_files)}"
        page.update()
    
    def send_selected_files(e):
        if not selected_files:
            status_text.value = "No hay archivos seleccionados"
            status_text.color = "red"
            page.update()
            return
        
        if not chat_instance:
            status_text.value = "Chat no disponible. Ve a Chat LAN primero."
            status_text.color = "red"
            page.update()
            return
            
        if not hasattr(chat_instance, 'is_connected') or not chat_instance.is_connected:
            status_text.value = "No hay conexión de chat activa"
            status_text.color = "red"
            page.update()
            return
        
        # Enviar archivos seleccionados
        sent_count = 0
        for file_path in selected_files:
            try:
                chat_instance.send_file_direct(file_path)
                sent_count += 1
                status_text.value = f"Enviando {sent_count}/{len(selected_files)}..."
                page.update()
            except Exception as ex:
                status_text.value = f"Error enviando {os.path.basename(file_path)}: {str(ex)}"
                status_text.color = "red"
                page.update()
                return
        
        status_text.value = f"✅ Enviados {sent_count} archivos por chat"
        status_text.color = "green"
        
        # Limpiar selección
        selected_files.clear()
        toggle_selection_mode(None)
        page.update()
    
    # Botones de acción
    refresh_btn = ft.ElevatedButton(
        text="Actualizar",
        bgcolor="blue",
        color="white",
        icon=ft.Icons.REFRESH,
        on_click=refresh_folders
    )
    
    open_system_btn = ft.ElevatedButton(
        text="Abrir PLAF System",
        bgcolor="green",
        color="white",
        icon=ft.Icons.FOLDER_OPEN,
        on_click=open_plaf_system
    )
    
    select_btn = ft.ElevatedButton(
        text="Seleccionar Archivos",
        bgcolor="purple",
        color="white",
        icon=ft.Icons.CHECK_BOX,
        on_click=toggle_selection_mode
    )
    
    send_btn = ft.ElevatedButton(
        text="Enviar por Chat",
        bgcolor="orange",
        color="white",
        icon=ft.Icons.SEND,
        on_click=send_selected_files,
        visible=False
    )
    
    # Inicializar
    scan_folders()
    
    return ft.Column(
        controls=[
            app_bar,
            ft.Column([
                ft.Text("Explorador de Archivos PLAF System", size=24, weight=ft.FontWeight.BOLD),
                path_text,
                ft.Divider(),
                
                ft.Row([
                    refresh_btn,
                    open_system_btn,
                    select_btn,
                    send_btn
                ], spacing=10),
                
                ft.Column([
                    folders_list
                ], height=400, scroll=ft.ScrollMode.AUTO),
                
                status_text
            ], spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
        ],
        expand=True
    )