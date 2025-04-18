"""
esp32 cam 실시간 스트리밍 라우터
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

# FastAPI용 라우터 객체 생성
router = APIRouter()

# 실시간 스트리밍을 받을 웹소켓 클라이언트 목록 (웹 브라우저 사용자)
clients_list = []

#ESP32-CAM으로부터 실시간 영상 데이터를 수신하는 WebSocket 엔드포인트
@router.websocket("/ws/video_feed")
async def video_feed(websocket: WebSocket):
    await websocket.accept()
    print("📡 ESP32 Connected")
    try:
        while True:
            # ESP32로부터 바이트 형태의 영상 프레임 수신
            data = await websocket.receive_bytes()

            # 수신한 데이터를 모든 클라이언트(웹 브라우저)에 브로드캐스트
            for client in clients_list:
                try:
                    await client.send_bytes(data)
                except Exception:
                    # 전송 중 오류 발생 시 무시하고 다음 클라이언트로
                    pass
    except WebSocketDisconnect:
        print("❌ ESP32 Disconnected")

#웹 브라우저 사용자(뷰어)와 연결되는 WebSocket 엔드포인트
@router.websocket("/ws/video")
async def video_viewer(websocket: WebSocket):
    # 연결 수락
    await websocket.accept()
    print("👀 Viewer Connected")

    # 현재 클라이언트를 클라이언트 목록에 추가
    clients_list.append(websocket)
    try:
        while True:
            # ping 유지용 메시지 수신 (실제 데이터 없음)
            await websocket.receive_text()  # ping 유지용
    except WebSocketDisconnect:
        print("👋 Viewer Disconnected")
        # 연결이 끊긴 클라이언트를 목록에서 제거
        clients_list.remove(websocket)
