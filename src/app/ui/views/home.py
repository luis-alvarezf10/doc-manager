# src/app/ui/views/home.py

import flet as ft
from src.app.ui.views.functions import functions_page
from src.app.ui.views.folder_view import folder_view
from src.app.ui.views.bcv_view import create_bcv_view
from src.app.ui.views.reports_view import create_reports_view
from src.utils.colors import grey

class HomeView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.route = "/home"
        self.page = page
        self.padding = 0
        self.margin = 0
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

        self.is_dark = self.page.platform_brightness == ft.Brightness.DARK
        
        self.dark_mode_switch = ft.Switch(on_change=self.toggle_dark_mode, value=self.is_dark)
        
        self.navigation_menu = ft.NavigationRail(
            bgcolor= "#111418",
            selected_index=0,
            selected_label_text_style=ft.TextStyle(color="white", weight=ft.FontWeight.BOLD, size=18),
            unselected_label_text_style=ft.TextStyle(color="gray", size=18),
            label_type=ft.NavigationRailLabelType.ALL,
            width=200,
            extended= True,
            group_alignment=-1.0,
            leading= ft.Column(
                controls=[
                    ft.Image(
                        src="assets/axiology.png",  
                        width=40,
                        height=40,
                        fit=ft.ImageFit.CONTAIN
                    ),
                    ft.Text("Axiology", size=25, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text("Versión 1.0", size=14, color= grey),
                    ft.Text("Desarrollado por Luis Álvarez", size=14, color= grey),
                    ft.Container(height=40),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.alignment.center
            ),
            destinations=[
                ft.NavigationRailDestination(
                    icon= ft.Icon(ft.Icons.LIBRARY_BOOKS_OUTLINED, color="white"),
                    selected_icon= ft.Icons.LIBRARY_BOOKS,
                    label= "Funciones",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.FOLDER_OUTLINED, color="white"),
                    selected_icon=ft.Icons.FOLDER,
                    label="Carpeta",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.CHAT_OUTLINED, color="white"),
                    selected_icon=ft.Icons.CHAT,
                    label="Chat LAN",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.MONETIZATION_ON, color="white"),
                    selected_icon=ft.Icons.MONETIZATION_ON,
                    label="Cambio BCV",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.FEEDBACK_OUTLINED, color="white"),
                    selected_icon=ft.Icons.FEEDBACK,
                    label="Reportes",
                ),
            ],
            # ...existing code...
            trailing= ft.Column(
                controls = [
                    ft.Container(height=120),
                    self.dark_mode_switch,
                    ft.Text("Modo Oscuro", size=14, color="white"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.alignment.center
            ),
            
            on_change=self.on_navigation_change,
        )

        self.controls = [
            ft.Row([
                self.navigation_menu,
                ft.VerticalDivider(width=1),
                self.content_area
            ], 
            expand=True,
            tight=True,
            spacing=0
            )
        ]
        
    def toggle_dark_mode(self, e):
        if self.dark_mode_switch.value:
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT

        self.page.update()

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
