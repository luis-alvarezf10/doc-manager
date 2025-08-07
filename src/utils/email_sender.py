import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(mail,subject, body):
    """Envía un email con el asunto y cuerpo especificados"""
    try:
        # Configuración del servidor SMTP de Gmail
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "axiologia.plaf@gmail.com" 
        sender_password = "tewg jtor ljze qjkj"  
        recipient_email = mail
        
        # Crear mensaje
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = f"[Axiology Doc Manager] {subject}"
        
        # Agregar cuerpo del mensaje
        message.attach(MIMEText(body, "plain"))
        
        # Conectar y enviar
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        
        return True, "Email enviado exitosamente"
        
    except Exception as e:
        return False, f"Error al enviar email: {str(e)}"