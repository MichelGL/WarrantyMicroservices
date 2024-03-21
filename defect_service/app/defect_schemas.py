from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict

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