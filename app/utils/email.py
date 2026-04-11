import smtplib
from email.mime.text import MIMEText
from app.core.config import settings

def send_reset_email(to_email: str, reset_link: str):
    msg = MIMEText(f"Click để reset mật khẩu: {reset_link}")
    msg["Subject"] = "Reset mật khẩu"
    msg["From"] = settings.EMAIL_USER
    msg["To"] = to_email

    server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    server.starttls()
    server.login(settings.EMAIL_USER, settings.EMAIL_PASS)
    server.send_message(msg)
    server.quit()