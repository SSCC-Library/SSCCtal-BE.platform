from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from services.websocket_controller import set_websocket, compelete_streaming, notify_started, send_start_command
from schemas.item import ItemResponse

router = APIRouter()

@router.websocket("/api/v0/ws/esp32/video")
async def esp32_video_ws(websocket: WebSocket):
    await websocket.accept()
    set_websocket(websocket)

    started = False
    timeout_task = None

    try:
        while True:
            if not started:
                data = await websocket.receive_text()
                print(f"[ESP32] 수신 메시지: {data}")
                if data == "started":
                    print("✅ 스트리밍 시작 신호 수신됨")
                    started = True
                    notify_started()
                    timeout_task = asyncio.create_task(asyncio.sleep(10))
                continue

            receive_task = asyncio.create_task(websocket.receive())
            done, _ = await asyncio.wait(
                {receive_task, timeout_task},
                return_when=asyncio.FIRST_COMPLETED
            )

            if timeout_task in done:
                print("⏰ 10초 초과로 종료")
                await websocket.send_text("stop")
                await websocket.close()
                compelete_streaming()
                break
            if receive_task in done:
                message = receive_task.result()
                if "bytes" in message:
                    print(f"📷 프레임 수신됨 ({len(message['bytes'])} bytes)")

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
    except Exception as e:
        print("[예외 발생]", repr(e))
        return ItemResponse(
            success=False,
            code=500
        )