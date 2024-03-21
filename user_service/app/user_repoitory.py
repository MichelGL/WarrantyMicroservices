from sqlalchemy import select

from user_database import new_session, UserOrm
from user_schemas import SUserAdd, SUser

class UserRepository:
    @classmethod
    async def add_one(cls, data: SUserAdd) -> int:
        async with new_session() as session:
            user_dict = data.model_dump()

            user = UserOrm(**user_dict)
            session.add(user)
            await session.flush()
            await session.commit()
            return user.id

    @classmethod
    async def find_all(cls) -> list[SUser]:
        async with new_session() as session:
            query = select(UserOrm)
            result = await session.execute(query)
            user_models = result.scalars().all()
            user_schemas = [SUser.model_validate(user_model) for user_model in user_models]
            return user_schemas