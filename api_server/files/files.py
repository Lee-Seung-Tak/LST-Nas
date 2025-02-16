from typing import Union, Optional
from fastapi import FastAPI, Response, APIRouter, status, Form, Depends, File, UploadFile
from config import supabase
from config import oauth2_scheme
from config import limit_file_size
import shutil
import os
import time
import json
app    = FastAPI()
router = APIRouter(prefix='/files')

async def make_file_location( file ):
    current_dir   = os.path.dirname(os.path.abspath(__file__))
    storage_dir   = os.path.join(current_dir, 'temporary_storage')
    file_location = os.path.join(storage_dir, file.filename)
    return file_location

    
    
async def get_bucket_name( token: str ):
    response    = supabase.auth.get_user( token )
    bucket_name = response.user.email 
    return bucket_name


async def file_save( file, file_location ):
    file.file.seek(0, 2)  # 파일 끝으로 이동
    file_size = file.file.tell()  # 현재 위치(파일 크기)
    file.file.seek(0)  # 다시 처음으로 이동 (중요!)
    
    if file_size > limit_file_size : 
        return False 

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return True


@router.get('/list')
async def get_all_file_list( token: str= Depends(oauth2_scheme) ):
    try:
        bucket_name  = await get_bucket_name( token )
      
        folder_list = supabase.storage.from_(bucket_name).list()
        
        file_list = []
        for folder in folder_list:

            response = supabase.storage.from_(bucket_name).list(
                folder['name'],
                {"offset": 0, "sortBy": {"column": "name", "order": "asc"}},
            )
            
          
            for data in response :
                print(data)
                if data['name'] != '.temp':
                    del data['metadata']
                    file_list.append(data)
                
        return file_list
    
    except Exception as e:
        if 'invalid JWT' in str(e) :
            return Response('invalid JWT', status_code=status.HTTP_401_UNAUTHORIZED)
        else :
            return Response('Bad request.', status_code=status.HTTP_400_BAD_REQUEST)

@router.get('/search')
async def search_file( query: str, token: str= Depends( oauth2_scheme )):
    try:
        bucket_name  = await get_bucket_name( token )
      
        folder_list = supabase.storage.from_(bucket_name).list()
        
        file_list = []
        for folder in folder_list:

            response = supabase.storage.from_(bucket_name).list(
                folder['name'],
                {"offset": 0, "search":query, "sortBy": {"column": "name", "order": "asc"}},
            )

          
            for data in response :
                del data['metadata']
                file_list.append(data)
                
        return file_list
    except Exception as e:
        if 'invalid JWT' in str(e) :
            return Response('invalid JWT', status_code=status.HTTP_401_UNAUTHORIZED)
        else :
            return Response('Bad request.', status_code=status.HTTP_400_BAD_REQUEST)


@router.post('/upload')
async def upload( token: str= Depends( oauth2_scheme ), file: UploadFile = File(...) ):
    try :
        bucket_name  = await get_bucket_name   ( token )
        file_location = await make_file_location( file )
        file_status   = await file_save         ( file, file_location )
        
        if file_status == False :
            return Response('File size is over. Max size is 5120.', status_code=status.HTTP_400_BAD_REQUEST)
        
        try :
            with open(file_location, 'rb') as f:
                supabase.storage.from_(bucket_name).upload(
                    file=f,
                    path=f'upload/{file.filename}',
                    file_options={"cache-control": "3600", "upsert": "false"},
                )
        except Exception as e:
            
            # file 이름이 중복된 경우 문제없이 업로드 하기 위한 로직직
            if 'Duplicate' in str(e):
                num = 2
                while(True):
                    try :
                        with open(file_location, 'rb') as f:
                            supabase.storage.from_(bucket_name).upload(
                                file=f,
                                path=f'upload/({num}){file.filename}',
                                file_options={"cache-control": "3600", "upsert": "false"},
                            )
                        return Response('Upload Success.',status_code=status.HTTP_200_OK)
                  
                    except Exception as e:
                        if 'Duplicate' in str(e):
                            num+=1
            else :
                print("Error : ", e)
                os.remove( file_location )
                return Response('Upload Error.',status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        os.remove( file_location )
        return Response('Upload Success.',status_code=status.HTTP_200_OK)
    
    except Exception as e:
        if 'invalid JWT' in str(e):
            return Response('token is expired', status_code=status.HTTP_401)
        return Response('There are no valid buckets.',status_code=status.HTTP_400_BAD_REQUEST)
    

@router.get('/{file_id}')
async def download( file_id: str, folder: str, token: str= Depends(oauth2_scheme) ):
    try :
        bucket_name  = await get_bucket_name( token )
        try :
            response  = supabase.storage.from_(bucket_name).create_signed_url(
                                f'{folder}/{file_id}', 60
                            )
            file_link = response['signedURL']
 
            return file_link
        except Exception as e:
            return Response('Bad Request.', status_code=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response('invalid JWT', status_code=status.HTTP_401_UNAUTHORIZED)

    
@router.delete('/{file_id}')
async def delete( file_id: str, folder: str, token: str= Depends(oauth2_scheme) ):
    try:
        bucket_name  = await get_bucket_name( token )
        try:
            supabase.storage.from_(bucket_name).remove([f'{folder}/{file_id}'])
            return Response('Delete Success.', status_code=status.HTTP_200_OK)
        
        except Exception as e:
            return Response('Bad Request.', status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response('invalid JWT', status_code=status.HTTP_401_UNAUTHORIZED)
    

@router.patch('/{file_id}')
async def patch( file_id: str, folder: str, rename: str, token: str= Depends(oauth2_scheme) ):
    try:
        bucket_name  = await get_bucket_name( token )
        try:
            supabase.storage.from_(bucket_name).copy(
                f'{folder}/{file_id}', f'{folder}/{rename}'
                )
            supabase.storage.from_(bucket_name).remove([f'{folder}/{file_id}'])

            return Response('Rename Success.', status_code=status.HTTP_200_OK)
        
        except Exception as e:
            return Response('Bad Request.', status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response('invalid JWT', status_code=status.HTTP_401_UNAUTHORIZED)
    
    
@router.post('/{file_id}/copy')
async def patch( file_id: str, folder: str = Form(...), token: str= Depends(oauth2_scheme) ):
    try:
        bucket_name  = await get_bucket_name( token )
        try:
            supabase.storage.from_(bucket_name).copy(
                f'{folder}/{file_id}', f'{folder}/(2).{file_id}'
            )

            return Response('File Copy Success.', status_code=status.HTTP_200_OK)
        
        except Exception as e:
            print('Duplicate' in str(e))
            if 'Duplicate' in str(e):
                num = 2
                while(True):
                    try :
                        supabase.storage.from_(bucket_name).copy(
                            f'{folder}/{file_id}', f'{folder}/({num}).{file_id}'
                        )
                        return Response('Copy Success.',status_code=status.HTTP_200_OK)
                    
                    except Exception as e:
                        if 'Duplicate' in str(e):
                            num+=1
                            
            return Response('Bad Request.', status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response('invalid JWT', status_code=status.HTTP_401_UNAUTHORIZED)
    
    
