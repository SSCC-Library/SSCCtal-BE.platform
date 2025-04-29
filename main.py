"""
FastAPI 엔드포인트 정의
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine, get_db
from models import user as models
from schemas import user as schemas
from routers.websocket_handler import router as websocket_router
from routers.auth import router as auth_router
from routers.manual_input import router as manual_input_router
from routers.rental import router as rental_router
from routers.return_handler import router as return_router

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

# WebSocket 핸들러 등록 (/ws/video_feed, /ws/video)
app.include_router(websocket_router)

# 인증 라우터 등록
app.include_router(auth_router)

# 수동 입력(manual input) 라우터 등록
app.include_router(manual_input_router)

# 대여 요청(rental) 라우터 등록
app.include_router(rental_router)

# 반납 요청(return) 라우터 등록
app.include_router(return_router)