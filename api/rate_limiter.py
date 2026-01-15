import time
from fastapi import HTTPException
from api.db.redis_client import redis_client
from api.config import RATE_LIMIT, WINDOW_SECONDS

def check_rate_limit(user_id: str):
    key = f"rate_limit:{user_id}"
    current = redis_client.incr(key)

    if current == 1:
        redis_client.expire(key, WINDOW_SECONDS)

    if current > RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Too many job submissions. Please retry later."
        )
