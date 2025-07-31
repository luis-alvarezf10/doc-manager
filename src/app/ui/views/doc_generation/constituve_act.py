import flet as ft
from src.app.ui.widgets.input_form import create_input
from src.app.ui.widgets.info_selected_mode import info_text
from src.app.ui.widgets.gradient_button import gradient_button
from src.utils.colors import main_gradient_color

def constituve_act_form(page: ft.Page):
    company = ["Nombre", "Dedicación", "RIF", "Domicilio (Ciudad)", "Domicilio (Municipio)", "Domicilio (Estado)"]
    show_visible_columns = ["Nombre", "Cédula", "Número de acciones", "Cargo"]

    accionistas = []
    accionista_fields = ["Nombre", "Nacionalidad", "Ocupación", "Estado civil", "Cédula", "RIF", "Domicilio (Ciudad)", "Domicilio (Municipio)", "Domicilio (Estado)", "Número de acciones", "Cargo"]
    
    info = ft.Column(
        controls=[
            ft.Text("Generador de Actas Constitutivas", size=25, text_align=ft.TextAlign.CENTER, style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight="bold"),
            info_text(text="1. Completa los campos Requeridos de información de empresa."),
            info_text(text="2. Elige el nombre del presentante de Acta"),
            info_text(text="3. Agrega los accionistas de la empresa."),
            info_text(text="4. Haz clic en 'Generar Acta' para crear el documento."),
            info_text(text="5. El documento se guardará con el nombre especificado o con el nombre de la empresa en la carpeta de -> Documentos Generados -> Actas Constitutivas")
        ],
        width=800
    )
    company_inputs = {}
    accionista_inputs = {}

    def create_section(title, person, target_dict):
        return ft.Column(
            controls=[
                ft.Text(title, style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight="bold"),
                ft.ResponsiveRow(
                    controls=[
                        create_input(title, field, target_dict) for field in person
                    ]
                )
            ]
        )
    
    accionistas_table = ft.DataTable(
        columns=[ft.DataColumn(ft.Text(col)) for col in show_visible_columns],
        rows=[]
    )

    def add_accionista(e):
        a_data = {k: v.value for k, v in accionista_inputs.items()}
        if any(v.strip() == "" for v in a_data.values()):
            page.update()
            return

        accionistas.append(a_data.copy())
        print("Total accionistas:", len(accionistas))  # <- Aquí
        update_table()
        clear_fields()

    def update_table():
        accionistas_table.rows.clear()
        for accionista in accionistas:
            accionistas_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(accionista.get(col, ""))) for col in show_visible_columns
                    ]
                )
            )
        page.update()


    def clear_fields():
        accionista_inputs.clear()

        # Crear nuevo formulario (nueva instancia)
        new_controls = [
                create_section("Datos de Accionista", accionista_fields, accionista_inputs),
                add_accionista_btn,
            ]

        # Reemplazar el contenido del container con el nuevo formulario
        accionista_form.controls = new_controls
            
        page.update()
        
    add_accionista_btn = ft.ElevatedButton(
        text="Agregar Accionista",
        bgcolor="blue",
        color="white",
        icon=ft.Icons.PERSON_ADD,
        on_click=add_accionista,
    )
    
    accionista_form = ft.Column(
                        controls=[
                            create_section("Datos de Accionista", accionista_fields, accionista_inputs),
                            add_accionista_btn,
                        ],
                        width=500,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    
    presentantes = ["Pedro Álvarez", "Marianela Franceschi"]
    
    presentante = ft.Dropdown(
        label="Presentante",
        value= presentantes[0],
        options=[ft.dropdown.Option(nombre) for nombre in presentantes],
        filled=True,
        expand=True,
        border_radius=8,
        border_width=0,
        border_color="transparent",
        focused_border_width=0,
        text_size=16,
    )
    
    def generate_act(e):
        
        if len(accionistas_table.rows) < 2:
            print("No hay accionistas")
            return
        # try:
            
        # except Exception as ex:
        #     print(ex)
        page.update()
    
    return ft.Column(
        controls=[
            ft.Container(height=20),
            info,
            ft.Container(
                content= ft.Column(
                    controls= [  
                    create_section("Datos de la empresa", company, company_inputs),
                    ft.Divider(),
                    ft.Text("Nombre de Presentante", style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight="bold"),
                    presentante
                    ],
                    
                    ),
                width=800,
                ),
            ft.Container(height=20),    
            ft.Divider(),
            ft.Row(
                controls=[
                    accionista_form,
                    accionistas_table
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.START
            ),
            ft.Divider(),
            gradient_button(
                text="Generar Acta",
                gradient = main_gradient_color,
                width= 200,
                height= 40,
                on_click= generate_act
            ),
            ft.Container(height=100),
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
