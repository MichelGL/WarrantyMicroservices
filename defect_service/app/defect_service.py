from fastapi import FastAPI, HTTPException
from starlette import status
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from enum import Enum
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound

from pydantic import BaseModel, ConfigDict

from contextlib import asynccontextmanager

engine = create_async_engine("sqlite+aiosqlite:///defect.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)

class Model(DeclarativeBase):
    pass

class DefectOrm(Model):
    __tablename__ = "defects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    status = Column(String)
    repair_deadline = Column(Integer, nullable=True)
    contractor = Column(String, nullable=True)

async def create_tables():
    # https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#synopsis-core
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)

class DefectStatus(str, Enum):
    new = "Новый"
    in_progress = "В работе"
    completed = "Завершен"

class SDefectAdd(BaseModel):
    name: str
    status: DefectStatus
    repair_deadline: Optional[int] = None
    contractor: Optional[str] = None

class SDefect(SDefectAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)

class DefectRepository:
    @classmethod
    async def add_one(cls, data: SDefectAdd) -> int:
        async with new_session() as session:
            defect_dict = data.model_dump()

            defect = DefectOrm(**defect_dict)
            session.add(defect)
            await session.flush()
            await session.commit()
            return defect.id

    @classmethod
    async def find_by_id(cls, defect_id: int) -> SDefect:
        async with new_session() as session:
            try:
                query = select(DefectOrm).filter_by(id=defect_id)
                result = await session.execute(query)
                defect_model = result.scalar_one()
                return SDefect.from_orm(defect_model)
            except NoResultFound:
                return None

    @classmethod
    async def update_status(cls, defect_id: int, new_status: DefectStatus) -> None:
        async with new_session() as session:
            statement = (
                update(DefectOrm)
                .where(DefectOrm.id == defect_id)
                .values(status=new_status)
            )
            await session.execute(statement)
            await session.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await delete_tables()
    print("База очищена")
    await create_tables()
    print("База готова к работе")
    yield
    print("Выключение")

app = FastAPI(lifespan=lifespan)

@app.post("/defects", status_code=status.HTTP_201_CREATED)
async def add_defect(
        defect: SDefectAdd
) -> None:
        defect_id = await DefectRepository.add_one(defect)
        return {"defect_id": defect_id, "message": "Дефект успешно добавлен"}

@app.get("/defects/{defect_id}")
async def get_defect(
        defect_id: int
) -> SDefect:
    defect = await DefectRepository.find_by_id(defect_id)
    if defect is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Дефект с указанным defect_id не найден")
    return defect


@app.put("/defects/{defect_id}")
async def update_defect_status(
        defect_id: int,
        new_status: DefectStatus
) -> None:
    defect = await DefectRepository.find_by_id(defect_id)
    if defect is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Дефект с указанным defect_id не найден")

    old_status = defect.status
    await DefectRepository.update_status(defect_id, new_status)
    return {"defect_id": defect_id, "message": f"Статус дефекта успешно изменён с '{old_status}' на '{new_status}'"}