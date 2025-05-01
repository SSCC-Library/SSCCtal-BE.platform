import asyncio
from schemas.item import ItemResponse

connected_websocket = None
streaming_future = None

def set_websocket(ws):
    global connected_websocket
    connected_websocket = ws

def get_websocket():
    return connected_websocket

def set_streaming_future():
    global streaming_future
    streaming_future = asyncio.get_event_loop().create_future()
    return streaming_future

def notify_started():
    global streaming_future
    if streaming_future and not streaming_future.done():
        streaming_future.set_result("started")

def compelete_streaming():
    global streaming_future
    if streaming_future and not streaming_future.done():
        streaming_future.set_result(True)

async def send_start_command():
    if connected_websocket is None:
        print("❌ WebSocket 없음 → 503 반환")
        return ItemResponse(
            success=False,
            code=503
        )

    try:
        await connected_websocket.send_text("start")
        print("📤 start 명령 전송됨")

        future = set_streaming_future()
        result = await asyncio.wait_for(future, timeout=15)

        if result == "started":
            print("✅ started 수신됨")
            return ItemResponse(
                success=True,
                code=200
            )
        elif result == "done":
            print("✅ 스트리밍 완료됨")
            return ItemResponse(
                success=True,
                code=201
            )
        else:
            print("❗ 예기치 않은 결과:", result)
            return ItemResponse(
                success=False,
                code=500
            )
    except asyncio.TimeoutError:
        print("⏱️ started 또는 종료 타임 아웃")
        return ItemResponse(
            success=False,
            code=504
        )
    except Exception as e:
        print("🔥 예외 발생:", repr(e))
        return ItemResponse(
            success=False,
            code=500
        )