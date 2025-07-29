import flet as ft
from datetime import datetime
from src.documents.buy_and_sell_doc import generate_buy_and_sell_doc
from src.utils.datestr import fecha_a_formato_legal

from src.utils.colors import dark_grey, gradient_color
from src.app.ui.widgets.gradient_button import gradient_button
from src.app.ui.widgets.input_form import create_input, input_list
from src.app.ui.widgets.info_selected_mode import info_text


def compraventa_contract_view(page: ft.Page):
    vendedor_fields = []
    comprador_fields = []
    inmueble_fields = []
    oficina_fields = []
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
            ft.Text("Generador de Contrato de Compraventa", size=20,text_align=ft.TextAlign.CENTER, style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight="bold"),  
            info_text(text="1. Completa los campos para generar un contrato de compraventa."),  
            info_text(text="2. Asegúrate de ingresar todos los datos requeridos."),
            info_text(text="3. Selecciona la fecha del contrato."),
            info_text(text="4. Haz clic en 'Generar Contrato' para crear el documento."),
            info_text(text="5. El contrato se guardará con el nombre especificado..."),
            input_filename,
        ]
    )
    
    def open_date_picker(e):
        date_picker.open = True
        page.update()

    datetime_button = ft.ElevatedButton(
                        text= "Seleccionar fecha",
                        icon=ft.Icons.CALENDAR_MONTH,
                        on_click=open_date_picker,
                        bgcolor= ft.Colors.ORANGE,
                        color=ft.Colors.WHITE,
                        width=200,
                        height=40,
                        style=ft.ButtonStyle(
                            text_style=ft.TextStyle(
                            size=16, 
                            weight="bold",
                            ),
                        )
    )
    
    status_text = ft.Text("Esperando acción...", size=15, color=dark_grey)


    def crear_seccion(titulo, campos, lista_destino):
        input_list.clear()  # Resetear el orden antes de agregar nuevos
        if titulo == "Datos de Oficina":
            return ft.Column([
                ft.Text(titulo, style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight="bold"),
                ft.ResponsiveRow(
                    [create_input(titulo, campo, lista_destino) for campo in campos],
                    columns=12,
                    alignment="start",
                    spacing=10
                ),
                ft.Row([
                    ft.Text("Fecha: ", weight="bold"),
                    datetime_button
                ], spacing=10)
            ], spacing=15)
        else:
            return ft.Column([
                ft.Text(titulo, style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight="bold"),
                ft.ResponsiveRow(
                    [create_input(titulo, campo, lista_destino) for campo in campos],
                    columns=12,
                    alignment="start",
                    spacing=10
                )
            ], spacing=15)

    vendedor_campos = [
        "Nombre", "Nacionalidad", "Ocupación", "Estado civil",
        "Cédula", "RIF", "Domicilio (Ciudad)", "Domicilio (Municipio)", "Domicilio (Estado)"
    ]

    comprador_campos = [
        "Nombre", "Nacionalidad", "Estado civil", 
        "Cédula",  
        "RIF",
        "Domicilio (Ciudad)", "Domicilio (Municipio)", "Domicilio (Estado)"
    ]

    inmueble_campos = [
        "Razón", "Ubicación", "Domicilio (Ciudad)","Domicilio (Parroquia)", "Domicilio (Municipio)", "Domicilio (Estado)",
        "Código catastral", "Superficie (m²)",
        "Límite Norte", "Límite Sur", "Límite Este", "Límite Oeste",
        "Precio", "Número de cheque", "Cuenta a depositar", "Banco"
    ]

    oficina_campos = [
        "Domicilio (Ciudad)", "Domicilio (Municipio)", "Domicilio (Estado)", 
        "Número de folio", "Protocolo", "Tomo", "Trimestre referido"
    ]
    
    selected_date_value = None 

    date_picker = ft.DatePicker(
        first_date=datetime(1980, 1, 1),
        last_date=datetime.now(),
        on_change=lambda e: handle_date_selection(e) 
    )

    page.overlay.append(date_picker)

    def handle_date_selection(e):
        nonlocal selected_date_value  
        if date_picker.value:
            selected_date_value = date_picker.value 
            datetime_button.text = selected_date_value.strftime("%d/%m/%Y")
            datetime_button.icon = ft.Icons.CHECK
        else:
            datetime_button.text = "Seleccionar fecha"
        page.update()
        
    def generar_contrato(e):
        try:
            v_data = {campo.label: campo.value for campo in vendedor_fields}
            c_data = {campo.label: campo.value for campo in comprador_fields} 
            i_data = {campo.label: campo.value for campo in inmueble_fields}
            o_data = {campo.label: campo.value for campo in oficina_fields}

            fecha_dict = fecha_a_formato_legal(selected_date_value)
            o_data.update({
                'Fecha': selected_date_value.strftime("%d/%m/%Y"),
                'Fecha_legal': fecha_dict['completa'],
                'Ano_legal': fecha_dict['ano_letras'],
                'Ano_numero': fecha_dict['ano_numero'],
                'Ano_documento': fecha_dict['ano_documento']
            })

            ruta_contrato = generate_buy_and_sell_doc(
                vendedor_data=v_data,
                comprador_data=c_data,
                inmueble_data=i_data,
                oficina_data=o_data,
                page=page,
                input_filename=input_filename.value 
            )

            status_text.value = f"✅ Contrato generado exitosamente!\n{ruta_contrato}",
            status_text.color = ft.Colors.GREEN_700
        except Exception as ex:
            status_text.value = f"❌ Error al generar contrato: {str(ex)}",
            status_text.color = ft.Colors.RED_700
        page.update()

    return ft.Column(
        controls=[
            ft.Column([
                ft.Container(height=20),
                info,
                crear_seccion("Datos del Vendedor", vendedor_campos, vendedor_fields),
                crear_seccion("Datos del Comprador", comprador_campos, comprador_fields),
                crear_seccion("Datos del Inmueble", inmueble_campos, inmueble_fields),
                crear_seccion("Datos de Oficina", oficina_campos, oficina_fields),
                gradient_button(
                    text= "Generar Contrato",
                    width= 200,
                    height= 40,
                    gradient= gradient_color,
                    on_click= generar_contrato,
                ),
                status_text,
                ft.Container(height=150),
            ], 
            spacing=15, 
            scroll=ft.ScrollMode.AUTO, 
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        ],
        scroll= ft.ScrollMode.AUTO,
        expand=True,
        width=800,
    )