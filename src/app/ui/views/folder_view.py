import flet as ft
import os
from src.app.utils.colors import *
from src.app.ui.widgets.custom_app_bar import custom_app_bar

def folder_view(page: ft.Page, back_callback=None, chat_instance=None):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    plaf_system_path = os.path.join(desktop_path, "PLAF_system")
    current_path = plaf_system_path
    folders_list = ft.Column()
    status_text = ft.Text("", size=14)
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
            os.makedirs(plaf_system_path, exist_ok=True)
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
            update_status(msg, "green")
        except Exception as ex:
            update_status(f"Error al abrir: {ex}", "red")

    def toggle_selection_mode(_):
        nonlocal selection_mode
        selection_mode = not selection_mode
        selected_files.clear()

        for c in file_checkboxes.values():
            c.visible = selection_mode
            c.value = False

        select_btn.text = "Cancelar Selección" if selection_mode else "Seleccionar Archivos"
        select_btn.bgcolor = "red" if selection_mode else "purple"

        if chat_instance:
            connected = getattr(chat_instance, "is_connected", False)
            send_btn.visible = selection_mode
            send_btn.text = "Enviar por Chat ✅" if connected else "Chat Desconectado ❌"
            send_btn.bgcolor = "orange" if connected else "grey"

        scan_folders()

    def toggle_file_selection(path, selected):
        if selected: selected_files.add(path)
        else: selected_files.discard(path)
        update_status(f"Archivos seleccionados: {len(selected_files)}")

    def send_selected_files(_):
        if not selected_files:
            return update_status("No hay archivos seleccionados", "red")
        if not chat_instance:
            return update_status("Chat no disponible", "red")
        if not getattr(chat_instance, "is_connected", False):
            return update_status("No hay conexión de chat activa", "red")

        for i, path in enumerate(selected_files, 1):
            try:
                chat_instance.send_file_direct(path)
                update_status(f"Enviando {i}/{len(selected_files)}...", "green")
            except Exception as ex:
                return update_status(f"Error enviando {os.path.basename(path)}: {ex}", "red")

        update_status(f"✅ Enviados {len(selected_files)} archivos")
        selected_files.clear()
        toggle_selection_mode(None)

    def make_file_icon(name):
        if name.endswith('.pdf'): return ft.Icons.PICTURE_AS_PDF
        if name.endswith(('.xls', '.xlsx')): return ft.Icons.TABLE_VIEW
        return ft.Icons.DESCRIPTION

    def make_folder_card(name):
        return ft.Card(
            content=ft.Container(
                ft.Row([
                    ft.Icon(ft.Icons.FOLDER, color="orange"),
                    ft.Text(name, size=16, expand=True),
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
        return ft.Card(
            content=ft.Container(
                ft.Row([
                    checkbox,
                    ft.Icon(make_file_icon(name), color="green"),
                    ft.Text(name, size=14, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.OPEN_IN_NEW,
                        tooltip="Abrir archivo",
                        on_click=lambda e: open_path(path, True)
                    )
                ]),
                padding=10
            )
        )

    def scan_folders():
        folders_list.controls.clear()
        if not os.path.exists(current_path) and not create_plaf_system():
            return

        path_text.value = f"Ruta: {current_path}"
        if current_path != plaf_system_path:
            folders_list.controls.append(ft.Card(
                content=ft.Container(
                    ft.Row([ft.Icon(ft.Icons.ARROW_BACK, color="blue"), ft.Text(".. (Volver)", size=16, weight=ft.FontWeight.BOLD)]),
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

    refresh_btn = ft.ElevatedButton("Actualizar", bgcolor="blue", color="white", icon=ft.Icons.REFRESH, on_click=lambda e: scan_folders())
    open_system_btn = ft.ElevatedButton("Abrir PLAF System", bgcolor="green", color="white", icon=ft.Icons.FOLDER_OPEN, on_click=lambda e: open_path(plaf_system_path))
    select_btn = ft.ElevatedButton("Seleccionar Archivos", bgcolor="purple", color="white", icon=ft.Icons.CHECK_BOX, on_click=toggle_selection_mode)
    send_btn = ft.ElevatedButton("Enviar por Chat", bgcolor="orange", color="white", icon=ft.Icons.SEND, on_click=send_selected_files, visible=False)

    scan_folders()

    return ft.Column(
        controls=[
            ft.Column([
                ft.Text("Explorador de Archivos PLAF System", size=24, weight=ft.FontWeight.BOLD),
                path_text,
                ft.Divider(),
                ft.Row([refresh_btn, open_system_btn, select_btn, send_btn], spacing=10),
                ft.Column([folders_list], height=400, scroll=ft.ScrollMode.AUTO),
                status_text
            ], spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
        ],
        expand=True
    )
