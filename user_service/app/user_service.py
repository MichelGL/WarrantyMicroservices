from fastapi import FastAPI, HTTPException
from sqlalchemy import select
from starlette import status

from contextlib import asynccontextmanager

from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from enum import Enum

from pydantic import BaseModel, ConfigDict

engine = create_async_engine("sqlite+aiosqlite:///user.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)

class Model(DeclarativeBase):
    pass

class UserOrm(Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    password = Column(String)
    role = Column(String)

async def create_tables():
    # https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#synopsis-core
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)

class Role(str, Enum):
    employee = "Сотрудник КС"
    contractor = "Подрядчик"

class SUserAdd(BaseModel):
    username: str
    password: str
    role: Role

class SUser(SUserAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    await delete_tables()
    print("База очищена")
    await create_tables()
    print("База готова к работе")
    yield
    print("Выключение")

app = FastAPI(lifespan=lifespan)

@app.post("/users", status_code=status.HTTP_201_CREATED)
async def add_user(
        user: SUserAdd
) -> None:
    # Проверяем, существует ли пользователь с таким логином
    async with new_session() as session:
        existing_user = await session.execute(select(UserOrm).where(UserOrm.username == user.username))
        if existing_user.scalar():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Пользователь с таким логином уже существует")

    # Если пользователь с таким логином не существует, добавляем нового пользователя
    user_id = await UserRepository.add_one(user)
    return {"user_id": user_id, "message": "Пользователь успешно добавлен"}

@app.get("/users")
async def get_users() -> list[SUser]:
    users = await UserRepository.find_all()
    return users