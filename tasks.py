from celery_app import app
from mail import send_test


@app.task(name="mail.send_test")
def send_test_email(
    to: str = "user@example.test",
    subject: str = "Celery + Mailexam",
    body: str = "Mailexam test from Celery",
) -> dict:
    send_test(to=to, subject=subject, body=body)
    return {"status": "ok", "to": to}
