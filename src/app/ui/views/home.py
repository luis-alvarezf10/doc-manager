# src/app/ui/views/home.py

import flet as ft
from src.app.ui.views.functions import functions_page
from src.app.ui.views.folder_view import folder_view
from src.app.ui.views.bcv_view import create_bcv_view
from src.app.ui.views.reports_view import create_reports_view
from src.app.utils.colors import dark_grey

class HomeView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.route = "/home"
        self.page = page
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.last_selected_index = 0

        self.content_area = ft.Column(
            controls=[], 
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )

        # Inicializa la primera vista
        self.functions_view = functions_page(self.page, self.change_content)
        self.content_area.controls.append(self.functions_view)

        # Diccionario de vistas perezosas
        self.views = {
            0: lambda: self.get_or_create("functions_view", lambda: functions_page(self.page, self.change_content)),
            1: lambda: self.create_folder_view(),
            2: lambda: self.get_or_create("lan_chat_view", self.init_chat_view),
            3: lambda: self.get_or_create("bcv_view", lambda: create_bcv_view(self.page)),
            4: lambda: self.get_or_create("reports_view", lambda: create_reports_view(self.page)),
        }

        self.navigation_menu = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            leading=ft.Column([
                ft.IconButton(
                    ft.Icons.DEHAZE,
                    icon_color=dark_grey,
                    on_click=lambda e: (
                        setattr(self.navigation_menu, 'extended', not self.navigation_menu.extended),
                        self.page.update()
                    )
                ),
                ft.Text("PLAF", size=25, weight=ft.FontWeight.BOLD, color=dark_grey)
            ]),
            group_alignment=-0.9,
            destinations=[
                *[
                    ft.NavigationRailDestination(icon=icon, selected_icon=selected, label=label)
                    for icon, selected, label in [
                        (ft.Icons.LIBRARY_BOOKS_OUTLINED, ft.Icons.LIBRARY_BOOKS, "Documentos"),
                        (ft.Icons.FOLDER_OUTLINED, ft.Icons.FOLDER, "Carpeta"),
                        (ft.Icons.CHAT_OUTLINED, ft.Icons.CHAT, "Chat LAN"),
                        (ft.Icons.MONETIZATION_ON, ft.Icons.MONETIZATION_ON, "Cambio BCV"),
                        (ft.Icons.FEEDBACK_OUTLINED, ft.Icons.FEEDBACK, "Reportes"),
                    ]
                ]
            ],
            on_change=self.on_navigation_change
        )

        self.controls = [
            ft.Row([
                self.navigation_menu,
                ft.VerticalDivider(width=1),
                self.content_area
            ], expand=True)
        ]

    # 🧠 Reutiliza o crea y guarda la vista si no existe
    def get_or_create(self, attr_name, creator):
        if not hasattr(self, attr_name) or getattr(self, attr_name) is None:
            setattr(self, attr_name, creator())
        return getattr(self, attr_name)

    def init_chat_view(self):
        from src.app.ui.views.lan_chat_view import LANChatView
        self.lan_chat_instance = LANChatView(self.page)
        return self.lan_chat_instance.create_view()

    def create_folder_view(self):
        chat_instance = getattr(self, "lan_chat_instance", None)
        self.folder_view_instance = folder_view(self.page, None, chat_instance)
        return self.folder_view_instance

    def on_navigation_change(self, e):
        self.content_area.controls.clear()
        view_creator = self.views.get(e.control.selected_index)
        if view_creator:
            self.content_area.controls.append(view_creator())
        self.page.update()

    def change_content(self, new_content):
        self.content_area.controls.clear()
        self.content_area.controls.append(new_content)
        self.page.update()
