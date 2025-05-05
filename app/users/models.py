

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    id: Mapped[int] = mapped_column(unique=True, autoincrement=True, primary_key=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(unique=True, nullable=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True, server_default="True")
    is_email_confirmed : Mapped[bool] = mapped_column(default=False, nullable=True)
    extend_existing = True

