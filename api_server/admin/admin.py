from typing import Optional
from fastapi import FastAPI, Response, APIRouter, status, Form, Depends
from config import supabase
from config import oauth2_scheme
from config import UserUpdate
from config import limit_file_size
import json

app    = FastAPI()
router = APIRouter(prefix='/admin')

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

async def create_bucket( email ):
    
    try :
        supabase.storage.create_bucket(
            email,
            options={
                    "public": False,
                    "file_size_limit": limit_file_size,
                }
            )
    except Exception as e:
        print("Error : ", e)

@router.post('/users')
async def get_users( token: str= Depends(oauth2_scheme), email: str = Form(...), pw: str = Form(...)):
    
    if token is None:
        return Response('access_token required.', status_code=status.HTTP_401_UNAUTHORIZED)
    
    if email is None or pw is None:
        return Response('Check your eamil and pw', status_code=status.HTTP_400_BAD_REQUEST)
        
    elif token is not None:
        
        try:
            user_is_admin = await check_user_role( token )

            if user_is_admin is True:
            
                try :
                    response = supabase.auth.sign_up( { 'email': email, 'password': pw } )
                    user_id  = response.user.id
                    
                    supabase.table('roles').insert( 
                        { 
                            'id'       : user_id, 
                            'role'     : 'user',
                            'email'    : email,
                            'pw'       : pw
                            
                        } 
                    ).execute()
                
                    await create_bucket( email )
                except Exception as e:
                    return Response(str(e), status_code=status.HTTP_400_BAD_REQUEST)
                
               
                
                return Response('Sign up Success.', status_code=status.HTTP_201_CREATED)
                                    
            else :
                return Response('User does not have permission.', status_code=status.HTTP_401_UNAUTHORIZED)
            
        except Exception as e:
            print(f"[LOG] - admin.py get_users function line 20 ~ 34 : {e}")   
            return Response('access_token required.', status_code=status.HTTP_401_UNAUTHORIZED)
        

    
@router.patch('/users/{user_id}')
async def update_user( user_id: str, user_update: UserUpdate, token: str= Depends( oauth2_scheme ) ):
    
    if token is None:
        return Response('access_token required.', status_code=status.HTTP_401_UNAUTHORIZED)
    
    user_update = user_update.model_dump()
    
    if user_update is None:
        return Response('Check user update data and pw', status_code=status.HTTP_400_BAD_REQUEST)
     
    try:
        user_is_admin = await check_user_role( token )
        
        if user_is_admin is True:
            try:
                user_data = supabase.table('roles').select('*').eq('id',user_id).execute().data[0]
 
                response = supabase.auth.sign_in_with_password( 
                    {"email": user_data['email'], "password": user_data['pw']}
                )
                
                supabase.auth.set_session( response.session.access_token, response.session.refresh_token )
                supabase.auth.update_user( user_update )
                
                if 'password' in user_update :
                    supabase.table('roles').update( {'pw' : user_update['password']} ).eq('id',user_id).execute()
                
                return Response('User update Success.', status_code=status.HTTP_200_OK)
        
            except Exception as e:
                return Response(str(e), status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response('User does not have permission.', status_code=status.HTTP_401_UNAUTHORIZED)


@router.get('/users')
async def get_users_list( token: str= Depends( oauth2_scheme ) ):
    
    if token is None:
        return Response('access_token required.', status_code=status.HTTP_401_UNAUTHORIZED)
    
    user_is_admin = await check_user_role( token )
        
    if user_is_admin is True:
        
        response = supabase.table('roles').select('*').execute()
        return response.data
    
    else :
        return Response('User does not have permission.', status_code=status.HTTP_401_UNAUTHORIZED)


@router.get('/users/{user_id}')
async def get_specific_user( user_id: str, token: str= Depends( oauth2_scheme ) ):
    if token is None:
        return Response('access_token required.', status_code=status.HTTP_401_UNAUTHORIZED)
    
    user_is_admin = await check_user_role( token )
    
    try :
        if user_is_admin is True:
            print("user_id : ", user_id)
            response = supabase.table('roles').select('*').eq('id',user_id).execute()
            return response.data
        
        else :
            return Response('User does not have permission.', status_code=status.HTTP_401_UNAUTHORIZED)
        
    except Exception as e:
        print(e)
        return Response('User ID is not valid', status_code=status.HTTP_400_BAD_REQUEST)
