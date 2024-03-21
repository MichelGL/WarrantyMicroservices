from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine("sqlite+aiosqlite://defect.db")
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