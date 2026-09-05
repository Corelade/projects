from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select
from contextlib import asynccontextmanager
from db import SessionDep, create_db_and_tables
from models import *
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from classes import StaffData
from utils import *
from structures import *
import logging, json, datetime, os, re
from structs.auth_struct import AuthResponse, AuthUser, Credentials, Token
from auth.auth import (
    get_password_hash,
    get_user,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    UserQuery,
)

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

origins = [
    # "http://localhost:5173",
    os.getenv("FRONTEND_URL"),
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(data: Credentials, db: SessionDep):
    username = data.username
    password = data.password

    USERNAME_PATTERN = r"^[a-zA-Z][a-zA-Z0-9._-]*$"
    PASSWORD_PATTERN = r"^[a-zA-Z0-9@!_-]*$"

    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is too short",
        )

    if not re.fullmatch(PASSWORD_PATTERN, password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password can only contain Numbers, Letters and @!_-",
        )

    if not re.fullmatch(USERNAME_PATTERN, username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username",
        )

    try:
        hashed_password = get_password_hash(password)
        user = User(username=username, password=hashed_password)
        db.add(user)
        db.commit()

    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is not available",
        )

    return


@app.post("/auth/login", response_model=AuthResponse)
def login(data: Credentials, db: SessionDep):
    "This is to return a token user will use in subsequent requests"
    user = get_user(data.username, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials"
        )

    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"user": user.username}, access_token_expires)
    token = Token(access_token=access_token, token_type="bearer")
    return {
        "token": access_token,
        "user": {"id": user.id, "username": user.username},
    }


@app.get("/schedule", response_model=ScheduleResponse | dict)
def home(week_start: str, db: SessionDep, user: UserQuery):
    week_end, generated_at, schedule = get_week_schedule(
        user=user, week_start=week_start, db=db
    )
    # if not schedule:
    #     raise HTTPException(
    #         status_code=status.HTTP_200_OK,
    #         detail="No Schedule for this week",
    #     )

    return {
        "week_start": str(week_start),
        "week_end": str(week_end),
        "schedule": schedule,
        "generated_at": str(generated_at),
    }


@app.post("/schedule/generate", response_model=ScheduleResponse)
def generate_schedule(data: WeekRequest, db: SessionDep, user: UserQuery):
    week_start = data.week_start

    try:
        schedule = create_schedule(week_start, db, user)
    except ScheduleError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

    week_end, generated_at, schedule = get_week_schedule(
        user=user, db=db, week_start=week_start
    )

    return {
        "week_start": str(week_start),
        "week_end": str(week_end),
        "schedule": schedule,
        "generated_at": str(generated_at),
    }


@app.post("/schedule/update", response_model=ScheduleCellResponse)
def update_cell(data: UpdateCellRequest, db: SessionDep, user: UserQuery):
    week_start = data.week_start
    department_id = data.department_id
    day = data.day
    shift = data.shift
    staff_ids = data.staff_ids

    _, _, schedule = get_week_schedule(
        user=user, db=db, week_start=week_start, regenerate=True
    )

    department_instances = DepartmentData.list_departments()
    staff_instances = StaffData.list_staff_members()

    department_instance = [
        dept for dept in department_instances if dept.id == department_id
    ][0]
    staff_members = [stf for stf in staff_instances if stf.id in staff_ids]

    schedule[day][department_instance][shift] = staff_members

    res = update_schedule(schedule, department_instances, staff_instances)["result"]

    current_week = get_week(week_start, db, user)

    if res:
        save_schedule(user=user, res=res, current_week=current_week, db=db)

    return {
        "department_id": department_id,
        "day": day,
        "shift": shift,
        "staff": [
            {"staff_id": stf.id, "staff_name": stf.name}
            for stf in res[day][department_instance][shift]
        ],
    }


@app.post("/create_staff", response_model=StaffResponse)
def create_staff(data: StaffCreateRequest, db: SessionDep, user: UserQuery):
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
        creator=user,
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
def list_staff(db: SessionDep, user: UserQuery):
    statement = (
        select(Staff)
        .where(Staff.deleted == False, Staff.creator == user)
        .options(selectinload(Staff.exclusions))
    )
    staff_list = db.exec(statement).all()
    return staff_list


@app.patch("/staff/{id}", response_model=StaffResponse)
def update_staff(id: int, data: StaffUpdateRequest, db: SessionDep, user: UserQuery):
    statement = (
        select(Staff)
        .where(Staff.id == id, Staff.creator == user)
        .options(selectinload(Staff.exclusions))
    )

    staff_instance = db.exec(statement).first()

    if not staff_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff not found",
        )

    if not staff_instance.creator == user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorised to modify this resource",
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
def delete_staff(id, db: SessionDep, user: UserQuery):
    staff_instance = db.get(Staff, id)

    if not staff_instance or staff_instance.deleted:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )

    if not staff_instance.creator == user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorised to modify this resource",
        )

    staff_instance.deleted = True

    db.commit()
    db.refresh(staff_instance)

    return staff_instance


@app.get(
    "/departments",
    response_model=list[DepartmentResponse],
    status_code=status.HTTP_200_OK,
)
def list_departments(db: SessionDep, user: UserQuery):
    statement = select(Department).where(
        Department.deleted == False, Department.creator == user
    )
    department_list = db.exec(statement).all()

    return department_list


@app.post(
    "/create_department",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_department(data: DepartmentCreateRequest, db: SessionDep, user: UserQuery):
    # if department existed, recover the deleted instance
    statement = select(Department).where(
        Department.name == data.name.lower(),
        Department.deleted.is_(True),
        Department.creator_id == user.id,
    )
    department = db.exec(statement).first()

    if department:
        department.deleted = False
        db.add(department)
        db.commit()
        db.refresh(department)
        return department

    # No department exists, create new one
    department = Department(
        name=data.name.lower(),
        min_staff=data.min_staff,
        max_staff=data.max_staff,
        creator=user,
    )

    try:
        db.add(department)
        db.commit()
        db.refresh(department)
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Department already exists"
        )

    return department


@app.patch(
    "/departments/{id}",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
)
def update_department(
    id, data: DepartmentUpdateRequest, db: SessionDep, user: UserQuery
):
    department = db.get(Department, id)

    if not department or department.deleted:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )

    if not department.creator == user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorised to modify this resource",
        )

    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(department, field, value)

    db.commit()
    db.refresh(department)

    return department


@app.delete("/departments/{id}")
def delete_department(id, db: SessionDep, user: UserQuery):
    department = db.get(Department, id)

    if not department or department.deleted:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )

    if not department.creator == user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorised to modify this resource",
        )

    department.deleted = True

    db.commit()
    db.refresh(department)

    return department
