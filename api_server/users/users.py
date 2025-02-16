from typing import Union
from fastapi import FastAPI, Response, APIRouter
from config import supabase

app    = FastAPI()
router = APIRouter(prefix="/users")


@router.get('/')
async def get_users():
    return