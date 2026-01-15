# Import the Redis client library
# This allows Python code to communicate with a Redis server
import redis


# Create a Redis client instance
# This object is reused wherever we need to interact with Redis
redis_client = redis.Redis(
    host="localhost",      # Redis server address
    port=6379,             # Default Redis port
    decode_responses=True  # Convert Redis bytes to Python strings
)


# Name of the Redis queue (LIST data structure)
# This key holds job IDs waiting to be processed by workers
QUEUE_NAME = "job_queue"
