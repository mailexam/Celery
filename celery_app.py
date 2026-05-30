import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

app = Celery(
    "mailexam",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    include=["tasks"],
)
