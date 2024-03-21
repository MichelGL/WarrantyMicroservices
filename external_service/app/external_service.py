from fastapi import FastAPI, HTTPException
import httpx
import os
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict
from starlette import status


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

app = FastAPI()

USER_SERVICE_URL = str(os.environ.get('USER_SERVICE_URL')) + "/users/"
DEFECT_SERVICE_URL = str(os.environ.get('DEFECT_SERVICE_URL')) + "/defects/"

class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"

@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")

@app.post("/defects/", status_code=201)
async def add_defect(
        defect: SDefectAdd
) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{DEFECT_SERVICE_URL}", json=defect.to_dict())

    if response.status_code == 422:
        raise HTTPException(status_code=422,
                            detail="Некорректный запрос (например, отсутствие обязательных параметров)")

    return response.json()

@app.get("/defects/{defect_id}", status_code=200)
async def get_defect(
        defect_id: int
) -> SDefect:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DEFECT_SERVICE_URL}{defect_id}")

    if response.status_code == 404:
        raise HTTPException(status_code=404,
                            detail="Дефект с указанным defect_id не найден")

    if response.status_code == 422:
        raise HTTPException(status_code=422,
                            detail="Некорректный запрос (например, отсутствие обязательных параметров)")

    return response.json()

@app.put("/defects/{defect_id}", status_code=200)
async def update_defect_status(
        defect_id: int,
        new_status: DefectStatus
) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{DEFECT_SERVICE_URL}{defect_id}?new_status={new_status}")

    if response.status_code == 404:
        raise HTTPException(status_code=404,
                            detail="Дефект с указанным defect_id не найден")

    if response.status_code == 422:
        raise HTTPException(status_code=422,
                            detail="Некорректный запрос (например, отсутствие обязательных параметров)")

    return response.json()

@app.post("/users", status_code=201)
async def add_user(
        user: SUserAdd
) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{USER_SERVICE_URL}", json=user.to_dict())

    if response.status_code == 409:
        raise HTTPException(status_code=409,
                            detail="Пользователь с таким логином уже существует")

    if response.status_code == 422:
        raise HTTPException(status_code=422,
                            detail="Некорректный запрос (например, отсутствие обязательных параметров)")

    return response.json()

@app.get("/users", status_code=201)
async def get_users() -> list[SUser]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE_URL}")

    return response.json()
