from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict

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