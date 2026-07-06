from sqlmodel import Field, Relationship, SQLModel
from enum import Enum
from datetime import date
from pydantic import EmailStr


class ExclusionType(str, Enum):
    shift = "shift"
    day = "day"


class Staff(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    first_name: str
    last_name: str
    email: EmailStr = Field(unique=True)
    position: str = Field(index=True)
    contract_hours: int = Field(default=40)
    age: int = Field(nullable=True, default=None)

    exclusions: list["Exclusion"] = Relationship(back_populates="staff")
    schedules: list["Schedule"] = Relationship(back_populates="staff")


class Exclusion(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    staff_id: int = Field(foreign_key="staff.id")

    type: ExclusionType
    value: str

    staff: Staff | None = Relationship(back_populates="exclusions")


class Department(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    name: str = Field(unique=True)
    min_staff: int = Field(default=1)
    max_staff: int = Field(default=1)
    include: bool = Field(default=True)

    schedules: list["Schedule"] = Relationship(back_populates="department")


class ScheduleWeek(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    week_start: date
    week_end: date
    complete: bool = Field(default=False)

    schedules: list["Schedule"] = Relationship(back_populates="week")


class Schedule(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)

    week_id: int = Field(foreign_key="scheduleweek.id")
    staff_id: int = Field(foreign_key="staff.id")
    department_id: int = Field(foreign_key="department.id")

    week_date: date

    week_day: str
    time: str

    week: ScheduleWeek = Relationship(back_populates="schedules")
    staff: Staff = Relationship(back_populates="schedules")
    department: Department = Relationship(back_populates="schedules")
