from fastapi import HTTPException, Depends

from fastapi import Request
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.database import get_db
from app.config import settings
from app.users.dao import UserDAO


def get_token(request: Request):
    """функция получения токена"""
    token = request.cookies.get('access_token')
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing")
    return token



async def get_current_user(token: str = Depends(get_token), session: AsyncSession  = Depends(get_db)):
    try:
        auth_data = settings.get_auth_data
        payload = jwt.decode(token, auth_data['SECRET_KEY'], algorithms=[auth_data['algorithm']])
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired"
        )
    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID is missing"
        )
    user_data = await UserDAO.get_one_or_none_by_id(session, int(user_id))
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID is invalid or expired"
        )
    return user_data



