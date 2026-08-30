from pydantic import BaseModel
from typing import Literal, TypedDict
from sqlmodel import SQLModel
from datetime import date
from models import *
from pydantic import EmailStr, model_validator, RootModel

SHIFTS = Literal["morning", "afternoon", "evening"]
DAY = Literal[
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
]


class StaffCreateRequest(BaseModel):
    first_name: str
    last_name: str
    position: str
    contract_hours: int
    min_hours: int = 8
    email: EmailStr
    shift_exclusions: list[SHIFTS]
    day_exclusions: list[DAY]

    @model_validator(mode="after")
    def validate_hours(self):
        if not (8 <= self.min_hours <= self.contract_hours):
            raise ValueError(f"min_hours must be between 8 and {self.contract_hours}.")

        return self


class StaffUpdateRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    position: str | None = None
    contract_hours: int | None = None
    min_hours: int | None = None
    day_exclusions: list[DAY] | None = None
    shift_exclusions: list[SHIFTS] | None = None

    @model_validator(mode="after")
    def validate_hours(self):
        if not (8 <= self.min_hours <= self.contract_hours):
            raise ValueError(f"min_hours must be between 8 and {self.contract_hours}.")

        return self


class DepartmentCreateRequest(BaseModel):
    name: str
    min_staff: int = 1
    max_staff: int = 1
    # include: bool = True


# class DepartmentUpdateRequest(BaseModel):
#     id: int
#     name: str | None = None
#     min_staff: int | None = None
#     max_staff: int | None = None


class DepartmentResponse(BaseModel):
    id: int
    name: str
    min_staff: int = 1
    max_staff: int = 1


class ExclusionRead(SQLModel):
    id: int
    type: ExclusionType
    value: str


class StaffResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    position: str
    contract_hours: int
    min_hours: int
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
    week_start: str
    week_end: str
    generated_at: str
    schedule: dict[str, dict[int, dict[str, list[dict]]]]


class StaffProp(TypedDict):
    staff_id: int
    staff_name: str


class ScheduleCellResponse(BaseModel):
    department_id: int
    day: DAY
    shift: SHIFTS
    staff: list[StaffProp]


class UpdateCellRequest(BaseModel):
    week_start: str
    department_id: int
    day: DAY
    shift: SHIFTS
    staff_ids: list[int]


class WeekRequest(BaseModel):
    week_start: str
