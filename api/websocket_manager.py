from typing import Dict, List
from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, job_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(job_id, []).append(websocket)

    def disconnect(self, job_id: str, websocket: WebSocket):
        self.active_connections[job_id].remove(websocket)
        if not self.active_connections[job_id]:
            del self.active_connections[job_id]

    async def send_update(self, job_id: str, message: dict):
        for ws in self.active_connections.get(job_id, []):
            await ws.send_json(message)
