import os.path

from pydantic_settings import BaseSettings, SettingsConfigDict

class SmtpSettings(BaseSettings):
    """настройки для отправки писем"""
    smtp_host: str
    smtp_port: int
    sender_email: str
    sender_password: str



class Settings(SmtpSettings, BaseSettings):
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    SECRET_KEY: str
    ALGORITHM: str

    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", '.env'))

    @property
    def get_auth_data(self):
        return {"algorithm": self.ALGORITHM,
                "SECRET_KEY": self.SECRET_KEY}

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()