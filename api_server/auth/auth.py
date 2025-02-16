from typing import Union
from fastapi import FastAPI, Response, APIRouter, Form, status
from config import supabase

app    = FastAPI()
router = APIRouter(prefix='/auth')


@router.post('/login')
async def login( email:str = Form(...), pw:str = Form(...) ):

    try :
        response = supabase.auth.sign_in_with_password( 
                {"email": email, "password": pw}
            )
            
        tokens  = {
            'access-token'  : response.session.access_token,
            'refresh-token' : response.session.refresh_token
        }
        
        return tokens
    
    except:
        return Response('Check Account Information', status_code=status.HTTP_401_UNAUTHORIZED)


@router.post('/refresh')
async def token_refresh( access_token:str = Form(...), refresh_token:str = Form(...) ):
    if access_token is None or refresh_token is None :
        return Response('Token required.', status_code=status.HTTP_400_BAD_REQUEST)
    
    try :
        response = supabase.auth.set_session(access_token, refresh_token)

        tokens  = {
            'access-token'  : response.session.access_token,
            'refresh-token' : response.session.refresh_token
        }
        
        return tokens
    
    except:
        return Response('Check Account Information', status_code=status.HTTP_401_UNAUTHORIZED)


@router.post('/logout')
async def logout( access_token:str = Form(...), refresh_token:str = Form(...) ):
    if access_token is None or refresh_token is None :
        return Response('Token required.', status_code=status.HTTP_400_BAD_REQUEST)
    
    try :
        supabase.auth.set_session(access_token, refresh_token)
        supabase.auth.sign_out()
        
        return Response("Logout Success.", status_code=status.HTTP_200_OK)
    
    except:
        return Response('Check token information.', status_code=status.HTTP_401_UNAUTHORIZED)