from fastapi import APIRouter, Depends, HTTPException
from api.schemas.job import JobCreate, JobStatusResponse
from api.db.database import SessionLocal
from api.db.redis_client import redis_client, QUEUE_NAME
from common.models import Job
from api.dependencies import get_current_user
from api.rate_limiter import check_rate_limit
from fastapi import Header
from api.idempotency import check_idempotency, save_idempotency
from common.logger import logger

router = APIRouter()

@router.post("/jobs")
def create_job(
    job: JobCreate, 
    user_id: str = Depends(get_current_user),
    idempotency_key: str = Header(None)):
    
    db = SessionLocal()
    check_rate_limit(user_id)  # 🔒 PROTECTION HERE

    if idempotency_key:
        existing_job_id = check_idempotency(idempotency_key)
        if existing_job_id:
            return {"job_id": existing_job_id, "status": "COMPLETED"}

    new_job = Job(
        job_type=job.job_type,
        payload=job.payload,
        user_id=user_id,
        status="QUEUED",
        max_retries=job.max_retries,
        timeout_seconds=job.timeout_seconds
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    if idempotency_key:
        save_idempotency(idempotency_key, new_job.id)
    redis_client.rpush(QUEUE_NAME, new_job.id)
    
    return {
        "job_id": new_job.id,
        "status": new_job.status
    }

@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(
    job_id: str, 
    user_id: str = Depends(get_current_user)
    ):
    db = SessionLocal()

    job = db.query(Job).filter(Job.id == job_id).first()
    
    if job.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")


    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
    job_id=job.id,
    job_type=job.job_type,
    status=job.status,
    attempts=job.attempts,
    created_at=job.created_at,
    started_at=job.started_at,
    finished_at=job.finished_at,
    last_error=job.last_error,
    result=job.result
)
