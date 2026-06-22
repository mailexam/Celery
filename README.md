# Celery + Mailexam

Minimal [Celery](https://docs.celeryq.dev/) example that sends test mail through [Mailexam](https://mailexam.io/) SMTP via a background worker and `smtplib`.

Based on the [Mailexam Celery guide](https://wiki.mailexam.ru/en/examples/celery/).

## What you need

- A Mailexam account and a project with SMTP credentials.
- Python 3.10+ and pip.
- A message broker — [Redis](https://redis.io/) (included in Docker Compose below).

From your Mailexam welcome email or dashboard:

| Variable | Description |
|----------|-------------|
| `MAILEXAM_LOGIN` | SMTP login (for example, `xxxxx`) |
| `MAILEXAM_PASSWORD` | SMTP password (paired with the login) |
| Host | `{MAILEXAM_LOGIN}.mailexam.io` (built in `mail.py`) |

## Quick start (host)

1. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

3. Edit `.env`:

```env
CELERY_BROKER_URL=redis://localhost:6379/0
MAILEXAM_LOGIN=YOUR_LOGIN
MAILEXAM_PASSWORD=YOUR_PASSWORD
MAILEXAM_PORT=587
MAIL_FROM=noreply@example.test
```

4. Start Redis (if not already running):

```bash
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

5. Start the Celery worker (terminal 1):

```bash
celery -A celery_app worker --loglevel=info
```

6. Start the HTTP app (terminal 2):

```bash
python app.py
```

The app listens on `http://127.0.0.1:5000` by default.

7. Send a test message (enqueues a Celery task):

```bash
curl -X POST http://127.0.0.1:5000/mail/test \
  -H 'Content-Type: application/json' \
  -d '{"to":"user@example.test","subject":"Test","body":"Hello"}'
```

The worker sends the message; it appears in the Mailexam dashboard → your project → inbox.

### Enqueue without HTTP

```bash
python -c "from tasks import send_test_email; print(send_test_email.delay().id)"
```

Or from the Celery shell:

```bash
celery -A celery_app shell
```

```python
from tasks import send_test_email
send_test_email.delay(
    to="user@example.test",
    subject="Test",
    body="Hello from the queue",
)
```

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CELERY_BROKER_URL` | no | `redis://localhost:6379/0` | Redis broker URL |
| `MAILEXAM_LOGIN` | yes | — | SMTP login; also used to build the host name |
| `MAILEXAM_PASSWORD` | yes | — | SMTP password |
| `MAILEXAM_PORT` | no | `587` | SMTP port (`587`, `2525`, or `25`) |
| `MAIL_FROM` | no | `noreply@example.test` | Sender address (any test address is fine) |
| `HTTP_HOST` | no | `127.0.0.1` | HTTP bind address |
| `HTTP_PORT` | no | `5000` | HTTP listen port |

For port **587** the worker calls `starttls()` before login. For port **25** it connects without STARTTLS.

## Project layout

```
.
├── requirements.txt
├── mail.py              # smtplib transport and send_test()
├── celery_app.py        # Celery application
├── tasks.py             # mail.send_test task
├── app.py               # POST /mail/test (enqueues task)
├── .env.example
├── Dockerfile           # for local debugging only
└── docker-compose.yml   # redis + worker + app
```

## Docker (debugging)

Docker is provided for local debugging. For day-to-day development, run Redis, the worker, and the app on the host (see above).

```bash
cp .env.example .env
# edit .env with your credentials

docker compose up --build
```

Then call the same endpoint on the mapped port:

```bash
curl -X POST http://127.0.0.1:5000/mail/test \
  -H 'Content-Type: application/json' \
  -d '{"to":"user@example.test","subject":"Test","body":"Hello"}'
```

Compose starts Redis, a Celery worker, and the HTTP app on port 5000.

## CI

Set these secrets in your CI environment:

```yaml
variables:
  CELERY_BROKER_URL: redis://redis:6379/0
  MAILEXAM_LOGIN: $MAILEXAM_LOGIN
  MAILEXAM_PASSWORD: $MAILEXAM_PASSWORD
  MAILEXAM_PORT: "587"
  MAIL_FROM: "noreply@example.test"
```

For tests without broker and SMTP:

```python
app.conf.task_always_eager = True
```

After sending a message in a test, verify delivery via the [Mailexam API](https://mailexam.io/api).

## Troubleshooting

**Task stuck in PENDING**

- Ensure the worker is running: `celery -A celery_app worker --loglevel=info`.
- Check that `CELERY_BROKER_URL` matches between worker and client, and Redis is reachable.

**SMTP error in worker logs**

- Host must be `{login}.mailexam.io`; login and password must come from the same Mailexam project.
- The worker loads `.env` via `load_dotenv()` in `celery_app.py`.

**Message not in the dashboard**

- Open the inbox of the same Mailexam project.
- Check the task result: `celery -A celery_app result <task_id>`.

## See also

- [Mailexam Celery guide (wiki)](https://wiki.mailexam.ru/en/examples/celery/)
- [Flask reference implementation](https://github.com/mailexam/Flask) — same `mail.py` module
- [Django](https://github.com/mailexam/Django) — SMTP via `send_mail` in tasks
- [Sidekiq](https://github.com/mailexam/Sidekiq) — Ruby background jobs with Redis
- [BullMQ](https://github.com/mailexam/BullMQ) — Node.js background jobs with Redis
- [Celery documentation](https://docs.celeryq.dev/)
- [Mailexam API documentation](https://mailexam.io/api)

## License

Apache 2.0
