from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter, Depends
from fastapi.responses import HTMLResponse
import asyncio, time, json
from typing import Optional, Set
from io import BytesIO
from models.item import Item
from models.item_copy import ItemCopy
from sqlalchemy.orm import Session
from database import get_db

# --- 바코드 인식 (OpenCV는 선택, pyzbar+PIL만으로도 동작) ---
try:
    import cv2  # 선택적
    _HAS_CV2 = True
except Exception:
    _HAS_CV2 = False

from pyzbar.pyzbar import decode as zbar_decode
from PIL import Image

router = APIRouter(prefix="/websocket",tags=["ws"])

# -------------------------
# 글로벌 상태 (단일 ESP32 가정)
# -------------------------
esp32_ctrl_ws: Optional[WebSocket] = None     # ESP32 컨트롤 소켓
esp32_video_ws: Optional[WebSocket] = None    # ESP32 비디오 소켓
web_clients: Set[WebSocket] = set()           # FE (/ws/web) 소켓들
viewers: Set[WebSocket] = set()               # 스트림 뷰어 (/ws/stream) 소켓들

latest_frame: Optional[bytes] = None

# start→started 3초 대기용
started_waiter: Optional[asyncio.Future] = None
# 바코드 스캔 윈도우 10초 타이머/상태
scan_deadline: float = 0.0
barcode_found: Optional[str] = None
scanning: bool = False

LOCK = asyncio.Lock()


# -------------------------
# 유틸
# -------------------------
async def send_json(ws: WebSocket, payload: dict):
    await ws.send_text(json.dumps(payload, ensure_ascii=False))

async def broadcast_json_to_web(payload: dict):
    dead = []
    msg = json.dumps(payload, ensure_ascii=False)
    for w in list(web_clients):
        try:
            await w.send_text(msg)
        except Exception:
            dead.append(w)
    for w in dead:
        web_clients.discard(w)

async def broadcast_frame(frame: bytes):
    dead = []
    for v in list(viewers):
        try:
            await v.send_bytes(frame)
        except Exception:
            dead.append(v)
    for v in dead:
        viewers.discard(v)

def decode_barcode_from_jpeg(jpeg: bytes) -> Optional[str]:
    """JPEG → (cv2|PIL) → pyzbar → 문자열"""
    try:
        if _HAS_CV2:
            import numpy as np
            buf = np.frombuffer(jpeg, dtype=np.uint8)
            img = cv2.imdecode(buf, cv2.IMREAD_GRAYSCALE)
            if img is None:
                return None
            results = zbar_decode(img)
        else:
            img = Image.open(BytesIO(jpeg)).convert("L")
            results = zbar_decode(img)

        if not results:
            return None
        data = results[0].data
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return str(data)
    except Exception:
        return None

async def lookup_item(barcode: str, db: Session = Depends(get_db)) -> Optional[dict]:
    """길이 13이면 ISBN, 아니면 item_id로 조회"""
    try:
        if len(barcode) == 13:
            # ISBN → ItemCopy → Item
            item_copy = db.query(ItemCopy).filter(ItemCopy.identifier_code == barcode).first()
            if item_copy:
                    return {
                        "identifier_code": item_copy.identifier_code,
                    }
        else:
            item_copy = db.query(ItemCopy).filter(ItemCopy.identifier_code == barcode).first()
            if item_copy:
                    return {
                        "identifier_code": item_copy.identifier_code,
                    }

    except Exception as e:
        print("lookup_item 에러:", e)

    return None

async def stop_streaming_and_notify():
    """ESP32에 stop 보내고, 시청자에게 상태 뿌림"""
    global esp32_ctrl_ws
    if esp32_ctrl_ws:
        try:
            await esp32_ctrl_ws.send_text("stop")
        except Exception:
            pass
    await broadcast_json_to_web({"type": "status", "from": "server", "value": "stop_sent"})

def reset_scan_state():
    global barcode_found, scan_deadline, scanning
    barcode_found = None
    scan_deadline = 0.0
    scanning = False

# -------------------------
# 0️⃣ FE ↔ BE: /ws/web
# -------------------------
@router.websocket("/ws/web")
async def ws_web(websocket: WebSocket):
    """FE 제어 채널: {type:'start'|'stop'} 전송, 결과/상태/인식 결과 수신"""
    global started_waiter, scan_deadline
    await websocket.accept()
    web_clients.add(websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                req = json.loads(raw)
            except Exception:
                # 잘못된 포맷 무시
                continue

            typ = req.get("type")
            if typ == "start":
                # 1) ESP32 연결 체크
                if esp32_ctrl_ws is None:
                    await send_json(websocket, {
                        "status": "error", "code": 503, "message": "ESP32 not connected"
                    })
                    continue

                # 2) started 대기자 준비 (3초 타임아웃)
                async with LOCK:
                    if started_waiter is None or started_waiter.done():
                        started_waiter = asyncio.get_event_loop().create_future()
                # 3) ESP32에 start 전송 (텍스트)
                try:
                    await esp32_ctrl_ws.send_text("start")
                except Exception:
                    await send_json(websocket, {
                        "status": "error", "code": 503, "message": "ESP32 not connected"
                    })
                    continue

                # 4) 3초 내 "started" 수신 대기
                try:
                    await asyncio.wait_for(started_waiter, timeout=3.0)
                except asyncio.TimeoutError:
                    await send_json(websocket, {
                        "status": "error", "code": 504, "message": "ESP32 no response (timeout)"
                    })
                    # 안전하게 stop 시도
                    await stop_streaming_and_notify()
                    continue

                # 5) 성공 응답
                await send_json(websocket, {"status": "started"})
                # 6) 스캔 윈도우(10초) 오픈
                reset_scan_state()
                scan_deadline = time.time() + 10.0
                await broadcast_json_to_web({"type": "status", "from": "server", "value": "scan_window_open"})

            elif typ == "stop":
                await stop_streaming_and_notify()
                reset_scan_state()
                await send_json(websocket, {"status": "stopped"})

            elif typ == "reset":
                reset_scan_state()
                await send_json(websocket, {"status": "ok", "message": "scan_state_reset"})

    except WebSocketDisconnect:
        pass
    finally:
        web_clients.discard(websocket)

# -------------------------
# 1️⃣ BE ↔ ESP32: /ws/esp32  (텍스트만: "ready"|"started"|"stopped")
# -------------------------
@router.websocket("/ws/esp32")
async def ws_esp32_ctrl(websocket: WebSocket, client_id: str = "esp32_001"):
    """ESP32 컨트롤 채널 (텍스트 'start'/'stop'만 사용)"""
    global esp32_ctrl_ws, started_waiter
    await websocket.accept()
    esp32_ctrl_ws = websocket
    await broadcast_json_to_web({"type": "status", "from": "esp32", "value": "connected"})

    try:
        while True:
            msg = await websocket.receive_text()
            # ESP32가 "started"/"stopped"/"ready" 등을 보내는 경우
            val = msg.strip().lower()
            await broadcast_json_to_web({"type": "status", "from": "esp32", "value": val})

            # "started"면 waiter 풀어주기
            if val == "started":
                async with LOCK:
                    if started_waiter and not started_waiter.done():
                        started_waiter.set_result(True)

    except WebSocketDisconnect:
        await broadcast_json_to_web({"type": "status", "from": "esp32", "value": "disconnected"})
    finally:
        esp32_ctrl_ws = None

# -------------------------
# 2️⃣ ESP32 → BE: /ws/esp32/video (바이너리 프레임)
# -------------------------
@router.websocket("/ws/esp32/video")
async def ws_esp32_video(websocket: WebSocket, client_id: str = "esp32_001"):
    """ESP32 비디오 채널(바이너리 JPEG), 약 33fps"""
    global latest_frame, barcode_found, scan_deadline, scanning
    await websocket.accept()
    esp32_video_ws = websocket
    await broadcast_json_to_web({"type": "status", "from": "esp32", "value": "video_connected"})

    try:
        while True:
            msg = await websocket.receive()
            if "bytes" in msg and msg["bytes"]:
                latest_frame = msg["bytes"]
                # 1) 프레임 브로드캐스트(원하면 안 써도 됨 — /ws/stream 구독자용)
                await broadcast_frame(latest_frame)

                # 2) 스캔 윈도우 열려 있으면 바코드 인식
                if scan_deadline > 0 and time.time() <= scan_deadline and not barcode_found:
                    if not scanning:
                        scanning = True
                        async def _scan_once(data: bytes):
                            global barcode_found, scanning
                            try:
                                code = await asyncio.to_thread(decode_barcode_from_jpeg, data)
                                if code:
                                    barcode_found = code
                                    # 결과 조회
                                    item = await lookup_item(code)
                                    if item:
                                        # 성공 + 물품 존재 (200)
                                        await broadcast_json_to_web({
                                            "status": "recognized", "code": 200, **item
                                        })
                                    else:
                                        # 성공 but 물품 없음 (404)
                                        await broadcast_json_to_web({"status": "not_found", "code": 404})
                                    # 어떤 경우든 stop 자동 전송
                                    await stop_streaming_and_notify()
                                    # 스캔 윈도우 종료
                                    reset_scan_state()
                            finally:
                                scanning = False
                        asyncio.create_task(_scan_once(latest_frame))
                # 3) 타임아웃 처리
                elif scan_deadline > 0 and time.time() > scan_deadline and not barcode_found:
                    # 408 timeout
                    await broadcast_json_to_web({"status": "timeout", "code": 408})
                    await stop_streaming_and_notify()
                    reset_scan_state()

            # 텍스트는 상태용(선택)
            elif "text" in msg and msg["text"]:
                await broadcast_json_to_web({"type": "status", "from": "esp32", "value": msg["text"]})

    except WebSocketDisconnect:
        await broadcast_json_to_web({"type": "status", "from": "esp32", "value": "video_disconnected"})

# -------------------------
# 추가) 시청자: /ws/stream  (프레임만 받고 싶은 FE가 구독)
# -------------------------
@router.websocket("/ws/stream")
async def ws_stream_view(websocket: WebSocket):
    await websocket.accept()
    viewers.add(websocket)
    try:
        while True:
            await asyncio.sleep(60)
    except WebSocketDisconnect:
        viewers.discard(websocket)

