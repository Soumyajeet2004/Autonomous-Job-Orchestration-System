from fastapi import APIRouter
from api.db.database import SessionLocal
from api.metrics import (
    get_queue_length,
    get_job_counts,
    get_avg_latency,
    get_throughput
)

router = APIRouter()

@router.get("/metrics")
def system_metrics():
    db = SessionLocal()

    data = {
        "queue_length": get_queue_length(),
        "job_counts": get_job_counts(db),
        "avg_execution_time_seconds": get_avg_latency(db),
        "throughput": get_throughput(db, window_minutes=1)
    }

    db.close()
    return data
