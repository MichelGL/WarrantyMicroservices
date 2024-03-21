from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound

from defect_database import new_session, DefectOrm
from defect_schemas import DefectStatus, SDefectAdd, SDefect

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