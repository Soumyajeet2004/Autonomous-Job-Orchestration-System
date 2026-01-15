from datetime import datetime, timedelta
from api.db.database import SessionLocal
from common.models import Job
from api.db.redis_client import redis_client, QUEUE_NAME

STALE_THRESHOLD_MINUTES = 5

def recover_stale_jobs():
    db = SessionLocal()
    cutoff = datetime.utcnow() - timedelta(minutes=STALE_THRESHOLD_MINUTES)

    stale_jobs = db.query(Job).filter(
        Job.status == "RUNNING",
        Job.started_at < cutoff
    ).all()

    for job in stale_jobs:
        job.status = "QUEUED"
        job.worker_id = None
        db.commit()
        redis_client.rpush(QUEUE_NAME, job.id)

    db.close()
