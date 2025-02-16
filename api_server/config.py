import os
from supabase import create_client, Client

from dotenv import load_dotenv
load_dotenv()

from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

api_key      :str     = os.environ.get('API_KEY')
database_url :str     = os.environ.get('DATABASE_URL')
supabase     :Client  = create_client(database_url, api_key)

from pydantic import BaseModel
class UserUpdate(BaseModel):
    phone: str | None = None  
    password: str | None = None  

limit_file_size=5120000