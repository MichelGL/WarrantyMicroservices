from fastapi import FastAPI, HTTPException
from starlette import status

from contextlib import asynccontextmanager
from defect_database import create_tables, delete_tables

from defect_repoitory import DefectRepository
from defect_schemas import DefectStatus, SDefectAdd, SDefect

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