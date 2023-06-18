from fastapi import APIRouter, Depends

from utils.auth import get_current_user

API_VERSION_MAJOR = 0
API_VERSION_MINOR = 1
API_VERSION_PATH = 0

API_VERSION = f'{API_VERSION_MAJOR}.{API_VERSION_MINOR}.{API_VERSION_PATH}'

router = APIRouter()


@router.get('/user/')
async def user(user_id: str = Depends(get_current_user)):
    return {'user_id': user_id}
