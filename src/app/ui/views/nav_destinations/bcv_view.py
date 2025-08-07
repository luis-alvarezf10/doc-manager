import flet as ft
import threading
from datetime import datetime
from src.app.ui.widgets.gradient_button import gradient_button
from src.app.ui.widgets.info_selected_mode import info_text
from src.utils.colors import main_gradient_color

try:
    import requests
    from bs4 import BeautifulSoup  # type: ignore
    import re
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    SCRAPING_AVAILABLE = True
except ImportError:
    try:
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        SCRAPING_AVAILABLE = False  # Solo requests disponible
    except ImportError:
        SCRAPING_AVAILABLE = False

def create_bcv_view(page):
    # Variables de estado
    usd_rate = ft.Text("--", size=40, weight=ft.FontWeight.BOLD, color="green")
    eur_rate = ft.Text("--", size=40, weight=ft.FontWeight.BOLD, color="blue")
    last_update = ft.Text("Sin actualizar", size=12, color="grey")
    status_text = ft.Text("Presiona 'Actualizar' para obtener tasas", size=14)
    info = ft.Column(
        controls=[
            ft.Text("Conversion de Tasa Monetaria (BCV)", size=25, text_align=ft.TextAlign.CENTER, style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight="bold"),
            info_text(text="- Tasas obtenidas de la página oficial de Banco central de Venezuela (BCV)"),
            info_text(text="- Si el valor no cambia, es posible que la página web no esté disponible o haya habido un error al obtener las tasas."),


        ],
        width=800
    )
    def scrape_bcv_rates():
        """Extraer tasas del BCV usando el método simple"""
        if not SCRAPING_AVAILABLE:
            return {"error": "Librerías de scraping no disponibles"}
            
        url = "https://www.bcv.org.ve/"
        try:
            print("Intentando BCV...")
            response = requests.get(url, verify=False, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            rates = {}
            
            # Buscar USD
            dollar_element = soup.select_one('#dolar strong')
            if dollar_element:
                price_text = dollar_element.get_text(strip=True)
                price_text = price_text.replace("Bs.", "").replace(",", ".").strip()
                try:
                    usd_price = float(price_text)
                    rates['USD'] = usd_price
                    print(f"BCV USD encontrado: {usd_price}")
                except ValueError:
                    print(f"No se pudo convertir USD: '{price_text}'")
            
            # Buscar EUR
            euro_element = soup.select_one('#euro strong')
            if euro_element:
                price_text = euro_element.get_text(strip=True)
                price_text = price_text.replace("Bs.", "").replace(",", ".").strip()
                try:
                    eur_price = float(price_text)
                    rates['EUR'] = eur_price
                    print(f"BCV EUR encontrado: {eur_price}")
                except ValueError:
                    print(f"No se pudo convertir EUR: '{price_text}'")
            
            if rates:
                print(f"BCV exitoso: {rates}")
                return rates
            else:
                print("BCV fallo: No se encontraron elementos")
                return {"error": "No se encontraron tasas"}
                
        except requests.exceptions.RequestException as e:
            print(f"BCV error de conexión: {e}")
            return {"error": f"Error de conexión: {e}"}
        except Exception as e:
            print(f"BCV error general: {e}")
            return {"error": str(e)}
    
    def get_fallback_rates():
        """Obtener tasas de API alternativa"""
        try:
            print("Intentando API alternativa...")
            api_url = "https://api.exchangerate-api.com/v4/latest/USD"
            response = requests.get(api_url, timeout=10, verify=False)
            data = response.json()
            
            if 'rates' in data and 'VES' in data['rates']:
                ves_rate = data['rates']['VES']
                print(f"API exitosa: USD={ves_rate}")
                return {
                    'USD': ves_rate,
                    'EUR': round(ves_rate * 1.1, 2)
                }
            else:
                print("API no tiene VES")
        except Exception as e:
            print(f"Error API: {e}")
        
        # Solo como último recurso
        print("Usando valores por defecto")
        return {
            'USD': 36.50,
            'EUR': 40.15
        }
    
    def update_rates(e=None):
        status_text.value = "🔄 Obteniendo tasas del BCV..."
        status_text.color = "blue"
        # Deshabilitar botón durante actualización
        if e and hasattr(e, 'control'):
            e.control.disabled = True
        page.update()
        
        def fetch_rates():
            try:
                # Intentar BCV primero
                print("=== INICIANDO ACTUALIZACION ===")
                rates = scrape_bcv_rates()
                print(f"Resultado BCV: {rates}")
                
                if 'error' in rates or not rates or len(rates) == 0:
                    print("BCV fallo, usando API...")
                    # Si falla, usar API alternativa
                    rates = get_fallback_rates()
                    source = "API Alternativa"
                else:
                    source = "BCV"
                    
                print(f"Tasas finales: {rates}, Fuente: {source}")
                
                # Actualizar UI
                if 'USD' in rates:
                    usd_rate.value = f"{rates['USD']:.2f}"
                if 'EUR' in rates:
                    eur_rate.value = f"{rates['EUR']:.2f}"
                
                last_update.value = f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')} - {source}"
                status_text.value = f"✅ Tasas actualizadas desde {source}"
                status_text.color = "green"
                
                # Actualizar calculadora automáticamente
            except Exception as ex:
                status_text.value = f"❌ Error: {str(ex)}"
                status_text.color = "red"
            
            # Rehabilitar botón y actualizar bs_input con tasa real
            if e and hasattr(e, 'control'):
                e.control.disabled = False
            
            # Actualizar bs_input con equivalente a 1 USD
            if 'USD' in rates:
                bs_input.value = f"{rates['USD']:.2f}"
            
            page.update()
        
        threading.Thread(target=fetch_rates, daemon=True).start()
    

    
    # Calculadora integrada
    countries = [
        {"key": "US", "flag": "https://flagcdn.com/h20/us.png", "name": "Estados Unidos", "suffix": "$"},
        {"key": "EU", "flag": "https://flagcdn.com/h20/eu.png", "name": "Europa", "suffix": "€"}
    ]
    
    selected_flag = ft.Image(src=countries[0]["flag"], width=32, height=24, fit=ft.ImageFit.COVER)
    amount_input = ft.TextField(label="", width=150, text_align=ft.TextAlign.CENTER, keyboard_type=ft.KeyboardType.NUMBER, suffix_text="$", value="1",         border_radius=8,
        border_width=0,
        border_color="transparent",
        filled=True,)
    usd_input = ft.TextField(label="USD", width=100, value="1", text_align=ft.TextAlign.CENTER, keyboard_type=ft.KeyboardType.NUMBER)
    eur_input = ft.TextField(label="EUR", width=100, value="1", text_align=ft.TextAlign.CENTER, keyboard_type=ft.KeyboardType.NUMBER)
    bs_input = ft.TextField(label="", width=150, value="36.50", text_align=ft.TextAlign.CENTER, keyboard_type=ft.KeyboardType.NUMBER, suffix_text="Bs",         border_radius=8,
        border_width=0,
        border_color="transparent",
        filled=True,)
    
    currency_selected = ft.Dropdown(
        options=[
            ft.dropdown.Option(
                key=country["key"],
                content=ft.Row([
                    ft.Image(src=country["flag"], width=24, height=16, fit=ft.ImageFit.COVER),
                    ft.Text(country["name"], size=14)
                ], spacing=8, tight=True)
            ) for country in countries
        ],
        value=countries[0]["key"],
        width=100,
        text_size=16,
        border_radius=8,
        border_width=0,
        border_color="transparent",
        filled=True,
    )
    
    
    
    
    usd_result = ft.Text("0.00 Bs", size=14, weight=ft.FontWeight.BOLD, color="green")
    eur_result = ft.Text("0.00 Bs", size=14, weight=ft.FontWeight.BOLD, color="blue")
    usd_from_bs = ft.Text("0.00 USD", size=14, weight=ft.FontWeight.BOLD, color="green")
    eur_from_bs = ft.Text("0.00 EUR", size=14, weight=ft.FontWeight.BOLD, color="blue")
    
    def calculate_to_bs(e=None):
        try:
            usd_val = float(usd_rate.value) if usd_rate.value != "--" else 36.50
            eur_val = float(eur_rate.value) if eur_rate.value != "--" else 40.15
            
            # Calcular USD a Bs
            usd_amount = float(usd_input.value) if usd_input.value else 0
            usd_bs = usd_amount * usd_val
            usd_result.value = f"{usd_bs:,.2f} Bs"
            
            # Calcular EUR a Bs
            eur_amount = float(eur_input.value) if eur_input.value else 0
            eur_bs = eur_amount * eur_val
            eur_result.value = f"{eur_bs:,.2f} Bs"
            
            page.update()
        except ValueError:
            pass
    
    def calculate_bidirectional(e=None):
        try:
            usd_val = float(usd_rate.value) if usd_rate.value != "--" else 36.50
            eur_val = float(eur_rate.value) if eur_rate.value != "--" else 40.15
            
            # Calcular Bs a USD y EUR para la calculadora bidireccional
            bs_amount = float(bs_input.value) if bs_input.value else 0
            usd_from_bs_val = bs_amount / usd_val
            eur_from_bs_val = bs_amount / eur_val
            
            usd_from_bs.value = f"{usd_from_bs_val:.2f} USD"
            eur_from_bs.value = f"{eur_from_bs_val:.2f} EUR"
            
            page.update()
        except ValueError:
            pass
    
    def calculate_from_bs(e=None):
        try:
            bs_amount = float(bs_input.value) if bs_input.value else 0
            selected_country = currency_selected.value
            
            # Actualizar bandera y suffix
            country_data = next((c for c in countries if c["key"] == selected_country), countries[0])
            selected_flag.src = country_data["flag"]
            amount_input.suffix_text = country_data["suffix"]
            
            if selected_country == "US":
                usd_val = float(usd_rate.value) if usd_rate.value != "--" else 36.50
                amount_result = bs_amount / usd_val
                amount_input.value = f"{amount_result:.2f}"
            elif selected_country == "EU":
                eur_val = float(eur_rate.value) if eur_rate.value != "--" else 40.15
                amount_result = bs_amount / eur_val
                amount_input.value = f"{amount_result:.2f}"
            
            page.update()
        except ValueError:
            pass
    
    def calculate_from_amount(e=None):
        try:
            amount = float(amount_input.value) if amount_input.value else 0
            selected_country = currency_selected.value
            
            if selected_country == "US":
                usd_val = float(usd_rate.value) if usd_rate.value != "--" else 36.50
                bs_result = amount * usd_val
                bs_input.value = f"{bs_result:.2f}"
            elif selected_country == "EU":
                eur_val = float(eur_rate.value) if eur_rate.value != "--" else 40.15
                bs_result = amount * eur_val
                bs_input.value = f"{bs_result:.2f}"
            
            page.update()
        except ValueError:
            pass
    
    def calculate_all(e=None):
        calculate_to_bs()
        calculate_bidirectional()
    
    # Conectar eventos
    bs_input.on_change = calculate_from_bs
    amount_input.on_change = calculate_from_amount
    currency_selected.on_change = calculate_from_bs
    usd_input.on_change = calculate_to_bs
    eur_input.on_change = calculate_to_bs
    

    
    # Agregar eventos de Enter
    amount_input.on_submit = calculate_from_amount
    bs_input.on_submit = calculate_from_bs
    
    # Carga automática de tasas
    update_rates()
    
    return ft.Column([
        ft.Container(height=20),
        info,
        ft.Divider(),
        ft.Container(height=20),
        ft.Row([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                            ft.Text("Dólar $", size=25, weight=ft.FontWeight.BOLD),
                            usd_rate,
                            ft.Text("Bolívares", size=15, color="grey")
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                ),
                elevation=8,
                width=200,
                height=200
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                            ft.Text("Euro €", size=25, weight=ft.FontWeight.BOLD),
                            eur_rate,
                            ft.Text("Bolívares", size=15, color="grey")
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                ),
                elevation=8,
                width=200,
                height=200
            )      
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        ),
        gradient_button(
            text = "Actualizar Tasas", 
            gradient=main_gradient_color,
            on_click= lambda e: (update_rates(e), calculate_all())
        ),
        ft.Card(
            content= ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.Column([
                            ft.Text("Moneda:", size=14, weight=ft.FontWeight.BOLD),
                            currency_selected
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Column([
                            ft.Text("Cantidad:", size=14, weight=ft.FontWeight.BOLD),
                            ft.Row([
                                selected_flag,
                                amount_input
                            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ]),
                    ft.Icon(ft.Icons.ARROW_CIRCLE_RIGHT, size=50, color="blue"),
                    ft.Column([
                        ft.Text("Bolívares:", size=14, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Image(src="https://flagcdn.com/h20/ve.png", width=32, height=24, fit=ft.ImageFit.COVER),
                            bs_input
                        ]),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                width=800,
                padding=20,
                border_radius=10
            ),
            elevation=8,
        ),
    ], 
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    alignment=ft.MainAxisAlignment.CENTER,
    spacing=15,
    scroll=ft.ScrollMode.AUTO,
    expand=True
    )