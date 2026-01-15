from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.websocket_manager import WebSocketManager
from jose import jwt, JWTError
from api.auth import SECRET_KEY, ALGORITHM
from api.db.database import SessionLocal
from common.models import Job
from common.logger import logger

router = APIRouter()
manager = WebSocketManager()

@router.websocket("/ws/jobs/{job_id}")
async def job_updates(websocket: WebSocket, job_id: str):
    logger.info("🔥 WebSocket connection attempt for job:", job_id)

    # 1️⃣ Extract token from query params
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    # 2️⃣ Decode token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        await websocket.close(code=1008)
        return

    # 3️⃣ Load job from DB
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    db.close()

    if not job:
        await websocket.close(code=1008)
        return

    # 4️⃣ Authorization check (ownership)
    if job.user_id != user_id:
        await websocket.close(code=1008)
        return

    # 5️⃣ Accept WebSocket
    await manager.connect(job_id, websocket)

    try:
        while True:
            await websocket.receive_text()  # keep alive
    except WebSocketDisconnect:
        manager.disconnect(job_id, websocket)
