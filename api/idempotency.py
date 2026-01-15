from api.db.redis_client import redis_client

IDEMPOTENCY_TTL = 300  # 5 minutes

def check_idempotency(key: str):
    exists = redis_client.get(f"idempotency:{key}")
    if exists:
        return exists
    return None

def save_idempotency(key: str, job_id: str):
    redis_client.setex(f"idempotency:{key}", IDEMPOTENCY_TTL, job_id)
