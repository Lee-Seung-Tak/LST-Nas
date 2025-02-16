from typing import Union
from fastapi import FastAPI  
from fastapi import APIRouter
from users.users import router as users_router
from auth.auth import router as auth_router
from admin.admin import router as admin_router
from files.files import router as files_router
from folder.folder import router as folder_router

app = FastAPI()  

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(files_router)
app.include_router(folder_router)