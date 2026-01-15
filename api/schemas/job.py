from pydantic import BaseModel
from typing import Dict
from typing import Optional
from datetime import datetime

class JobCreate(BaseModel):
    job_type: str
    payload: Dict
    max_retries: int = 3
    timeout_seconds: int = 120
class JobStatusResponse(BaseModel):
    job_id: str
    job_type: str
    status: str
    attempts: int
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    last_error: Optional[str]
    result: Optional[dict]