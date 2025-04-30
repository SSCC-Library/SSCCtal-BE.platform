from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.websocket_controller import set_websocket, send_start_command
from schemas.item import ItemResponse

router = APIRouter()

@router.websocket("/api/v0/ws/esp32/video")
async def esp32_video_ws(websocket: WebSocket):
    await websocket.accept()
    set_websocket(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"[ESP32] 수신 메시지: {data}")
    except WebSocketDisconnect:
        print("[ESP32] 연결 해제됨")
        set_websocket(None)

@router.post("/api/v0/stream/start")
async def start_stream():
    try:
        result = await send_start_command()
        return result
    except TimeoutError:
        return ItemResponse(
            success=False,
            code=504
        )
    except Exception:
        return ItemResponse(
            success=False,
            code=500
        )