import flet as ft
from datetime import datetime
from src.documents.buy_and_sell_doc import generate_buy_and_sell_doc
from src.utils.datestr import fecha_a_formato_legal

def compraventa_contract_view(page: ft.Page):
    vendedor_fields = []
    comprador_fields = []
    inmueble_fields = []
    oficina_fields = []
    nombre_archivo = ft.TextField(label="Nombre del archivo", filled=True, expand=True)
    # Texto para mostrar estado
    status_text = ft.Text("")

    def crear_input(label, lista):
        if label.lower() == "estado civil":
            dropdown = ft.Dropdown(
                label=label,
                options=[
                    ft.dropdown.Option("Soltero/a"),
                    ft.dropdown.Option("Casado/a"),
                    ft.dropdown.Option("Divorciado/a"),
                    ft.dropdown.Option("Viudo/a"),
                ],
                filled=True,
                expand=True
            )
            lista.append(dropdown)
            return dropdown
        elif label.lower() == "razón":
            dropdown = ft.Dropdown(
                label=label,
                options=[
                    ft.dropdown.Option("Edificio"),
                    ft.dropdown.Option("Casa"),
                    ft.dropdown.Option("Apartamento"),
                    ft.dropdown.Option("Terreno"),
                    ft.dropdown.Option("Local Comercial"),
                ],
                filled=True,
                expand=True
            )
            lista.append(dropdown)
            return dropdown
        else:
            campo = ft.TextField(label=label, filled=True, expand=True)
            lista.append(campo)
            return campo

    def crear_seccion(titulo, campos, lista_destino):
        return ft.Column([
            ft.Text(titulo, style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight="bold"),
            ft.ResponsiveRow(
                [crear_input(campo, lista_destino) for campo in campos],
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
        "Domicilio (Ciudad)", "Domicilio (Municipio)", "Domicilio (Estado)", "Número de folio", "Protocolo", "Tomo", "Trimestre referido"
    ]
    selected_date = datetime.now()
    fecha_text = ft.Text()
    
    async def pick_date(e):
        date_picker = ft.DatePicker(
            first_date=datetime(datetime.now().year - 10, 1, 1),
            last_date=datetime(datetime.now().year + 10, 12, 31),
        )
        
        page.overlay.append(date_picker)
        await page.update_async()  # Actualiza la página primero
        
        # Abre el diálogo del DatePicker
        await date_picker.open_async()  # Método actualizado
        
        nonlocal selected_date
        if date_picker.value:
            selected_date = date_picker.value
            fecha_text.value = selected_date.strftime("%d/%m/%Y")
            await page.update_async()
    
    def crear_seccion(titulo, campos, lista_destino):
        # Si es la sección de oficina, añadimos el date picker
        if titulo == "Datos de Oficina":
            return ft.Column([
                ft.Text(titulo, style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight="bold"),
                ft.ResponsiveRow(
                    [crear_input(campo, lista_destino) for campo in campos],
                    columns=12,
                    alignment="start",
                    spacing=10
                ),
                ft.Row([
                    ft.Text("Fecha: ", weight="bold"),
                    fecha_text,
                    ft.IconButton(
                        icon=ft.Icons.CALENDAR_MONTH,
                        on_click=pick_date,
                        tooltip="Seleccionar fecha"
                    )
                ], spacing=10)
            ], spacing=15)
        else:
            return ft.Column([
                ft.Text(titulo, style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight="bold"),
                ft.ResponsiveRow(
                    [crear_input(campo, lista_destino) for campo in campos],
                    columns=12,
                    alignment="start",
                    spacing=10
                )
            ], spacing=15)

    
    
    def generar_contrato(e):
        # Datos de prueba automáticos (mock data)
        mock_vendedor = {
            'Nombre': 'MARIA GABRIELA SUAREZ',
            'Nacionalidad': 'venezolana',
            'Ocupación': 'Comerciante',
            'Estado civil': 'Soltera',
            'Cédula': 'V-12345678',
            'RIF': 'V-987654321',
            'Domicilio (Ciudad)': 'Barcelona',
            'Domicilio (Municipio)': 'Simón Bolívar',
            'Domicilio (Estado)': 'Anzoátegui'
        }

        mock_comprador = {
            'Nombre': 'JUAN CARLOS PEREZ',
            'Nacionalidad': 'venezolanO',
            'Estado civil': 'Casado',
            'Cédula': 'V-87654321',
            'RIF': 'V-123456789',
            'Domicilio (Ciudad)': 'Barcelona',
            'Domicilio (Municipio)': 'Simón Bolívar',
            'Domicilio (Estado)': 'Anzoátegui'
        }
        
        
        mock_inmueble = {
            'Razón': 'Casa',
            'Ubicación': 'Calle Principal, número 123',
            'Domicilio (Ciudad)': 'Barcelona',
            'Domicilio (Parroquia)': 'El Carmen',
            'Domicilio (Municipio)': 'Simón Bolívar',
            'Domicilio (Estado)': 'Anzoátegui',
            'Código catastral': '1234567890',
            'Superficie (m²)': '120,00',
            'Límite Norte': 'Calle Principal',
            'Límite Sur': 'Calle Secundaria',
            'Límite Este': 'Avenida Este',
            'Límite Oeste': 'Avenida Oeste',
            'Precio': '1.999.100,00',
            'Número de cheque': '987654',
            'Cuenta a depositar': '1234567890',
            'Banco': 'Banco de Venezuela'
        }
    
        fecha_dict = fecha_a_formato_legal(selected_date)
        mock_oficina = {
            'Domicilio (Ciudad)': 'Barcelona',
            'Domicilio (Municipio)': 'Simón Bolívar',
            'Domicilio (Estado)': 'Anzoátegui',
            'Fecha': selected_date.strftime("%d/%m/%Y"),
            'Fecha_legal': fecha_dict['completa'],
            'Ano_legal': fecha_dict['ano_letras'],  # Coincide con 'ano_letras'
            'Ano_numero': fecha_dict['ano_numero'],
            'Ano_documento': fecha_dict['ano_documento'],  # Cambiado a 'ano_documento'['ano_formato_documento'],
            'Número de folio': '123',
            'Protocolo': '456',
            'Tomo': '789',
            'Trimestre referido': 'Primer'
        }

        try:
            # Llamar a la función de generación con datos de prueba
            ruta_contrato = generate_buy_and_sell_doc(
                vendedor_data=mock_vendedor,
                comprador_data=mock_comprador,
                inmueble_data=mock_inmueble,
                oficina_data=mock_oficina,
                page=page
            )

            # Mostrar mensaje de éxito
            print(f"✅ Contrato generado exitosamente!\n{ruta_contrato}"),

        except Exception as ex:
            print(f"❌ Error al generar contrato: {str(ex)}"),
        page.update()

    
    # def generar_contrato(e):
    #     # Validar campos obligatorios
    #     required_fields = [
    #         *vendedor_fields[:8],
    #         *[campo for campo in comprador_fields if campo.label in ["Nombre", "Estado civil", "RIF"]],
    #         *inmueble_fields[:13]
    #     ]
        
    #     if not all(campo.value for campo in required_fields):
    #         print("❌ Complete todos los campos obligatorios"),
    #         page.update()
    #         return

    #     try:
    #         # Obtener datos de los campos
    #         v_data = {campo.label: campo.value for campo in vendedor_fields}
    #         c_data = {campo.label: campo.value for campo in comprador_fields} 
    #         i_data = {campo.label: campo.value for campo in inmueble_fields}
    #         o_data = {campo.label: campo.value for campo in oficina_fields}

    #         # Llamar a la función de generación
    #         ruta_contrato = generate_buy_and_sell_doc(
    #             vendedor_data=v_data,
    #             comprador_data=c_data,
    #             inmueble_data=i_data,
    #             oficina_data=o_data,
    #             page=page
    #         )

    #         # Mostrar mensaje de éxito
    #         print(f"✅ Contrato generado: {ruta_contrato}"),

    #     except Exception as ex:
    #         print(f"❌ Error: {str(ex)}"),
        
    #     page.update()

    return ft.Column(
        controls=[
            ft.Column([
                ft.Container(height=20),
                nombre_archivo,
                crear_seccion("Datos del Vendedor", vendedor_campos, vendedor_fields),
                crear_seccion("Datos del Comprador", comprador_campos, comprador_fields),
                crear_seccion("Datos del Inmueble", inmueble_campos, inmueble_fields),
                crear_seccion("Datos de Oficina", oficina_campos, oficina_fields),
                ft.ElevatedButton("Generar Contrato", icon=ft.Icons.DESCRIPTION, on_click=generar_contrato),
                status_text,
                ft.Container(height=100),
            ], spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
        ],
        height=600,
        expand=True,
        width=800,
    )
