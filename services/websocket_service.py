class WebSocketManager:
    # 현재 연결된 모든 웹소켓 클라이언트를 리스트로 저장
    def __init__(self):
        self.active_connections: list = []

    # 새 클라이언트 연결 시 accept()하고 리스트에 추가
    async def connect(self, websocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    # 연결이 끊긴 클라이언트는 리스트에서 제거
    def disconnect(self, websocket):
        self.active_connections.remove(websocket)

    # 연결된 모든 클라이언트에게 메시지(문자열) 전송
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
