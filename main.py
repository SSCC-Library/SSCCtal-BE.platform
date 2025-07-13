from fastapi import FastAPI
from routers.auth import router as auth_router
from routers.item import router as item_router
from routers.item_copy import router as item_copy_router
from routers.rental import router as rental_router
from routers.user import router as user_router
from internal.admin_auth import router as admin_auth_router
from internal.admin_user import router as admin_user_router
from internal.admin_item import router as admin_item_router
from internal import admin
from database import engine, Base


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(admin_item_router,prefix="/api/v1/admin")
app.include_router(admin_user_router,prefix="/api/v1/admin")
app.include_router(auth_router,prefix="/api/v1")
app.include_router(item_router,prefix="/api/v1")
app.include_router(user_router,prefix="/api/v1")
app.include_router(rental_router,prefix="/api/v1")
app.include_router(item_copy_router,prefix="/api/v1")
app.include_router(admin_auth_router,prefix="/api/v1/admin")