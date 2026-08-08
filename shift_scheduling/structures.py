from pydantic import BaseModel
from typing import Literal
from sqlmodel import SQLModel
from datetime import date
from models import *
from pydantic import EmailStr, model_validator


class StaffCreateRequest(BaseModel):
    first_name: str
    last_name: str
    position: str
    contract_hours: int
    min_hours: int
    email: EmailStr
    shift_exclusions: list[Literal["morning", "afternoon", "evening"]]
    day_exclusions: list[
        Literal[
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
        ]
    ]

    @model_validator(mode="after")
    def validate_hours(self):
        if not (8 <= self.min_hours <= self.contract_hours):
            raise ValueError(f"min_hours must be between 8 and {self.contract_hours}.")

        return self


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
    email: EmailStr
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
