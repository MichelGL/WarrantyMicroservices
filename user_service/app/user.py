from fastapi import FastAPI, HTTPException
from sqlalchemy import select
from starlette import status

from contextlib import asynccontextmanager

from user_database import new_session, UserOrm, create_tables, delete_tables
from user_repoitory import UserRepository
from user_schemas import Role, SUserAdd, SUser

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