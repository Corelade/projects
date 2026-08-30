from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, TypedDict
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
from utils import *
from structures import *
from app import to_normal_dict
import logging, json, datetime

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# python3 -m fastapi dev api.py for running server


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


@app.get("/schedule", response_model=ScheduleResponse | dict)
def home(week_start: str, db: SessionDep):

    week_end, generated_at, schedule = get_week_schedule(week_start=week_start, db=db)
    # if not schedule:
    #     raise HTTPException(
    #         status_code=404,
    #         detail="No Schedule for this week",
    #     )

    return {
        "week_start": str(week_start),
        "week_end": str(week_end),
        "schedule": schedule,
        "generated_at": str(generated_at),
    }


@app.post("/schedule/generate", response_model=ScheduleResponse)
def generate_schedule(data: WeekRequest, db: SessionDep):
    week_start = data.week_start
    schedule = create_schedule(week_start, db)

    week_end, generated_at, schedule = get_week_schedule(db=db, week_start=week_start)

    return {
        "week_start": str(week_start),
        "week_end": str(week_end),
        "schedule": schedule,
        "generated_at": str(generated_at),
    }


@app.post("/schedule/update", response_model=ScheduleCellResponse)
def update_cell(data: UpdateCellRequest, db: SessionDep):
    week_start = data.week_start
    department_id = data.department_id
    day = data.day
    shift = data.shift
    staff_ids = data.staff_ids

    _, _, schedule = get_week_schedule(db=db, week_start=week_start, regenerate=True)

    department_instances = DepartmentData.list_departments()
    staff_instances = StaffData.list_staff_members()

    department_instance = [
        dept for dept in department_instances if dept.id == department_id
    ][0]
    staff_members = [stf for stf in staff_instances if stf.id in staff_ids]

    schedule[day][department_instance][shift] = staff_members

    res = update_schedule(schedule, department_instances, staff_instances)["result"]

    current_week = get_week(week_start, db)

    if res:
        save_schedule(res=res, current_week=current_week, db=db)

    return {
        "department_id": department_id,
        "day": day,
        "shift": shift,
        "staff": [
            {"staff_id": stf.id, "staff_name": stf.name}
            for stf in res[day][department_instance][shift]
        ],
    }


@app.post("/create-staff", response_model=StaffResponse)
def create_staff(data: StaffCreateRequest, db: SessionDep):
    try:
        StaffData(
            name=data.first_name,
            id=None,
            shift_exclusion_list=data.shift_exclusions,
            day_exclusion_list=data.day_exclusions,
            contract_hours=data.contract_hours,
            min_hours=data.min_hours,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    staff = Staff(
        first_name=data.first_name,
        last_name=data.last_name,
        position=data.position,
        contract_hours=int(data.contract_hours),
        email=data.email,
        min_hours=data.min_hours,
    )

    try:
        db.add(staff)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Email already exists")

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

    StaffData.reset()

    return staff


@app.get("/list_staff", response_model=list[StaffResponse])
def list_staff(db: SessionDep):
    statement = (
        select(Staff)
        .where(Staff.deleted == False)
        .options(selectinload(Staff.exclusions))
    )
    staff_list = db.exec(statement).all()
    return staff_list


@app.patch("/staff/{id}", response_model=StaffResponse)
def update_staff(
    id: int,
    data: StaffUpdateRequest,
    db: SessionDep,
):
    statement = (
        select(Staff).where(Staff.id == id).options(selectinload(Staff.exclusions))
    )

    staff_instance = db.exec(statement).first()

    if not staff_instance:
        raise HTTPException(
            status_code=404,
            detail="Staff not found",
        )

    updates = data.model_dump(
        exclude_unset=True,
        exclude={"day_exclusions", "shift_exclusions"},
    )

    for field, value in updates.items():
        setattr(staff_instance, field, value)

    if "day_exclusions" in data.model_fields_set:
        for exclusion in staff_instance.exclusions:
            if exclusion.type == ExclusionType.day:
                db.delete(exclusion)

        for day in data.day_exclusions or []:
            db.add(
                Exclusion(
                    staff=staff_instance,
                    type=ExclusionType.day,
                    value=day,
                )
            )

    if "shift_exclusions" in data.model_fields_set:
        for exclusion in staff_instance.exclusions:
            if exclusion.type == ExclusionType.shift:
                db.delete(exclusion)

        for shift in data.shift_exclusions or []:
            db.add(
                Exclusion(
                    staff=staff_instance,
                    type=ExclusionType.shift,
                    value=shift,
                )
            )

    db.commit()
    db.refresh(staff_instance)

    return staff_instance


@app.delete("/staff/{id}", response_model=StaffResponse)
def delete_staff(id, db: SessionDep):
    staff_instance = db.get(Staff, id)

    if not staff_instance or staff_instance.deleted:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )
    staff_instance.deleted = True

    db.commit()
    db.refresh(staff_instance)

    return staff_instance


@app.get("/departments", response_model=list[DepartmentResponse])
def list_departments(db: SessionDep):
    statement = select(Department).where(Department.deleted == False)
    department_list = db.exec(statement).all()

    return department_list


@app.post("/create_department", response_model=DepartmentResponse)
def create_department(data: DepartmentCreateRequest, db: SessionDep):
    statement = select(Department).where(
        Department.name == data.name.lower(), Department.deleted == True
    )
    department = db.exec(statement).first()

    if department:
        department.deleted = False
        db.add(department)
        db.commit()
        db.refresh(department)
        return department

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


@app.patch("/departments/{id}", response_model=DepartmentResponse)
def update_department(id, data: DepartmentCreateRequest, db: SessionDep):
    department = db.get(Department, id)

    if not department or department.deleted:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )

    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(department, field, value)

    db.commit()
    db.refresh(department)

    return department


@app.delete("/departments/{id}")
def delete_department(id, db: SessionDep):
    department = db.get(Department, id)
    if not department or department.deleted:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )

    department.deleted = True

    db.commit()
    db.refresh(department)

    return department
