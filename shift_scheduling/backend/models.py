from sqlmodel import Field, Relationship, SQLModel
from enum import Enum
from datetime import date, datetime
from pydantic import EmailStr, ConfigDict, model_validator
from structures import ExclusionType
from sqlalchemy import UniqueConstraint


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    password: str

    staff: list["Staff"] = Relationship(back_populates="creator")
    department: list["Department"] = Relationship(back_populates="creator")
    schedule: list["Schedule"] = Relationship(back_populates="creator")
    week: list["ScheduleWeek"] = Relationship(back_populates="creator")
    weekly_hours_worked: list["StaffWeeklyHours"] = Relationship(
        back_populates="creator"
    )


class Staff(SQLModel, table=True):
    model_config = ConfigDict(validate_assignment=True)

    id: int | None = Field(primary_key=True, default=None)
    first_name: str
    last_name: str
    email: EmailStr = Field(unique=True)
    position: str = Field(index=True)
    contract_hours: int = Field(default=40, ge=8)
    min_hours: int = Field(default=8, ge=8)
    age: int | None = Field(nullable=True, default=None)
    deleted: bool = Field(default=False)
    creator_id: int = Field(foreign_key="user.id", nullable=True)

    exclusions: list["Exclusion"] = Relationship(back_populates="staff")
    schedules: list["Schedule"] = Relationship(back_populates="staff")

    weekly_hours_worked: list["StaffWeeklyHours"] = Relationship(back_populates="staff")

    creator: User = Relationship(back_populates="staff")


class Exclusion(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    staff_id: int = Field(foreign_key="staff.id")

    type: ExclusionType
    value: str

    staff: Staff | None = Relationship(back_populates="exclusions")


class Department(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("name", "creator_id"),)

    id: int | None = Field(primary_key=True, default=None)
    name: str = Field(nullable=False, min_length=3)
    min_staff: int = Field(default=1, ge=1)
    max_staff: int = Field(default=1, ge=1)
    deleted: bool = Field(default=False)
    creator_id: int = Field(foreign_key="user.id", nullable=True)

    schedules: list["Schedule"] = Relationship(back_populates="department")
    creator: User = Relationship(back_populates="department")


class ScheduleWeek(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    week_start: date
    week_end: date
    complete: bool = Field(default=False)
    generated_at: datetime = Field(nullable=True, default=datetime.now())
    creator_id: int | None = Field(foreign_key="user.id", nullable=True, default=None)

    schedules: list["Schedule"] = Relationship(back_populates="week")

    staff_weekly_hours_worked: list["StaffWeeklyHours"] = Relationship(
        back_populates="week"
    )
    creator: User = Relationship(back_populates="week")


class Schedule(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)

    week_id: int = Field(foreign_key="scheduleweek.id")
    staff_id: int = Field(foreign_key="staff.id")
    department_id: int = Field(foreign_key="department.id")
    creator_id: int = Field(foreign_key="user.id", nullable=True)

    week_date: date

    week_day: str
    time: str

    week: ScheduleWeek = Relationship(back_populates="schedules")
    staff: Staff = Relationship(back_populates="schedules")
    department: Department = Relationship(back_populates="schedules")

    creator: User = Relationship(back_populates="schedule")


class StaffWeeklyHours(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)

    hours: int = Field(default=0)

    staff_id: int = Field(foreign_key="staff.id")
    week_id: int = Field(foreign_key="scheduleweek.id")
    creator_id: int | None = Field(foreign_key="user.id", nullable=True, default=None)

    week: ScheduleWeek = Relationship(back_populates="staff_weekly_hours_worked")
    staff: Staff = Relationship(back_populates="weekly_hours_worked")
    creator: User = Relationship(back_populates="weekly_hours_worked")
