from schemas.item import ItemResponse
import asyncio

connected_websocket = None

def set_websocket(ws):
    global connected_websocket
    connected_websocket = ws

async def send_start_command():
    if connected_websocket is None:
        return ItemResponse(
            success=False,
            code=503
        )
    
    await connected_websocket.send_text("start")

    try:
        msg = await asyncio.wait_for(connected_websocket.receive_text(), timeout=3)
        if msg == "started":
            return ItemResponse(
                success=True,
                code=200
            )
        else:
            return ItemResponse(
                success=False,
                code=500
            )
    except asyncio.TimeoutError:
        return ItemResponse(
            success=False,
            code=504
        )