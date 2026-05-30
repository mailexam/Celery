import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from tasks import send_test_email

load_dotenv()

app = Flask(__name__)


@app.post("/mail/test")
def mail_test():
    data = request.get_json(force=True, silent=True) or {}
    result = send_test_email.delay(
        to=data.get("to", "user@example.test"),
        subject=data.get("subject", "Celery + Mailexam"),
        body=data.get("body", data.get("text", "Mailexam test from Celery")),
    )
    return jsonify({"status": "ok", "task_id": result.id})


if __name__ == "__main__":
    host = os.environ.get("HTTP_HOST", "127.0.0.1")
    port = int(os.environ.get("HTTP_PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)
