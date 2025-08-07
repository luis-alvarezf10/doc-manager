import flet as ft
import threading
from datetime import datetime
from src.app.ui.widgets.gradient_button import gradient_button
from src.utils.colors import main_gradient_color

# Imports opcionales para scraping
try:
    import requests
    from bs4 import BeautifulSoup  # type: ignore
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    SCRAPING_AVAILABLE = True
except ImportError:
    try:
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        SCRAPING_AVAILABLE = False
    except ImportError:
        SCRAPING_AVAILABLE = False

def create_bcv_view(page):
    # ==================== CONFIGURACIÓN INICIAL ====================
    
    # Datos de países
    countries = [
        {"key": "US", "flag": "https://flagcdn.com/24x18/us.png", "name": "Estados Unidos", "suffix": "$"},
        {"key": "EU", "flag": "https://flagcdn.com/24x18/eu.png", "name": "Europa", "suffix": "€"}
    ]
    
    # Variables de estado
    usd_rate = ft.Text("--", size=40, weight=ft.FontWeight.BOLD, color="green")
    eur_rate = ft.Text("--", size=40, weight=ft.FontWeight.BOLD, color="blue")
    last_update = ft.Text("Sin actualizar", size=12, color="grey")
    status_text = ft.Text("Presiona 'Actualizar' para obtener tasas", size=14)
    
    # Componentes de UI
    selected_flag = ft.Image(src=countries[0]["flag"], width=32, height=24, fit=ft.ImageFit.COVER)
    amount_input = ft.TextField(label="Cantidad", width=150, text_align=ft.TextAlign.CENTER, keyboard_type=ft.KeyboardType.NUMBER, suffix_text="$", value="1")
    bs_input = ft.TextField(label="Bolívares", width=120, value="36.50", text_align=ft.TextAlign.CENTER, keyboard_type=ft.KeyboardType.NUMBER, suffix_text="Bs")
    
    # Resultados de calculadora bidireccional
    usd_from_bs = ft.Text("0.00 USD", size=14, weight=ft.FontWeight.BOLD, color="green")
    eur_from_bs = ft.Text("0.00 EUR", size=14, weight=ft.FontWeight.BOLD, color="blue")
    
    # Dropdown de monedas
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
        width=200,
        text_size=16,
    )
    
    # ==================== FUNCIONES DE SCRAPING ====================
    
    def scrape_bcv_rates():
        """Extraer tasas del BCV desde el sitio oficial"""
        if not SCRAPING_AVAILABLE:
            return {"error": "Librerías de scraping no disponibles"}
            
        url = "https://www.bcv.org.ve/"
        try:
            response = requests.get(url, verify=False, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            rates = {}
            
            # Buscar USD
            dollar_element = soup.select_one('#dolar strong')
            if dollar_element:
                price_text = dollar_element.get_text(strip=True).replace("Bs.", "").replace(",", ".").strip()
                try:
                    rates['USD'] = float(price_text)
                except ValueError:
                    pass
            
            # Buscar EUR
            euro_element = soup.select_one('#euro strong')
            if euro_element:
                price_text = euro_element.get_text(strip=True).replace("Bs.", "").replace(",", ".").strip()
                try:
                    rates['EUR'] = float(price_text)
                except ValueError:
                    pass
            
            return rates if rates else {"error": "No se encontraron tasas"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def get_fallback_rates():
        """Obtener tasas de API alternativa"""
        try:
            api_url = "https://api.exchangerate-api.com/v4/latest/USD"
            response = requests.get(api_url, timeout=10, verify=False)
            data = response.json()
            
            if 'rates' in data and 'VES' in data['rates']:
                ves_rate = data['rates']['VES']
                return {'USD': ves_rate, 'EUR': round(ves_rate * 1.1, 2)}
        except Exception:
            pass
        
        # Valores por defecto
        return {'USD': 36.50, 'EUR': 40.15}
    
    # ==================== FUNCIONES DE CÁLCULO ====================
    
    def calculate_from_bs(e=None):
        """Convertir de bolívares a moneda extranjera"""
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
        """Convertir de moneda extranjera a bolívares"""
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
    

    
    def calculate_bidirectional(e=None):
        """Calcular conversiones desde bolívares para la calculadora bidireccional"""
        try:
            usd_val = float(usd_rate.value) if usd_rate.value != "--" else 36.50
            eur_val = float(eur_rate.value) if eur_rate.value != "--" else 40.15
            
            bs_amount = float(bs_input.value) if bs_input.value else 0
            usd_from_bs_val = bs_amount / usd_val
            eur_from_bs_val = bs_amount / eur_val
            
            usd_from_bs.value = f"{usd_from_bs_val:.2f} USD"
            eur_from_bs.value = f"{eur_from_bs_val:.2f} EUR"
            
            page.update()
        except ValueError:
            pass
    
    def calculate_all(e=None):
        """Ejecutar todos los cálculos"""
        calculate_bidirectional()
    
    # ==================== FUNCIÓN DE ACTUALIZACIÓN ====================
    
    def update_rates(e=None):
        """Actualizar tasas del BCV"""
        status_text.value = "🔄 Obteniendo tasas del BCV..."
        status_text.color = "blue"
        
        if e and hasattr(e, 'control'):
            e.control.disabled = True
        page.update()
        
        def fetch_rates():
            try:
                rates = scrape_bcv_rates()
                
                if 'error' in rates or not rates:
                    rates = get_fallback_rates()
                    source = "API Alternativa"
                else:
                    source = "BCV"
                
                # Actualizar UI
                if 'USD' in rates:
                    usd_rate.value = f"{rates['USD']:.2f}"
                if 'EUR' in rates:
                    eur_rate.value = f"{rates['EUR']:.2f}"
                
                last_update.value = f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')} - {source}"
                status_text.value = f"✅ Tasas actualizadas desde {source}"
                status_text.color = "green"
                
                # Actualizar bs_input con equivalente a 1 USD
                if 'USD' in rates:
                    bs_input.value = f"{rates['USD']:.2f}"
                
            except Exception as ex:
                status_text.value = f"❌ Error: {str(ex)}"
                status_text.color = "red"
            
            if e and hasattr(e, 'control'):
                e.control.disabled = False
            page.update()
        
        threading.Thread(target=fetch_rates, daemon=True).start()
    
    # ==================== EVENTOS ====================
    
    # Eventos de cambio
    bs_input.on_change = calculate_from_bs
    amount_input.on_change = calculate_from_amount
    currency_selected.on_change = calculate_from_bs
    
    # Eventos de Enter
    amount_input.on_submit = calculate_from_amount
    bs_input.on_submit = calculate_from_bs
    
    # ==================== INICIALIZACIÓN ====================
    
    update_rates()  # Carga automática de tasas
    
    # ==================== INTERFAZ DE USUARIO ====================
    
    return ft.Column([
        # Título
        ft.Text("Calculadora de cambio monetario", size=25, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        ft.Divider(),
        
        # Tarjetas de tasas
        ft.Row([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Dólar $", size=25, weight=ft.FontWeight.BOLD),
                        usd_rate,
                        ft.Text("Bolívares", size=15, color="grey")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                ),
                elevation=8, width=200, height=200
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Euro €", size=25, weight=ft.FontWeight.BOLD),
                        eur_rate,
                        ft.Text("Bolívares", size=15, color="grey")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                ),
                elevation=8, width=200, height=200
            )
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        
        # Botón actualizar
        gradient_button(
            text="Actualizar Tasas", 
            gradient=main_gradient_color,
            on_click=lambda e: (update_rates(e), calculate_all())
        ),
        
        # Convertidor principal
        ft.Card(
            content=ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.Column([
                            ft.Text("Moneda:", size=14, weight=ft.FontWeight.BOLD),
                            currency_selected
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Column([
                            ft.Text("Cantidad:", size=14, weight=ft.FontWeight.BOLD),
                            ft.Row([selected_flag, amount_input], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ]),
                    ft.Icon(ft.Icons.ARROW_FORWARD, size=30, color="blue"),
                    ft.Column([
                        ft.Text("Bolívares:", size=14, weight=ft.FontWeight.BOLD),
                        bs_input
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                width=800, padding=20, border_radius=10
            ),
            elevation=8,
        ),
        
        # Calculadora bidireccional
        ft.Column([
            ft.Text("🧮 Calculadora Bidireccional", size=18, weight=ft.FontWeight.BOLD),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Bolívares → 💱", size=14, weight=ft.FontWeight.BOLD, color="#1565c0"),
                        ft.Row([bs_input], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Divider(height=5),
                        ft.Row([
                            usd_from_bs,
                            ft.Text("|", size=16, color="grey"),
                            eur_from_bs
                        ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
                    ]),
                    padding=15, bgcolor="#e3f2fd", border_radius=10
                )
            )
        ], expand=1),
        
        # Estado
        ft.Container(
            content=ft.Column([status_text, last_update]),
            padding=15, bgcolor="#f0f8ff", border_radius=10, margin=ft.margin.only(top=20)
        ),
        
        # Información
        ft.Container(
            content=ft.Column([
                ft.Text("ℹ️ Información", weight=ft.FontWeight.BOLD),
                ft.Text("• Las tasas se obtienen del sitio oficial del BCV"),
                ft.Text("• Si el BCV no está disponible, se usa API alternativa"),
                ft.Text("• Los datos son referenciales"),
                ft.Text("• Actualización manual requerida")
            ]),
            padding=15, bgcolor="#fff8dc", border_radius=10, margin=ft.margin.only(top=10),
        )
    ], 
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    spacing=15,
    scroll=ft.ScrollMode.AUTO,
    expand=True
    )