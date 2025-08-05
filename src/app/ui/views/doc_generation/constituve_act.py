import flet as ft
from src.app.ui.widgets.input_form import create_input, clear_input_list
from src.app.ui.widgets.info_selected_mode import info_text
from src.app.ui.widgets.gradient_button import gradient_button
from src.utils.colors import main_gradient_color, grey
from src.documents.constitutive_act import generate_constitutive_act
from src.app.ui.widgets.show_snackbar import show_snackbar

def constituve_act_form(page: ft.Page):
    company = ["Nombre", "Dedicación", "RIF", "Ubicación", "Domicilio (Ciudad)", "Domicilio (Municipio)", "Domicilio (Estado)", "Duración","Capital", "Años de función de accionistas"]
    show_visible_columns = ["Nombre", "No Acciones", "Cargo", "Acciones"]

    accionistas = []

    accionista_fields = ["Nombre", "Sexo", "Nacionalidad", "Ocupación", "Estado civil", "Cédula", "RIF", "Domicilio (Ciudad)", "Domicilio (Municipio)", "Domicilio (Estado)", "No Acciones", "Cargo"]
    
    comisario_fields = ["Nombre", "Sexo", "Cédula", "Nacionalidad", "No de Colegio", "Años de función"]
    comisario = {}
    
    input_filename = ft.TextField(
        label="Nombre del archivo", 
        filled=True, 
        expand=True, 
        border_radius=8,                           
        border_width=0,      
        border_color="transparent", 
        focused_border_width=0,  
        text_size=16,     
    )
    
    info = ft.Column(
        controls=[
            ft.Text("Generador de Actas Constitutivas", size=25, text_align=ft.TextAlign.CENTER, style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight="bold"),
            info_text(text="1. Completa los campos Requeridos de información de empresa."),
            info_text(text="2. Elige el nombre del presentante de Acta"),
            info_text(text="3. Agrega los accionistas de la empresa."),
            info_text(text="4. No te preocupes si no sabes realmente el costo de la acciones, ni la distribución de total invertido por los accionistas el sistema lo hará de manera automática sin necesidad de sacar calculos, unicamente es necesario el capital total de la empresa y el número de acciones."),
            info_text(text="5. Haz clic en 'Generar Acta' para crear el documento."),
            info_text(text="6. Revisa detalladamente el documento para evitar errores de escritura, si hubo porfavor es necesario que lo notifiques en el apartado de reportes para una breve mejoría en el sistema"),
            info_text(text="7. El documento se guardará con el nombre especificado o con el nombre de la empresa en la carpeta de -> Documentos Generados -> Actas Constitutivas"), 
            input_filename
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
    
    
    def contar_acciones():
        total = 0
        for a in accionistas:
            try:
                total += int(a.get("No Acciones", 0))
            except ValueError:
                print(f"Error al convertir acciones de {a['Nombre']}")
        print(f"Total de acciones: {total}")
        return total
    
    acciones_total_text = ft.Text("0", color=ft.Colors.WHITE, weight="bold", size=20)
    container_cont = ft.Container(
        content=acciones_total_text,
        bgcolor=grey,
        border_radius=10,
        padding=10,
        alignment=ft.alignment.center,
        width=150,
        height=45,
    )
    
    def update_total_acciones():
        total = contar_acciones()
        acciones_total_text.value = f"{total}"
        page.update()
        
    def add_accionista(e):
        a_data = {k: v.value for k, v in accionista_inputs.items()}
        if any(v.strip() == "" for v in a_data.values()):
            page.update()
            return

        accionistas.append(a_data.copy())
        update_table()
        update_total_acciones()
        clear_fields()
        page.open(show_snackbar(content=f"Agregado nuevo accionista satisfactoriamente", type="success"))       

    def delete_accionista(index):
        def _delete(e):
            accionistas.pop(index)
            update_table()
            update_total_acciones()
        return _delete
    
    def view_accionista(accionista):
        def _view(e):
            # Crear diálogo con información del accionista
            dialog = ft.AlertDialog(
                title=ft.Text(f"Información de {accionista['Nombre']}"),
                content=ft.Column([
                    ft.Text(f"Cédula: {accionista['Cédula']}"),
                    ft.Text(f"RIF: {accionista['RIF']}"),
                    ft.Text(f"Sexo: {accionista['Sexo']}"),
                    ft.Text(f"Estado civil: {accionista['Estado civil']}"),
                    ft.Text(f"Nacionalidad: {accionista['Nacionalidad']}"),
                    ft.Text(f"Ocupación: {accionista['Ocupación']}"),
                    ft.Text(f"Domicilio: {accionista['Domicilio (Ciudad)']}, {accionista['Domicilio (Municipio)']}, {accionista['Domicilio (Estado)']}"),
                    ft.Text(f"No Acciones: {accionista['No Acciones']}"),
                    ft.Text(f"Cargo: {accionista['Cargo']}")
                ], tight=True),
                actions=[ft.TextButton("Cerrar", on_click=lambda e: page.close(dialog))]
            )
            page.open(dialog)
        return _view

    def update_table():
        accionistas_table.rows.clear()
        for i, accionista in enumerate(accionistas):
            # Crear celdas para las columnas visibles (excluyendo "Acciones")
            cells = [ft.DataCell(ft.Text(accionista.get(col, ""))) for col in show_visible_columns[:-1]]
            
            # Agregar celda con botones de acción
            action_buttons = ft.Row([
                ft.IconButton(
                    icon=ft.Icons.VISIBILITY,
                    tooltip="Ver detalles",
                    on_click=view_accionista(accionista)
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    tooltip="Eliminar",
                    icon_color=ft.Colors.RED,
                    on_click=delete_accionista(i)
                )
            ], spacing=5)
            
            cells.append(ft.DataCell(action_buttons))
            
            accionistas_table.rows.append(ft.DataRow(cells=cells))
        accionistas_table.update()


    def clear_fields():
        accionista_inputs.clear()
        clear_input_list()  # Limpiar la lista global de inputs

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
    
    presentantes_data = [
        {"nombre": "Pedro Luis Álvarez Farías", 
         "sexo": "Masculino",
         "nacionalidad": "venezolano", 
         "ocupacion": "abogado",
         "estado civil": "casado",
         "cedula": "V-8.245.502",
         "rif": "8.245.502-3", 
         "ciudad": "Barcelona", 
         "municipio": "Simón Bolívar", 
         "estado": "Anzoátegui"
        },
        {"nombre": "Marianela Del Valle Franceschi Chacín De Álvarez", 
         "sexo": "Femenino",
         "nacionalidad": "venezolana", 
         "ocupacion": "docente",     
         "estado civil": "casada",
         "cedula": "V-8.262.318",
         "rif": "8.262.318-0",
         "ciudad": "Barcelona", 
         "municipio": "Simón Bolívar", 
         "estado": "Anzoátegui"
        }
    ]
    
    presentante = ft.Dropdown(
        label="Presentante",
        value= presentantes_data[0]["nombre"],
        options=[ft.dropdown.Option(p["nombre"]) for p in presentantes_data],
        filled=True,
        expand=True,
        border_radius=8,
        border_width=0,
        border_color="transparent",
        focused_border_width=0,
        text_size=16,
    )
    
    
    info_table =  ft.Column(
                        controls= [
                            ft.Text("Tabla de Accionistas", style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight="bold"),
                            accionistas_table,
                            ft.Row([
                                ft.Text("Total de acciones: ", weight="bold"),
                                container_cont
                            ], spacing=10)
                        ]
                )
    
    def generate_act(e):
        
        if len(accionistas) < 2:
            page.open(show_snackbar(content="Debes agregar al menos 2 accionistas", type="error"))
            return
        
        presentante_seleccionado = presentante.value
        p_data = None
        for persona in presentantes_data:
            if persona["nombre"] == presentante_seleccionado:
                p_data = persona
                print("Presentante seleccionado:", persona)
                break
    
        # Extraer valores de los TextField
        empresa_data = {k: v.value for k, v in company_inputs.items()}
        comisario_data = {k: v.value for k, v in comisario.items()}
        
        try:           
            ruta_contrato = generate_constitutive_act(
                accionistas, 
                p_data, 
                empresa_data, 
                acciones_total_text.value, 
                comisario_data,
                input_filename.value,
                )
            page.open(show_snackbar(content=f"Acta Constitutiva generada con éxito en {ruta_contrato}", type="success"))    
        except Exception as ex:
            page.open(show_snackbar(content=f"Error al generar el acta: {ex}", type="error"))       
        
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
                        presentante,
                        create_section("Datos de Comisario", comisario_fields, comisario),
                    ],
                    
                    ),
                width=800,
                ),
            ft.Container(height=20),    
            ft.Divider(),
            ft.Row(
                controls=[
                    accionista_form,
                    info_table
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
