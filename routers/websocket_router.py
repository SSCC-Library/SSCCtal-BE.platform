from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio

router = APIRouter()

esp32_ws: WebSocket = None  # 단일 ESP32만 지원
viewer_clients = set()      # 영상 보는 클라이언트들

@router.websocket("/ws/esp32/stream")
async def esp32_stream(websocket: WebSocket):
    global esp32_ws
    await websocket.accept()
    esp32_ws = websocket
    try:
        while True:
            msg = await websocket.receive()
            if msg.get("type") == "websocket.receive":
                if msg.get("bytes") is not None:
                    frame = msg["bytes"]
                    # 영상 시청자들에게 브로드캐스트
                    for viewer in list(viewer_clients):
                        try:
                            await viewer.send_bytes(frame)
                        except Exception as e:
                            viewer_clients.discard(viewer)
                elif msg.get("text") is not None:
                    pass # 필요시 로그
    except Exception as e:
        esp32_ws = None

@router.websocket("/api/v0/ws/video")
async def video_ws(websocket: WebSocket):
    global esp32_ws
    await websocket.accept()
    viewer_clients.add(websocket)
    try:
        while True:
            msg = await websocket.receive()
            if msg.get("type") == "websocket.receive":
                if msg.get("text") == "stop":
                    # FE에서 stop 요청 → ESP32에 stop 명령 전송
                    if esp32_ws:
                        await esp32_ws.send_text("stop")
                elif msg.get("text") == "start":
                    # FE에서 start 요청 → ESP32에 start 명령 전송
                    if esp32_ws:
                        await esp32_ws.send_text("start")
            elif msg.get("type") == "websocket.disconnect":
                break
    except WebSocketDisconnect:
        pass
    finally:
        viewer_clients.discard(websocket)