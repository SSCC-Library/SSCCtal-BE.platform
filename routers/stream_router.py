from fastapi import APIRouter
from services.websocket_controller import send_start_command
from schemas.item import ItemResponse

router = APIRouter()

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