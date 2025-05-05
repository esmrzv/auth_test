import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException

from app.config import settings


async def send_email(to_email: str, subject: str, body: str):
    smtp_host = settings.smtp_host
    smtp_port = settings.smtp_port
    sender_email = settings.sender_email
    sender_password = settings.sender_password

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = to_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'html'))

    try:
        async with aiosmtplib.SMTP(hostname=smtp_host, port=smtp_port, use_tls=True) as smtp:
            await smtp.login(sender_email, sender_password)
            await smtp.send_message(message)
        print(f'имайл отправлен на {to_email}')
    except Exception as e:
        print(f'failed to send email: {e}')
        raise HTTPException(
            status_code=500,
            detail='failed to send email'
        )


