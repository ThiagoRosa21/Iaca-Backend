import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def enviar_email(destinatario: str, assunto: str, corpo: str, anexo_pdf: str = None):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = destinatario
    msg["Subject"] = assunto

    msg.attach(MIMEText(corpo, "plain"))


    if anexo_pdf and os.path.exists(anexo_pdf):
        with open(anexo_pdf, "rb") as file:
            pdf = MIMEApplication(file.read(), _subtype="pdf")
            pdf.add_header('Content-Disposition', 'attachment', filename=os.path.basename(anexo_pdf))
            msg.attach(pdf)

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as servidor:
        servidor.starttls()
        servidor.login(EMAIL_USER, EMAIL_PASS)
        servidor.send_message(msg)
