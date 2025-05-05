

from starlette import status

from app.users.auth import hash_password, authenticate_user, create_access_token, generate_reset_password_token, \
    confirm_reset_password_token, generate_email_token, confirm_email_token

from fastapi import APIRouter, Response, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.users.dao import UserDAO

from app.users.shemas import UserRegister, UserLogin
from app.users.utils import send_email
from fastapi import Form

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/register')
async def register(user_data: UserRegister, session: AsyncSession = Depends(get_db)):
    user = await UserDAO.get_one_ore_none(email=user_data.email, session=session)
    if user:
        return {'message': "Пользователь уже существует"}

    user_dict = user_data.model_dump()
    user_dict['hashed_password'] = hash_password(user_data.hashed_password)
    await UserDAO.create_item(**user_dict, session=session)
    return {
        'message': "Вы успешно зарегистрировались"
    }


@router.post('/login')
async def login(response: Response, user_data: UserLogin, session: AsyncSession = Depends(get_db)):
    user_data = await authenticate_user(email=user_data.email, password=user_data.password, session=session)
    if user_data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Incorrect email or password')
    access_token = create_access_token({'sub': str(user_data.id)})
    response.set_cookie(key='access_token', value=access_token, httponly=True)
    return {'access_token': access_token}


@router.post('/logout')
async def logout(response: Response):
    response.delete_cookie(key='access_token')
    return {'message': "Вы вышли из системы"}


# @router.get('/me', summary='Данные о мне')
# async def me(user: User = Depends(get_current_user)):
#     return user
#

@router.get('/{user_id}', summary='Получение пользователя по айди')
async def get_user_by_id(user_id: int, session: AsyncSession = Depends(get_db)):
    check = await UserDAO.get_user_by_id(user_id=user_id, session=session)
    if check is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='user not found')
    return check


@router.post('/forgot-password')
async def forgot_password(email: str, session: AsyncSession = Depends(get_db)):
    user = UserDAO.get_one_ore_none(email=email, session=session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Пользователь не найден')

    token = generate_reset_password_token(email)
    reset_url = f'http://127.0.0.1:8000/users/reset-password?token={token}'

    ## send email

    subject = 'Сбросить ваш пароль'
    body = f'Перейдите по ссылке чтоб сбросить свой пароль <a href="{reset_url}">Reset Password</a>'
    await send_email(to_email=email, subject=subject, body=body)
    return {'message': 'Password reset email sent'}


@router.post('/reset-password')
async def reset_password(token, new_password: str = Form(...), session: AsyncSession = Depends(get_db)):
    email = confirm_reset_password_token(token)
    user = await UserDAO.get_one_ore_none(email=email, session=session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='user not found')
    hashed_password = hash_password(new_password)
    await UserDAO.update_item(data_id=user.id, session=session, hashed_password=hashed_password)
    return {'message': 'Password reset successfully'}



@router.post('/send-confirm-email')
async def send_confirm_email(email: str, session: AsyncSession = Depends(get_db)):
    user = await UserDAO.get_one_ore_none(email=email, session=session)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='user not found')
    token = generate_email_token(email)
    confirmation_url = f'http://127.0.0.1:8000/users/confirm-email?token={token}'


    subject = 'Confirm your email'
    body = f'Перейдите по ссылке для подтверждения почтыЖ <a href="{confirmation_url}">Confirm Email</a>'
    await send_email(to_email=email, subject=subject, body=body)
    return {"message": "Confirmation email sent"}

@router.post('/confirm-email')
async def confirm_email(token: str, session: AsyncSession = Depends(get_db)):
    email = confirm_email_token(token)

    user = await UserDAO.get_one_ore_none(email=email, session=session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='user not found')
    await UserDAO.confirm_user_email(user_id=user.id, session=session)
    return {"message": "Email confirmed"}




