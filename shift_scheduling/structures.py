from pydantic import BaseModel
from typing import Literal
from sqlmodel import SQLModel
from datetime import date
from models import *


class StaffCreateRequest(BaseModel):
    first_name: str
    last_name: str
    position: str
    contract_hours: int
    shift_exclusions: list[Literal["morning", "afternoon", "evening"]]
    day_exclusions: list[
        Literal[
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
        ]
    ]


class DepartmentCreateRequest(BaseModel):
    name: str
    min_staff: int = 1
    max_staff: int = 1


class ExclusionRead(SQLModel):
    id: int
    type: ExclusionType
    value: str


class StaffRead(SQLModel):
    id: int
    first_name: str
    last_name: str
    position: str
    contract_hours: int
    exclusions: list[ExclusionRead] = []


class ScheduleItem(BaseModel):
    id: int
    department: str
    staff: str
    week_day: str
    week_date: date
    time: str


class ScheduleResponse(BaseModel):
    success: bool
    schedule: dict[str, dict[str, object]]
    