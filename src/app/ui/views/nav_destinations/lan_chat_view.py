import flet as ft
import socket
import threading
import os
import json
import time
from datetime import datetime
try:
    from src.utils.network_utils import get_local_ip
except:
    def get_local_ip():
        return "127.0.0.1"

class LANChatView:
    def __init__(self, page):
        self.page = page
        self.socket = None
        self.is_server = False
        self.is_connected = False
        self.username = "Usuario"
        
        # UI Components
        self.chat_messages = ft.ListView(expand=True, spacing=5, auto_scroll=True)
        self.message_input = ft.TextField(
            hint_text="Escribe tu mensaje...",
            expand=True,
            on_submit=self.send_message,
            multiline=True,
            max_lines=3
        )
        self.status_text = ft.Text("Desconectado", color="red", size=12)
        self.file_picker = ft.FilePicker(on_result=self.handle_file_selection)
        page.overlay.append(self.file_picker)
        
    def create_view(self):
        # Configuración inicial
        config_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("🌐 Chat LAN - PLAF System", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.TextField(
                            label="Tu nombre",
                            value=self.username,
                            width=150,
                            on_change=lambda e: setattr(self, 'username', e.control.value)
                        ),
                        self.status_text
                    ]),
                    ft.Row([
                        ft.ElevatedButton(
                            "🖥️ Crear Servidor",
                            on_click=self.start_server,
                            bgcolor="green",
                            color="white"
                        ),
                        ft.ElevatedButton(
                            "🔌 Conectar",
                            on_click=self.show_connect_dialog,
                            bgcolor="blue",
                            color="white"
                        ),
                        ft.ElevatedButton(
                            "❌ Desconectar",
                            on_click=self.disconnect,
                            bgcolor="red",
                            color="white"
                        )
                    ])
                ], spacing=10),
                padding=15
            )
        )
        
        # Área de chat
        chat_section = ft.Container(
            content=self.chat_messages,
            expand=True,
            bgcolor="#f5f5f5",
            border_radius=10,
            padding=10
        )
        
        # Input de mensaje
        input_section = ft.Row([
            self.message_input,
            ft.IconButton(
                ft.Icons.ATTACH_FILE,
                tooltip="Enviar archivo",
                on_click=lambda e: self.file_picker.pick_files(
                    dialog_title="Seleccionar archivo",
                    allow_multiple=False
                )
            ),
            ft.IconButton(
                ft.Icons.SEND,
                tooltip="Enviar mensaje",
                on_click=self.send_message,
                bgcolor="blue",
                icon_color="white"
            )
        ])
        
        return ft.Column([
            config_section,
            chat_section,
            ft.Container(
                content=input_section,
                padding=10,
                bgcolor="white",
                border=ft.border.all(1, "#cccccc")
            )
        ], expand=True)
    
    def add_message(self, message, sender="Sistema", msg_type="text", is_own=False):
        timestamp = datetime.now().strftime("%H:%M")
        
        if msg_type == "file":
            icon = ft.Icons.ATTACH_FILE
            color = "orange"
        elif sender == "Sistema":
            icon = ft.Icons.INFO
            color = "grey"
        else:
            icon = ft.Icons.PERSON
            color = "blue" if is_own else "green"
        
        message_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, size=16, color=color),
                        ft.Text(f"{sender} - {timestamp}", size=12, weight=ft.FontWeight.BOLD),
                    ]),
                    ft.Text(message, size=14)
                ], spacing=5),
                padding=10,
                bgcolor="#e3f2fd" if is_own else "#e8f5e8"
            ),
            margin=ft.margin.only(left=50 if is_own else 0, right=0 if is_own else 50)
        )
        
        self.chat_messages.controls.append(message_card)
        self.page.update()
    
    def start_server(self, e):
        if self.is_connected:
            self.add_message("⚠️ Ya hay una conexión activa")
            return
            
        self.add_message("🚀 Iniciando servidor...")
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Usar localhost para test local
            local_ip = "127.0.0.1"
            self.add_message(f"🔧 Intentando bind en {local_ip}:8888")
            
            self.socket.bind((local_ip, 8888))
            self.socket.listen(1)
            
            self.is_server = True
            self.is_connected = True
            self.status_text.value = f"Servidor activo en {local_ip}:8888"
            self.status_text.color = "green"
            
            self.add_message(f"✅ Servidor iniciado en {local_ip}:8888")
            self.add_message("⏳ Esperando conexión de cliente...")
            
            # Esperar conexión en hilo separado
            threading.Thread(target=self.accept_connection, daemon=True).start()
            
        except Exception as ex:
            self.add_message(f"❌ Error al iniciar servidor: {str(ex)}")
            self.status_text.value = "Error al iniciar servidor"
            self.status_text.color = "red"
        
        self.page.update()
    
    def accept_connection(self):
        try:
            self.add_message("🔍 Esperando cliente...")
            client_socket, addr = self.socket.accept()
            
            # Cerrar socket servidor y usar socket cliente
            server_socket = self.socket
            self.socket = client_socket
            server_socket.close()
            
            self.add_message(f"🎉 Cliente conectado desde {addr[0]}")
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as ex:
            self.add_message(f"❌ Error en accept_connection: {str(ex)}")
    
    def show_connect_dialog(self, e):
        # Debug: agregar mensaje para verificar que se ejecuta
        self.add_message("🔍 Intentando abrir diálogo de conexión...")
        
        if self.is_connected:
            self.add_message("Ya hay una conexión activa")
            return
            
        ip_field = ft.TextField(label="IP del servidor", value="127.0.0.1")
        
        def connect_to_server(e):
            try:
                ip = ip_field.value.strip()
                if not ip:
                    self.add_message("Ingresa una IP válida")
                    return
                
                self.add_message(f"🔌 Intentando conectar a {ip}:8888...")
                
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((ip, 8888))
                self.socket.settimeout(None)  # Sin timeout para recepción
                
                self.is_connected = True
                self.status_text.value = f"Conectado a {ip}:8888"
                self.status_text.color = "green"
                
                self.add_message(f"✅ Conectado al servidor {ip}")
                
                # Iniciar recepción de mensajes
                threading.Thread(target=self.receive_messages, daemon=True).start()
                
                # Cerrar diálogo
                self.page.close(dialog)
                
            except Exception as ex:
                self.add_message(f"❌ Error de conexión: {str(ex)}")
                self.add_message("💡 Asegúrate de que el servidor esté ejecutándose primero")
                self.status_text.value = "Error de conexión"
                self.status_text.color = "red"
                self.page.update()
        
        def close_dialog(e):
            try:
                self.page.close(dialog)
            except:
                pass
        
        try:
            dialog = ft.AlertDialog(
                title=ft.Text("Conectar al servidor"),
                content=ft.Column([
                    ip_field,
                    ft.Text("Puerto: 8888", size=12)
                ], height=100),
                actions=[
                    ft.TextButton("Cancelar", on_click=close_dialog),
                    ft.ElevatedButton("Conectar", on_click=connect_to_server)
                ]
            )
            
            # Usar page.open() en lugar de dialog.open
            self.page.open(dialog)
            self.add_message("✅ Diálogo abierto con page.open()")
            
        except Exception as ex:
            self.add_message(f"❌ Error al crear diálogo: {str(ex)}")
            # Fallback: conectar directamente a localhost
            self.add_message("🔄 Conectando directamente a 127.0.0.1:8888...")
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect(("127.0.0.1", 8888))
                self.is_connected = True
                self.status_text.value = "Conectado a 127.0.0.1:8888"
                self.status_text.color = "green"
                self.add_message("Conectado al servidor 127.0.0.1")
                threading.Thread(target=self.receive_messages, daemon=True).start()
            except Exception as conn_ex:
                self.add_message(f"Error de conexión: {str(conn_ex)}")
    
    def send_message(self, e=None):
        if not self.is_connected or not self.socket:
            self.add_message("No hay conexión activa")
            return
        
        message = self.message_input.value.strip()
        if not message:
            return
        
        try:
            data = {
                "type": "message",
                "sender": self.username,
                "content": message,
                "timestamp": time.time()
            }
            
            self.socket.send((json.dumps(data) + "\n").encode('utf-8'))
            self.add_message(message, self.username, is_own=True)
            self.message_input.value = ""
            self.page.update()
            
        except Exception as ex:
            self.add_message(f"Error al enviar: {str(ex)}")
            self.disconnect()
    
    def handle_file_selection(self, e):
        if not e.files or not self.is_connected:
            return
        
        file_path = e.files[0].path
        self.send_file_direct(file_path)
    
    def send_file_direct(self, file_path):
        """Enviar archivo directamente por ruta"""
        if not self.is_connected:
            raise Exception("No hay conexión activa")
        
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        try:
            self.add_message(f"🚀 Iniciando envío: {filename} ({file_size} bytes)")
            
            # Enviar información del archivo
            file_info = {
                "type": "file_info",
                "sender": self.username,
                "filename": filename,
                "size": file_size
            }
            
            self.socket.send((json.dumps(file_info) + "\n").encode('utf-8'))
            time.sleep(0.1)  # Pequeña pausa
            
            # Enviar archivo
            bytes_sent = 0
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(4096)
                    if not data:
                        break
                    self.socket.send(data)
                    bytes_sent += len(data)
            
            # Señal de fin de archivo
            self.socket.send(b"<EOF>")
            
            self.add_message(f"✅ Archivo enviado: {filename} ({bytes_sent} bytes)", self.username, "file", True)
            
        except Exception as ex:
            self.add_message(f"Error al enviar archivo: {str(ex)}")
            raise ex
    
    def receive_messages(self):
        buffer = b""
        receiving_file = False
        file_info = None
        file_data = b""
        
        while self.is_connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                if receiving_file:
                    if data.endswith(b"<EOF>"):
                        file_data += data[:-5]  # Remover <EOF>
                        self.save_received_file(file_info, file_data)
                        receiving_file = False
                        file_data = b""
                    else:
                        file_data += data
                else:
                    buffer += data
                    
                    while b'\n' in buffer or len(buffer) > 0:
                        try:
                            if b'\n' in buffer:
                                line, buffer = buffer.split(b'\n', 1)
                            else:
                                line = buffer
                                buffer = b""
                            
                            if not line:
                                continue
                                
                            message_data = json.loads(line.decode('utf-8'))
                            
                            if message_data["type"] == "message":
                                self.add_message(
                                    message_data["content"],
                                    message_data["sender"]
                                )
                            elif message_data["type"] == "file_info":
                                file_info = message_data
                                receiving_file = True
                                self.add_message(
                                    f"📎 Recibiendo archivo: {file_info['filename']} ({file_info['size']} bytes)",
                                    file_info["sender"],
                                    "file"
                                )
                            break
                            
                        except json.JSONDecodeError:
                            break
                        except UnicodeDecodeError:
                            buffer = b""
                            break
                            
            except Exception as ex:
                if self.is_connected:
                    self.add_message(f"Error de conexión: {str(ex)}")
                    self.disconnect()
                break
    
    def save_received_file(self, file_info, file_data):
        try:
            # Crear carpeta "recibidos" en PLAF_system
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            plaf_system_path = os.path.join(desktop_path, "PLAF_system")
            recibidos_dir = os.path.join(plaf_system_path, "recibidos")
            os.makedirs(recibidos_dir, exist_ok=True)
            
            # Guardar archivo
            file_path = os.path.join(recibidos_dir, file_info["filename"])
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            self.add_message(
                f"📎 Archivo recibido: {file_info['filename']}\nGuardado en: Desktop/PLAF_system/recibidos/",
                file_info["sender"],
                "file"
            )
            
            # Debug: verificar que se guardó
            if os.path.exists(file_path):
                self.add_message(f"✅ Confirmado: Archivo guardado correctamente")
            else:
                self.add_message(f"❌ Error: No se pudo guardar el archivo")
            
        except Exception as ex:
            self.add_message(f"Error al guardar archivo: {str(ex)}")
            self.add_message(f"Debug: Ruta intentada: Desktop/PLAF_system/recibidos/")
    
    def disconnect(self, e=None):
        self.is_connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        self.status_text.value = "Desconectado"
        self.status_text.color = "red"
        self.add_message("Desconectado del chat")
        self.page.update()

def create_lan_chat_view(page):
    chat_view = LANChatView(page)
    return chat_view.create_view()