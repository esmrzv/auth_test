from datetime import datetime, timedelta

from starlette import status
from fastapi import HTTPException

from jose import jwt
from pydantic import EmailStr

from app.config import settings
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
from app.users.dao import UserDAO

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


def hash_password(password):
    """функция хеширования пароля"""
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    """фунция проверки простого пароля с хешированным"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    """функция создает access_token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    auth_data = settings.get_auth_data
    encoded_jwt = jwt.encode(to_encode, auth_data['SECRET_KEY'], algorithm=auth_data['algorithm'])
    return encoded_jwt


async def authenticate_user(email: EmailStr, password: str, session):
    """функция для проверки почтв и пароля"""
    user = await UserDAO.get_one_ore_none(email=email, session=session)
    if not user or verify_password(plain_password=password, hashed_password=user.hashed_password) is False:
        return None

    return user


def generate_reset_password_token(email: str):
    """функция генерации токена на сброс пароля"""
    return serializer.dumps(email, salt='reset-password')


def confirm_reset_password_token(token: str, expiration=3600):
    """функция подтверждения токена"""
    try:
        email = serializer.loads(token, salt='reset-password', max_age=expiration)
        return email
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Token expired'
        )

def generate_email_token(email: str, expiration=3600):
    """функция генерации токена для почты"""
    return serializer.dumps(email, salt='email-token')


def confirm_email_token(token: str, expiration=3600):
    """функция подтверждения токена"""
    try:
        email = serializer.loads(token, salt='email-token', max_age=expiration)
        return email
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Token expired'
        )