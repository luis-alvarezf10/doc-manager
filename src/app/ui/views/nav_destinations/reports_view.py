import flet as ft
from datetime import datetime
import json
import os

def create_reports_view(page):
    """Vista de reportes y sugerencias"""
    
    # Campo de texto para reportes
    feedback_field = ft.TextField(
        label="Reportar problema o sugerencia",
        multiline=True,
        min_lines=4,
        max_lines=8,
        width=600,
        hint_text="Describe cualquier problema, error o mejora que sugieras para la aplicación..."
    )
    
    feedback_status = ft.Text("", size=14)
    
    def save_feedback(e):
        if not feedback_field.value.strip():
            feedback_status.value = "⚠️ Escribe algo antes de enviar"
            feedback_status.color = "orange"
            page.update()
            return
            
        # Crear carpeta de reportes si no existe
        reports_dir = os.path.join(os.path.expanduser("~"), "PLAF_Reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Cargar reportes existentes
        reports_file = os.path.join(reports_dir, "reportes.json")
        reports = []
        if os.path.exists(reports_file):
            try:
                with open(reports_file, 'r', encoding='utf-8') as f:
                    reports = json.load(f)
            except:
                reports = []
        
        # Agregar nuevo reporte
        new_report = {
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "reporte": feedback_field.value.strip()
        }
        reports.append(new_report)
        
        # Guardar reportes
        try:
            with open(reports_file, 'w', encoding='utf-8') as f:
                json.dump(reports, f, ensure_ascii=False, indent=2)
            
            feedback_field.value = ""
            feedback_status.value = f"✅ Reporte guardado correctamente ({len(reports)} reportes totales)"
            feedback_status.color = "green"
        except Exception as ex:
            feedback_status.value = f"❌ Error al guardar: {str(ex)}"
            feedback_status.color = "red"
        
        page.update()
    
    def download_reports(e):
        reports_dir = os.path.join(os.path.expanduser("~"), "PLAF_Reports")
        reports_file = os.path.join(reports_dir, "reportes.json")
        
        if not os.path.exists(reports_file):
            feedback_status.value = "⚠️ No hay reportes para descargar"
            feedback_status.color = "orange"
            page.update()
            return
        
        # Crear archivo de texto legible
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        output_file = os.path.join(downloads_dir, f"Reportes_PLAF_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        try:
            with open(reports_file, 'r', encoding='utf-8') as f:
                reports = json.load(f)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("REPORTES DE LA APLICACIÓN PLAF\n")
                f.write("=" * 60 + "\n\n")
                
                for i, report in enumerate(reports, 1):
                    f.write(f"REPORTE #{i}\n")
                    f.write(f"Fecha: {report['fecha']}\n")
                    f.write(f"Contenido:\n{report['reporte']}\n")
                    f.write("-" * 40 + "\n\n")
                
                f.write(f"\nTotal de reportes: {len(reports)}\n")
                f.write(f"Archivo generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            
            feedback_status.value = f"📥 Descargado: {os.path.basename(output_file)}"
            feedback_status.color = "blue"
        except Exception as ex:
            feedback_status.value = f"❌ Error al descargar: {str(ex)}"
            feedback_status.color = "red"
        
        page.update()
    
    def clear_reports(e):
        reports_dir = os.path.join(os.path.expanduser("~"), "PLAF_Reports")
        reports_file = os.path.join(reports_dir, "reportes.json")
        
        if os.path.exists(reports_file):
            try:
                os.remove(reports_file)
                feedback_status.value = "🗑️ Todos los reportes han sido eliminados"
                feedback_status.color = "gray"
            except Exception as ex:
                feedback_status.value = f"❌ Error al limpiar: {str(ex)}"
                feedback_status.color = "red"
        else:
            feedback_status.value = "ℹ️ No hay reportes para eliminar"
            feedback_status.color = "gray"
        
        page.update()
    
    return ft.Column([
        ft.Text("📝 Sistema de Reportes y Sugerencias", size=28, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        
        ft.Container(
            content=ft.Column([
                ft.Text("💬 Enviar Reporte", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Ayúdanos a mejorar la aplicación reportando problemas o sugiriendo mejoras:", size=14, color="gray"),
                feedback_field,
                
                ft.Row([
                    ft.ElevatedButton(
                        "📤 Enviar Reporte",
                        on_click=save_feedback,
                        bgcolor="#4caf50",
                        color="white",
                        icon=ft.Icons.SEND
                    )
                ], spacing=10),
                
                feedback_status
            ]),
            padding=20,
            bgcolor="#f8f9fa",
            border_radius=10,
            margin=ft.margin.only(bottom=20)
        ),
        
        ft.Container(
            content=ft.Column([
                ft.Text("📊 Gestión de Reportes", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Opciones para administrar los reportes guardados:", size=14, color="gray"),
                
                ft.Row([
                    ft.ElevatedButton(
                        "📥 Descargar Reportes",
                        on_click=download_reports,
                        bgcolor="#2196f3",
                        color="white",
                        icon=ft.Icons.DOWNLOAD
                    ),
                    ft.ElevatedButton(
                        "🗑️ Limpiar Reportes",
                        on_click=clear_reports,
                        bgcolor="#f44336",
                        color="white",
                        icon=ft.Icons.DELETE
                    )
                ], spacing=10)
            ]),
            padding=20,
            bgcolor="#fff3e0",
            border_radius=10
        ),
        
        ft.Container(
            content=ft.Column([
                ft.Text("ℹ️ Información", weight=ft.FontWeight.BOLD),
                ft.Text("• Los reportes se guardan localmente en tu computadora"),
                ft.Text("• Puedes descargar un archivo con todos los reportes"),
                ft.Text("• Los reportes se mantienen aunque cierres la aplicación"),
                ft.Text("• El archivo se guarda en tu carpeta de Descargas")
            ]),
            padding=15,
            bgcolor="#e8f5e8",
            border_radius=10,
            margin=ft.margin.only(top=20)
        )
    ], spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)