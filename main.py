from fastapi import FastAPI
from routers.auth import router as auth_router
from routers.item import router as item_router
from routers.item_copy import router as item_copy_router
from routers.rental import router as rental_router
from routers.user import router as user_router
from internal import admin
from database import engine, Base


Base.metadata.create_all(bind=engine)

app = FastAPI()



app.include_router(auth_router)
app.include_router(item_router)
app.include_router(user_router)
app.include_router(rental_router)
app.include_router(item_copy_router)
app.include_router(admin.router, prefix="/admin")