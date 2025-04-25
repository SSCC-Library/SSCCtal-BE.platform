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

# 인증 라우터를 FastAPI 애플리케이션에 등록
app.include_router(auth_router)
