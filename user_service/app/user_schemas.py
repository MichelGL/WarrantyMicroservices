from enum import Enum

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