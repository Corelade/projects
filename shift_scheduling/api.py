from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from sqlmodel import SQLModel, create_engine, Field, Session, select
from contextlib import asynccontextmanager
from db import SessionDep, create_db_and_tables
from models import *
from pydantic import BaseModel
from typing import Literal
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from classes import StaffData
from collections import defaultdict
from utils import get_date_from_week
from structures import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    create_db_and_tables()
    yield

    # Shutdown logic
    # print("Shutting down app")


app = FastAPI(lifespan=lifespan)

origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=ScheduleResponse)
def home(db: SessionDep):
    SHIFTS = ["morning", "afternoon", "evening"]

    grouped = defaultdict(
        lambda: {
            "date": None,
            "schedule": defaultdict(lambda: {shift: [] for shift in SHIFTS}),
        }
    )

    schedule_statement = select(Schedule).options(
        selectinload(Schedule.staff),
        selectinload(Schedule.department),
        selectinload(Schedule.week),
    )

    schedule_list = db.exec(schedule_statement).all()

    for s in schedule_list:
        day = s.week_day.capitalize()
        dept = s.department.name.capitalize()
        shift = s.time

        grouped[day]["date"] = get_date_from_week(s.week.week_start, day)

        grouped[day]["schedule"][dept][shift].append(
            f"{s.staff.first_name} {s.staff.last_name}"
        )

    result = {
        day: {
            "date": data["date"],
            "schedule": [
                {dept: dict(shift_data)}
                for dept, shift_data in data["schedule"].items()
            ],
        }
        for day, data in grouped.items()
    }

    return {
        "success": True,
        "schedule": result,
    }


@app.post("/create-staff")
def create_staff(data: StaffCreateRequest, db: SessionDep) -> StaffRead:
    try:
        StaffData(
            name=data.first_name,
            id=None,
            shift_exclusion_list=data.shift_exclusions,
            day_exclusion_list=data.day_exclusions,
            contract_hours=data.contract_hours,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    staff = Staff(
        first_name=data.first_name,
        last_name=data.last_name,
        position=data.position,
        contract_hours=int(data.contract_hours),
        email=data.email,
    )

    try:
        db.add(staff)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f'Email already exists: {str(e)}')

    db.refresh(staff)

    exclusions = []

    for shift in data.shift_exclusions:
        exclusions.append(
            Exclusion(staff_id=staff.id, type=ExclusionType.shift, value=shift)
        )

    for day in data.day_exclusions:
        exclusions.append(
            Exclusion(staff_id=staff.id, type=ExclusionType.day, value=day)
        )

    db.add_all(exclusions)
    db.commit()

    return staff


@app.get("/list_staff", response_model=list[StaffRead])
def list_staff(db: SessionDep):
    statement = select(Staff).options(selectinload(Staff.exclusions))

    staff_list = db.exec(statement).all()
    return staff_list


@app.post("/create_department", response_model=Department)
def create_department(data: DepartmentCreateRequest, db: SessionDep):
    department = Department(
        name=data.name.lower(), min_staff=data.min_staff, max_staff=data.max_staff
    )

    try:
        db.add(department)
        db.commit()
        db.refresh(department)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Department already exists")

    return department


@app.get("/departments", response_model=list[Department])
def list_departments(db: SessionDep):
    statement = select(Department)
    department_list = db.exec(statement).all()

    return department_list