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
router = APIRouter(prefix='/folder')

async def make_file_location( file ):
    current_dir   = os.path.dirname(os.path.abspath(__file__))
    storage_dir   = os.path.join(current_dir, 'temporary_storage')
    file_location = os.path.join(storage_dir, '.temp')
    return file_location
    
    
async def get_bucket_name( token: str ):
    response    = supabase.auth.get_user( token )
    bucket_name = response.user.email 
    return bucket_name

    
    
@router.post('/folders')
async def make_folder( folder: str = Form(...), token: str= Depends(oauth2_scheme) ) :
    try :
        bucket_name   = await get_bucket_name   ( token )
        file_location = await make_file_location( '.temp' )

        try :
            with open(file_location, 'rb') as f:
                supabase.storage.from_(bucket_name).upload(
                    file=f,
                    path=f'{folder}/.temp',
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
                                path=f'{num}.{folder}/.temp',
                                file_options={"cache-control": "3600", "upsert": "false"},
                            )
                        return Response('Make new Folder Success.',status_code=status.HTTP_200_OK)
                        break
                    except Exception as e:
                        if 'Duplicate' in str(e):
                            num+=1
            else :
                print("Error : ", e)
                return Response('Make new Folder Error.',status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response('Make new Folder Success.',status_code=status.HTTP_200_OK)
    
    except Exception as e:
        print(e)
        if 'invalid JWT' in str(e) :
            return Response('token is expired', status_code=status.HTTP_401_UNAUTHORIZED)
        return Response('There are no valid buckets.',status_code=status.HTTP_400_BAD_REQUEST)
    

@router.delete('/folders')
async def delete_folder( folder_name: str = Form(...), token: str=Depends(oauth2_scheme) ):
    
    try :
        bucket_name  = await get_bucket_name   ( token )
        
        try :
                files      = supabase.storage.from_(bucket_name).list(folder_name)
                file_paths = [f"{folder_name}/{file['name']}" for file in files]
                if file_paths:
                    supabase.storage.from_(bucket_name).remove(file_paths)

        except Exception as e:
            print(e)
            return Response('Delete Folder Error.',status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response('Delete Folder Success.',status_code=status.HTTP_200_OK)
    
    except Exception as e:
        print(e)
        if 'invalid JWT' in str(e) :
            return Response('token is expired', status_code=status.HTTP_401_UNAUTHORIZED)
        return Response('There are no valid buckets.',status_code=status.HTTP_400_BAD_REQUEST)
    
