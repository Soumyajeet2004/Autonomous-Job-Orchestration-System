import time
import random
from common.logger import logger

def execute_job(job_type: str, payload: dict) -> dict:
    delay = payload.get("delay_seconds", 20)
    if payload.get("force_stuck") is True:
        logger.info("[EXECUTOR] Simulating stuck job")
        while True:
            pass  # infinite loop

# Example of how to test a stuck job via API:        
#     Invoke-RestMethod `
#   -Uri "http://127.0.0.1:8000/jobs" `
#   -Method POST `
#   -ContentType "application/json" `
#   -Body '{"job_type":"timeout_test","payload":{"force_stuck": true},"timeout_seconds":5}'
    
    logger.info(f"[EXECUTOR] Executing job, sleeping for {delay} seconds")
    time.sleep(delay)

    # Simulate failure (30% chance)
    if random.random() < 0.3:
        raise Exception("Simulated job failure")
    
#     if payload.get("force_fail") is True:
#         raise Exception("Forced failure for testing")
    
# Example of how to test a failing job via API:
#     Invoke-RestMethod `
#   -Uri "http://127.0.0.1:8000/jobs" `
#   -Method POST `
#   -ContentType "application/json" `
#   -Body '{"job_type":"test","payload":{"force_fail": true}}'

    return {
        "job_type": job_type,
        "input": payload,
        "message": f"Job executed after {delay} seconds"
    }
