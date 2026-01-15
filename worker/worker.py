import signal
import threading
from threading import Semaphore
from api.config import REDIS_HOST, REDIS_PORT, QUEUE_NAME, DATABASE_URL
# Redis client library to interact with Redis queue
import redis

# SQLAlchemy imports for database connection and sessions
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Job ORM model (represents jobs table)
from common.models import Job

# Function that actually executes the job logic
from worker.executor import execute_job

# Used for timezone-aware timestamps
from datetime import datetime, timezone
import json
import time
import uuid
from common.logger import logger

# =========================
# CONFIGURATION CONSTANTS
# =========================


MAX_CONCURRENT_JOBS = 2
semaphore = Semaphore(MAX_CONCURRENT_JOBS)

# Unique worker ID for tracking
WORKER_ID = str(uuid.uuid4())
shutdown_event = threading.Event()
# =========================
# REDIS CLIENT SETUP
# =========================

# Create Redis client
# decode_responses=True ensures strings instead of bytes
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)


# =========================
# DATABASE SETUP
# =========================

# Create SQLAlchemy engine (connection factory)
engine = create_engine(DATABASE_URL)

# Create session factory for DB transactions
SessionLocal = sessionmaker(bind=engine)

def publish_job_update(job_id: str, status: str):
    message = json.dumps({
        "job_id": job_id,
        "status": status
    })
    redis_client.publish("job_updates", message)
# =========================
# JOB PROCESSING FUNCTION
# =========================
def handle_shutdown(signum, frame):
    logger.info("[WORKER] Shutdown signal received. Finishing current jobs...")
    shutdown_event.set()

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

def process_job(job_id: str):
    """
    Process a single job identified by job_id.
    This function:
    - Loads the job from DB
    - Marks it RUNNING
    - Executes job logic
    - Updates status based on success or failure
    """
    # Open a new DB session
    db = SessionLocal()

    # Fetch job record from database
    job = db.query(Job).filter(Job.id == job_id).first()

    # If job does not exist, log and exit
    if not job:
        logger.info(f"[WORKER] Job {job_id} not found")
        return
    # 🔒 SAFETY CHECK — ADD THIS HERE
    if job.status not in ("QUEUED", "RETRYING"):
        logger.info(f"[WORKER] Skipping job {job.id}, status={job.status}")
        return
    logger.info(f"[WORKER] Processing job {job.id}")

    # Mark job as RUNNING
    job.status = "RUNNING"
    job.worker_id = WORKER_ID
    # Record job start time (timezone-aware UTC)
    job.started_at = datetime.now(timezone.utc)

    # Persist changes
    db.commit()
    logger.info(f"[WORKER] Job {job.id} marked RUNNING")
    publish_job_update(job.id, "RUNNING")

    try:
        # Execute the actual job logic
        # This is user-defined work (CPU / IO / etc.)
        logger.info(f"[WORKER] Waiting for execution slot: {job.id}")
        with semaphore:
            logger.info(f"[WORKER] Executing job (slot acquired): {job.id}")
            result = execute_job(job.job_type, job.payload)
        logger.info(f"[WORKER] Job finished, slot released: {job.id}")
    


        # If execution succeeds, mark job COMPLETED
        job.status = "COMPLETED"

        # Record completion time
        job.finished_at = datetime.now(timezone.utc)

        # Store result (temporary – may move elsewhere later)
        job.result = result

        # Persist changes
        db.commit()
        
        publish_job_update(job.id, "COMPLETED")

        logger.info(f"[WORKER] Job {job.id} completed")

    except Exception as e:
        # If execution fails, increment attempt counter
        job.attempts += 1

        # Store error message for debugging
        job.last_error = str(e)

        # Check if retries are still allowed
        if job.attempts <= job.max_retries:
            # Mark job as RETRYING
            job.status = "RETRYING"
            db.commit()
            publish_job_update(job.id, "RETRYING")

            logger.warning(f"[WORKER] Job {job.id} failed with error: {e}. Retrying (attempt {job.attempts}/{job.max_retries})")

            # Push job ID back into Redis queue for retry
            redis_client.rpush(QUEUE_NAME, job.id)

        else:
            # If retries exhausted, mark job as FAILED
            job.status = "FAILED"
            db.commit()
            publish_job_update(job.id, "FAILED")

            logger.error(f"[WORKER] Job {job.id} permanently failed.")

    finally:
        # Always close DB session
        db.close()


# =========================
# WORKER MAIN LOOP
# =========================

def main():
    """
    Worker entry point.
    Continuously waits for jobs from Redis queue
    and processes them one by one.
    """

    logger.info("[WORKER] Worker started. Waiting for jobs...")

    while not shutdown_event.is_set():
        job = redis_client.blpop(QUEUE_NAME, timeout=5)

        if job:
            process_job(job[1])


# =========================
# SCRIPT ENTRY POINT
# =========================

if __name__ == "__main__":
    # Start the worker process
    main()
