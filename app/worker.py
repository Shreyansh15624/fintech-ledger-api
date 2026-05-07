from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Using the existing redis container as both the message broker and the result backend
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

celery_app = Celery(
    "fintech_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks"] # This tells Celery where to look for the background jobs 
)

# Standardized date formats
celery_app.conf.update(
    task_serializers="json",
    result_serializers="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)