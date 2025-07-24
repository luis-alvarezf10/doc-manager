import flet as ft
import threading
from datetime import datetime

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
    usd_rate = ft.Text("--", size=32, weight=ft.FontWeight.BOLD, color="green")
    eur_rate = ft.Text("--", size=32, weight=ft.FontWeight.BOLD, color="blue")
    last_update = ft.Text("Sin actualizar", size=12, color="grey")
    status_text = ft.Text("Presiona 'Actualizar' para obtener tasas", size=14)
    
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
        e.control.disabled = True if e else None
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
                calculate_all()
                
            except Exception as ex:
                status_text.value = f"❌ Error: {str(ex)}"
                status_text.color = "red"
            
            # Rehabilitar botón
            if e and hasattr(e, 'control'):
                e.control.disabled = False
            page.update()
        
        threading.Thread(target=fetch_rates, daemon=True).start()
    

    
    # Calculadora integrada
    usd_input = ft.TextField(label="USD", width=100, value="1", text_align=ft.TextAlign.CENTER, keyboard_type=ft.KeyboardType.NUMBER)
    eur_input = ft.TextField(label="EUR", width=100, value="1", text_align=ft.TextAlign.CENTER, keyboard_type=ft.KeyboardType.NUMBER)
    bs_input = ft.TextField(label="Bolívares", width=120, value="100", text_align=ft.TextAlign.CENTER, keyboard_type=ft.KeyboardType.NUMBER)
    
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
    
    def calculate_from_bs(e=None):
        try:
            usd_val = float(usd_rate.value) if usd_rate.value != "--" else 36.50
            eur_val = float(eur_rate.value) if eur_rate.value != "--" else 40.15
            
            # Calcular Bs a USD y EUR
            bs_amount = float(bs_input.value) if bs_input.value else 0
            usd_from_bs_val = bs_amount / usd_val
            eur_from_bs_val = bs_amount / eur_val
            
            usd_from_bs.value = f"{usd_from_bs_val:.2f} USD"
            eur_from_bs.value = f"{eur_from_bs_val:.2f} EUR"
            
            page.update()
        except ValueError:
            pass
    
    def calculate_all(e=None):
        calculate_to_bs()
        calculate_from_bs()
    
    usd_input.on_change = calculate_to_bs
    eur_input.on_change = calculate_to_bs
    bs_input.on_change = calculate_from_bs
    

    
    # Cálculo inicial
    calculate_all()
    
    return ft.Column([
        ft.Text("🏦 Tasas BCV - Banco Central de Venezuela", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        
        # Layout principal con tasas y calculadora
        ft.Row([
            # Columna izquierda - Tasas
            ft.Column([
                ft.Text("💱 Tasas Oficiales", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("🇺🇸 Dólar USD", size=16, weight=ft.FontWeight.BOLD),
                                usd_rate,
                                ft.Text("Bolívares", size=10, color="grey")
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=15,
                            bgcolor="#e8f5e8",
                            border_radius=10
                        ),
                        width=150
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("🇪🇺 Euro EUR", size=16, weight=ft.FontWeight.BOLD),
                                eur_rate,
                                ft.Text("Bolívares", size=10, color="grey")
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=15,
                            bgcolor="#e3f2fd",
                            border_radius=10
                        ),
                        width=150
                    )
                ], spacing=10)
            ], expand=1),
            
            ft.VerticalDivider(width=1),
            
            # Columna derecha - Calculadora
            ft.Column([
                ft.Text("🧮 Calculadora Bidireccional", size=18, weight=ft.FontWeight.BOLD),
                
                # Conversión a Bolívares
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("💱 → Bolívares", size=14, weight=ft.FontWeight.BOLD, color="#2e7d32"),
                            ft.Row([
                                usd_input,
                                ft.Text("=", size=16),
                                usd_result
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Row([
                                eur_input,
                                ft.Text("=", size=16),
                                eur_result
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ]),
                        padding=15,
                        bgcolor="#e8f5e8",
                        border_radius=10
                    )
                ),
                
                # Conversión desde Bolívares
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Bolívares → 💱", size=14, weight=ft.FontWeight.BOLD, color="#1565c0"),
                            ft.Row([
                                bs_input
                            ], alignment=ft.MainAxisAlignment.CENTER),
                            ft.Divider(height=5),
                            ft.Row([
                                usd_from_bs,
                                ft.Text("|", size=16, color="grey"),
                                eur_from_bs
                            ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
                        ]),
                        padding=15,
                        bgcolor="#e3f2fd",
                        border_radius=10
                    )
                )
            ], expand=1)
        ], spacing=20),
        
        # Botón de actualización
        ft.Container(
            content=ft.ElevatedButton(
                "🔄 Actualizar Tasas",
                on_click=lambda e: [update_rates(e), calculate_all()],
                bgcolor="green",
                color="white",
                icon=ft.Icons.REFRESH
            ),
            alignment=ft.alignment.center
        ),
        
        # Estado y última actualización
        ft.Container(
            content=ft.Column([
                status_text,
                last_update
            ]),
            padding=15,
            bgcolor="#f0f8ff",
            border_radius=10,
            margin=ft.margin.only(top=20)
        ),
        
        # Información adicional
        ft.Container(
            content=ft.Column([
                ft.Text("ℹ️ Información", weight=ft.FontWeight.BOLD),
                ft.Text("• Las tasas se obtienen del sitio oficial del BCV"),
                ft.Text("• Si el BCV no está disponible, se usa API alternativa"),
                ft.Text("• Los datos son referenciales"),
                ft.Text("• Actualización manual requerida")
            ]),
            padding=15,
            bgcolor="#fff8dc",
            border_radius=10,
            margin=ft.margin.only(top=10),
        )
    ], 
    spacing=15,
    scroll=ft.ScrollMode.AUTO,
    expand=True
    )