from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import router as auth_router
from routers.item import router as item_router
#from routers.item_copy import router as item_copy_router
#from routers.rental import router as rental_router
from routers.user import router as user_router
from internal.auth import router as admin_auth_router
from internal.admin_user import router as admin_user_router
from internal.admin_item import router as admin_item_router
from internal.admin_rental import router as admin_rental_router
from kiosk.router import router as kiosk_router
from internal import admin
from database import engine, Base


Base.metadata.create_all(bind=engine)

app = FastAPI(
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 또는 ["*"] (개발 환경에서만)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(kiosk_router,prefix="/api/v1")
app.include_router(admin_auth_router,prefix="/api/v1")
app.include_router(admin_item_router,prefix="/api/v1/admin")
app.include_router(admin_user_router,prefix="/api/v1/admin")
app.include_router(admin_rental_router,prefix="/api/v1/admin")
app.include_router(auth_router,prefix="/api/v1")
app.include_router(item_router,prefix="/api/v1")
app.include_router(user_router,prefix="/api/v1")
#app.include_router(rental_router,prefix="/api/v1")
#app.include_router(item_copy_router,prefix="/api/v1")
