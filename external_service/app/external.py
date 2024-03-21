from fastapi import FastAPI, HTTPException
import httpx
import os

from external_schemas import SUserAdd, SUser, DefectStatus, SDefectAdd, SDefect

app = FastAPI()

USER_SERVICE_URL = str(os.environ.get('USER_SERVICE_URL')) + "/users/"
DEFECT_SERVICE_URL = str(os.environ.get('DEFECT_SERVICE_URL')) + "/defects/"

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
