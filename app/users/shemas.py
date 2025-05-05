from pydantic import BaseModel, Field, EmailStr


class UserRegister(BaseModel):
    first_name: str = Field(description="имя")
    last_name: str = Field(description="фамилия")
    email: EmailStr = Field(description="почта")
    hashed_password: str = Field(description="пароль")
    phone_number: str = Field(description="номер телефона")


class UserLogin(BaseModel):
    email: EmailStr
    password: str
