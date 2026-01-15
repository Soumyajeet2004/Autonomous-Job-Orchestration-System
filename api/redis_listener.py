import json
import threading
import redis
from api.websocket_manager import WebSocketManager

REDIS_HOST = "localhost"
REDIS_PORT = 6379

def start_redis_listener(manager: WebSocketManager):
    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    pubsub = client.pubsub()
    pubsub.subscribe("job_updates")

    for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            job_id = data["job_id"]

            # Push to all WebSocket clients subscribed to this job
            import asyncio
            asyncio.run(manager.send_update(job_id, data))
