from sqlalchemy.orm import Session
from sqlalchemy import func
from common.models import Job
from api.db.redis_client import redis_client, QUEUE_NAME
from datetime import datetime, timedelta

def get_queue_length():
    return redis_client.llen(QUEUE_NAME)

def get_job_counts(db: Session):
    return {
        "queued": db.query(Job).filter(Job.status == "QUEUED").count(),
        "running": db.query(Job).filter(Job.status == "RUNNING").count(),
        "retrying": db.query(Job).filter(Job.status == "RETRYING").count(),
        "completed": db.query(Job).filter(Job.status == "COMPLETED").count(),
        "failed": db.query(Job).filter(Job.status == "FAILED").count(),
    }

def get_avg_latency(db: Session):
    jobs = db.query(Job).filter(
        Job.finished_at.isnot(None),
        Job.started_at.isnot(None)
    ).all()

    if not jobs:
        return 0

    latencies = [
        (job.finished_at - job.started_at).total_seconds()
        for job in jobs
    ]

    return round(sum(latencies) / len(latencies), 2)

def get_throughput(db: Session, window_minutes: int = 1):
    window_start = datetime.utcnow() - timedelta(minutes=window_minutes)

    completed_count = db.query(Job).filter(
        Job.status == "COMPLETED",
        Job.finished_at >= window_start
    ).count()

    return {
        "jobs_per_minute": completed_count,
        "window_minutes": window_minutes
    }