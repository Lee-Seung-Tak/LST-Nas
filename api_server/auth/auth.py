from typing import Optional
from fastapi import FastAPI, Response, APIRouter, status, Form, Depends
from config import supabase
from config import oauth2_scheme

app    = FastAPI()
router = APIRouter(prefix='/auth')

async def check_user_role( token: str, option: Optional[bool] = None ):
    
    response        = supabase.auth.get_user( token )
    user_id         = response.user.id
    check_user_role = supabase.table('roles').select('*').eq('id',user_id).eq('role','admin').execute()
    
    if check_user_role.data != []:
        
        if option is not None :
            return True, user_id
        else :
            return True
        
    else:
        
        if option is not None :
            return False, None
        else :
            return False
            

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
async def token_refresh( access_token:str = Form(...), refresh_token:str = Form(...), token: str= Depends( oauth2_scheme )  ):
    
    if token is None:
        return Response('access_token required.', status_code=status.HTTP_401_UNAUTHORIZED)
    
    try :
        usser_status = await check_user_role( token )
        if usser_status == False :
            return Response('Invalid Token', status_code=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response('Invalid Token', status_code=status.HTTP_401_UNAUTHORIZED)
    
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
async def logout( access_token:str = Form(...), refresh_token:str = Form(...) , token: str= Depends( oauth2_scheme ) ):
    
    if token is None:
        return Response('access_token required.', status_code=status.HTTP_401_UNAUTHORIZED)
    
    try :
        usser_status = await check_user_role( token )
        if usser_status == False :
            return Response('Invalid Token', status_code=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response('Invalid Token', status_code=status.HTTP_401_UNAUTHORIZED)
    
    if access_token is None or refresh_token is None :
        return Response('Token required.', status_code=status.HTTP_400_BAD_REQUEST)
    
    try :
        supabase.auth.set_session(access_token, refresh_token)
        supabase.auth.sign_out()
        
        return Response("Logout Success.", status_code=status.HTTP_200_OK)
    
    except Exception as e:
        print(e)
        return Response('Check token information.', status_code=status.HTTP_401_UNAUTHORIZED)