from fastapi import FastAPI
from api.db.database import create_tables, test_connection
from api.routes.jobs import router as jobs_router
from api.routes.metrics import router as metrics_router
from api.redis_listener import start_redis_listener
from api.routes.ws import manager
from api.routes.ws import router as ws_router
from api.recovery import recover_stale_jobs
import threading

app = FastAPI()

create_tables()

app.include_router(jobs_router)
app.include_router(metrics_router)
app.include_router(ws_router)

@app.on_event("startup")
def startup_event():
    recover_stale_jobs()
    
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/db-check")
def db_check():
    try:
        test_connection()
        return {"database": "connected"}
    except Exception as e:
        return {"database": "error", "detail": str(e)}

@app.on_event("startup")
def startup_event():
    thread = threading.Thread(
        target=start_redis_listener,
        args=(manager,),
        daemon=True
    )
    thread.start()