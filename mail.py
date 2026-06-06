import os
import smtplib
from email.message import EmailMessage


def smtp_host() -> str:
    login = os.environ["MAILEXAM_LOGIN"]
    return f"{login}.mailexam.io"


def send_test(*, to: str, subject: str, body: str) -> None:
    login = os.environ["MAILEXAM_LOGIN"]
    password = os.environ["MAILEXAM_PASSWORD"]
    port = int(os.environ.get("MAILEXAM_PORT", "587"))
    mail_from = os.environ.get("MAIL_FROM", "noreply@example.test")

    msg = EmailMessage()
    msg["From"] = mail_from
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(smtp_host(), port, timeout=30) as smtp:
        if port in (587, 2525):
            smtp.starttls()
        smtp.login(login, password)
        smtp.send_message(msg)
