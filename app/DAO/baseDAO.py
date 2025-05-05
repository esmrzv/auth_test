from typing import Generic, TypeVar, List

from pydantic.v1 import BaseModel
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError


from app.database import Base

T = TypeVar('T', bound=Base)


class BaseDAO(Generic[T]):
    model = type[T]

    @classmethod
    async def get_all(cls, session, **filters):
        query = select(cls.model).filter_by(**filters)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_one_ore_none(cls, session, **filters):
        query = select(cls.model).filter_by(**filters)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_one_or_none_by_id(cls, session, data_id: int):
        query = select(cls.model).filter_by(id=data_id)
        result = await session.execute(query)
        return result.scalars().one_or_none()

    @classmethod
    async def create_item(cls, session, **data):
        new_item = cls.model(**data)
        session.add(new_item)
        try:
            await session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        return new_item


    @classmethod
    async def add_many(cls, session, instances: List[BaseModel]):
        instance_dict = [item.dict(exclude_unset=True) for item in instances]
        new_instance = [cls.model(**item) for item in instance_dict]
        session.add_all(new_instance)
        try:
            await session.flush()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        return new_instance

    @classmethod
    async def update_item(cls, session, data_id: int, **kwargs):
        query = (
            update(cls.model)
            .where(cls.model.id == data_id)
            .values(**kwargs)
        )
        await session.execute(query)
        await session.commit()

    @classmethod
    async def confirm_user_email(cls, session, user_id: int):
        """
        Подтверждает email пользователя.
        :param session: Асинхронная сессия SQLAlchemy.
        :param user_id: ID пользователя для подтверждения email.
        """
        query = (
            update(cls.model)
            .where(cls.model.id == user_id)
            .values(is_email_confirmed=True)
        )
        await session.execute(query)
        await session.commit()





