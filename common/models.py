from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    
    user_id = Column(String, nullable=False)
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_type = Column(String, nullable=False)
    worker_id = Column(String, nullable=True)
    payload = Column(JSON, nullable=False)   # INPUT
    result = Column(JSON, nullable=True)     # OUTPUT
    status = Column(String, nullable=False)
    attempts = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    timeout_seconds = Column(Integer, default=120)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    last_error = Column(String, nullable=True)
