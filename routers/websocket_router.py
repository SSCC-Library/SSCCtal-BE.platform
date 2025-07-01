from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from database import SessionLocal  # 실제 세션 생성 함수 import
from models.item import Item      # 실제 모델 import
from schemas.item import ItemResponse  # 실제 pydantic 스키마 import
from services.barcode_recognizer import recognize_barcodes
import json

router = APIRouter()

esp32_ws: WebSocket = None  # 단일 ESP32만 지원
viewer_clients = set()      # 영상 보는 클라이언트들

# DB에서 바코드로 조회하는 함수
def get_item_by_barcode(db: Session, barcode: str):
    db_item = db.query(Item).filter(Item.isbn == barcode).first()
    if not db_item:
        return {
            "success": False,
            "code": 404,
            "item_id": None,
            "title": None,
            "status": None,
            "img": None
        }
    return {
        "success": True,
        "code": 200,
        "item_id": db_item.id,
        "title": db_item.name,               # 필드명은 실제 모델에 맞게
        "status": db_item.is_available,      # Enum/Bool 등 실제 모델에 맞게
        "img": db_item.img                  # 이미지 URL 등
    }

@router.websocket("/ws/esp32/stream")
async def esp32_stream(websocket: WebSocket):
    global esp32_ws
    db = SessionLocal()
    await websocket.accept()
    esp32_ws = websocket
    try:
        while True:
            msg = await websocket.receive()
            if msg.get("type") == "websocket.receive":
                if msg.get("bytes") is not None:
                    frame = msg["bytes"]

                    # 바코드/QR 인식
                    recognized, _ = recognize_barcodes(frame, draw_rect=False)
                    for r in recognized:
                        barcode_data = r['data']
                        print(f"\n✅ [인식됨] {r['type']}: {barcode_data} 위치={r['rect']}")
                        
                        # DB에서 조회
                        item_info = get_item_by_barcode(db, barcode_data)
                        response = ItemResponse(**item_info)

                        # 모든 시청자에게 결과 전송 (JSON)
                        for viewer in list(viewer_clients):
                            try:
                                await viewer.send_text(response.json())
                            except Exception:
                                viewer_clients.discard(viewer)

                        # 인식 결과 있으면 ESP32에 정지 신호 전송
                        if recognized and esp32_ws:
                            print("❗ 바코드 인식됨 → ESP32에 스트리밍 정지 신호 전송")
                            await esp32_ws.send_text("stop")
                            # break (필요시)

                    # 영상 프레임도 시청자에게 브로드캐스트
                    for viewer in list(viewer_clients):
                        try:
                            await viewer.send_bytes(frame)
                        except Exception:
                            viewer_clients.discard(viewer)
                elif msg.get("text") is not None:
                    pass
    except Exception as e:
        esp32_ws = None
    finally:
        db.close()

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
