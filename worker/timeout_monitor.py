# SQLAlchemy engine creation for database connectivity
from sqlalchemy import create_engine

# Session factory to manage DB transactions
from sqlalchemy.orm import sessionmaker

# Used for time comparison and timeout calculation
from datetime import datetime, timedelta

# Job ORM model (represents jobs table)
from common.models import Job

# Redis client library
import redis

# Used to pause execution between checks
import time
from api.config import DATABASE_URL, REDIS_HOST, REDIS_PORT, QUEUE_NAME
from common.logger import logger

# =========================
# DATABASE SETUP
# =========================

# Create SQLAlchemy engine (connection factory)
engine = create_engine(DATABASE_URL)

# Create session factory for DB access
SessionLocal = sessionmaker(bind=engine)

# =========================
# REDIS SETUP
# =========================

# Create Redis client
# decode_responses=True ensures Redis returns strings instead of bytes
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)
# =========================
# MONITOR CONFIGURATION
# =========================

# How often the timeout monitor runs (in seconds)
CHECK_INTERVAL = 10


# =========================
# TIMEOUT CHECK LOGIC
# =========================

def check_timed_out_jobs():
    """
    Scans all RUNNING jobs and checks whether they have exceeded
    their allowed execution time (timeout_seconds).

    If a job times out:
    - Retry it if retries remain
    - Otherwise mark it FAILED
    """

    # Open a new database session
    db = SessionLocal()

    # Current time (used to calculate elapsed execution time)
    # NOTE: utcnow() is used here; later we should move to timezone-aware UTC
    now = datetime.utcnow()

    # Fetch all jobs that are currently RUNNING
    running_jobs = db.query(Job).filter(Job.status == "RUNNING").all()

    # Iterate over all running jobs
    for job in running_jobs:
        # Calculate how long the job has been running
        elapsed = (now - job.started_at).total_seconds()

        # Check if job exceeded its timeout limit
        if elapsed > job.timeout_seconds:
            # Increment retry attempt counter
            job.attempts += 1

            # Store timeout error message
            job.last_error = "Job timed out"

            # If retries are still allowed
            if job.attempts <= job.max_retries:
                # Mark job as RETRYING
                job.status = "RETRYING"

                # Persist DB changes
                db.commit()

                # Push job back into Redis queue for retry
                redis_client.rpush(QUEUE_NAME, job.id)

                logger.info(f"[TIMEOUT] Job {job.id} timed out. Retrying.")

            else:
                # No retries left → permanently fail job
                job.status = "FAILED"

                # Persist DB changes
                db.commit()

                logger.error(f"[TIMEOUT] Job {job.id} permanently failed.")

    # Close database session
    db.close()


# =========================
# MONITOR MAIN LOOP
# =========================

def main():
    """
    Entry point for the timeout monitor service.

    Runs forever:
    - Periodically checks for timed-out jobs
    - Sleeps for CHECK_INTERVAL seconds
    """

    print("[TIMEOUT MONITOR] Started.")

    while True:
        # Perform timeout check
        check_timed_out_jobs()

        # Sleep before next scan
        time.sleep(CHECK_INTERVAL)


# =========================
# SCRIPT ENTRY POINT
# =========================

if __name__ == "__main__":
    # Start the timeout monitoring service
    main()
