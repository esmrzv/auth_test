
from sqlalchemy.exc import SQLAlchemyError

from app.DAO.baseDAO import BaseDAO
from app.users.models import User


class UserDAO(BaseDAO[User]):
    model = User

    @classmethod
    async def get_user_by_id(cls, session, user_id: int):
        try:
            return await session.get(cls.model, user_id)
        except SQLAlchemyError as e:
            print(f'Error {e}')
            raise