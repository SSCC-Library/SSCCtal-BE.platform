"""
FastAPI 엔드포인트 정의
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import user as models
from schemas import user as schemas
from routers.websocket_handler import router as websocket_router

# 앱 실행 시 테이블 자동 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 허용할 origin 리스트
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#WebSocket 핸들러(router)를 FastAPI 애플리케이션에 등록
app.include_router(websocket_router)    #/ws/video_feed (ESP32용) 및 /ws/video (브라우저용) 경로에서 웹소켓 통신 처리

# DB 세션 의존성 함수 (요청마다 DB 세션 생성 -> 자동 닫힘)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 학번을 통해 사용자 정보를 조회하는 API
@app.post("/user/by-school-number", response_model=schemas.UserResponse)
def get_user_by_schoolnumber(request: schemas.SchoolNumberRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.school_number == request.school_number).first()    # DB에서 학번 기준으로 사용자 조회
    if not user:
        raise HTTPException(status_code=404, detail="User not found")    # 사용자 없을 경우 404 에러 반환
    return user    # 조회된 사용자 정보 반환
