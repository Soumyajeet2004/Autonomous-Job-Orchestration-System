import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://jobuser:jobpass@localhost:5432/jobdb"
)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
QUEUE_NAME = os.getenv("QUEUE_NAME", "job_queue")

JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key")

RATE_LIMIT = int(os.getenv("RATE_LIMIT", 5))
WINDOW_SECONDS = int(os.getenv("WINDOW_SECONDS", 60))
