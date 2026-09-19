from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
from app import scheduler, print_schedule, to_normal_dict, update_schedule
from classes import *
import json
from prompt_toolkit import prompt
from typing import TypedDict
from models import *
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, Session
from db import engine
from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from typing import get_args
from collections import Counter
from datetime import datetime, timedelta
from app import ScheduleError
from utils import (
    check_staff_hours,
    create_schedule,
    get_week,
    get_week_schedule,
    save_schedule,
)
from structures import *

# TODO AI
"""
- Department
    - Create ✅
    - Read ✅
    - Update ✅
    - Delete ✅
- Staff
    - Create ✅
    - Read ✅
    - Update ✅
    - Delete ✅
- Schedule
    - Create ✅
    - Read ✅
    - Update ✅
    - Delete ✅
"""


class DepartmentDict(TypedDict):
    name: str
    min_staff: int
    max_staff: int
    id: int | None


class StaffDict(TypedDict):
    first_name: str
    last_name: str
    email: str
    position: str
    shift_exclusion_list: list
    day_exclusion_list: list
    contract_hours: int
    min_hours: int
    id: int | None = None


departmentSchema = {
    "type": "object",
    # "description": "A list containing all of the currently available departments",
    "properties": {
        "name": {
            "type": "string",
            "description": "The name of the department.",
        },
        "max_staff": {
            "type": "integer",
            "description": "The maximum number of staff that can be assigned to the departent at any given time.",
            "default": 1,
        },
        "min_staff": {
            "type": "integer",
            "description": "The minimum number of staff that can be assigned to the departent at any given time.",
            "default": 1,
        },
        "id": {
            "type": ["integer", "null"],
            "description": "Database identifier for this department.",
        },
    },
    "required": ["name"],
    "additionalProperties": False,
}

staffSchema = {
    "type": "object",
    "properties": {
        "first_name": {
            "type": "string",
            "description": "The first name of staff",
        },
        "last_name": {
            "type": "string",
            "description": "The last name of staff",
        },
        "email": {
            "type": "string",
            "description": "The email address of staff. Must be unique.",
        },
        "position": {
            "type": "string",
            "description": "The position of staff in the company.",
            "enum": [
                "associate",
            ],
            "default": "associate",
        },
        "shift_exclusion_list": {
            "type": "array",
            "description": "The shifts this staff member cannot work. Leave empty if the staff member has no shift restrictions.",
            "items": {
                "type": "string",
                "enum": [
                    "morning",
                    "afternoon",
                    "evening",
                ],
            },
            "default": [],
        },
        "day_exclusion_list": {
            "type": "array",
            "description": "The days this staff member cannot work. Leave empty if the staff member has no shift restrictions.",
            "items": {
                "type": "string",
                "enum": [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                ],
            },
            "default": [],
        },
        "contract_hours": {
            "type": "integer",
            "description": "The number of hours this staff can work in a week. Shouldn't be more than 40",
            "default": 40,
        },
        "min_hours": {
            "type": "integer",
            "description": "The minimum number of hours this staff can work in a week. Shouldn't be more than contract hours",
            "default": 8,
        },
    },
    "required": ["first_name", "last_name", "email"],
    "additionalProperties": False,
}

staffLookupProperties = {
    "id": {"type": "number", "description": "The staff ID."},
    "email": {"type": "string", "description": "The staff email."},
    "name": {
        "type": "string",
        "description": "Just the person's name (first, last, full or the start of it), e.g. 'benjamin'. No other words.",
    },
}

weekStartProperty = {
    "type": "string",
    "description": "Any date in the week, as YYYY-MM-DD. Weeks start on Monday.",
}


load_dotenv()
import os

api_key = os.getenv("SHIFT_AI_KEY")
client = AsyncOpenAI(api_key=api_key)


def create_department(
    department_objects: list[DepartmentDict] | DepartmentDict, user: User, db=None
):
    try:
        if isinstance(department_objects, dict):
            department_objects = [department_objects]
        departments = [DepartmentData(**dept) for dept in department_objects]
        department_json = []

        # add to db
        # creator_id, not creator=user: the chat reuses one detached User for the
        # whole conversation, and attaching it here expires it when this session
        # closes, breaking every later tool call with DetachedInstanceError.
        department_instances = [
            Department(
                name=dept.name,
                min_staff=dept.min_staff,
                max_staff=dept.max_staff,
                creator_id=user.id,
            )
            for dept in departments
        ]
        try:
            with Session(engine) as db:
                db.add_all(department_instances)
                db.commit()
                department_json = [
                    DepartmentResponse.model_validate(dept, from_attributes=True).model_dump()
                    for dept in department_instances
                ]
        except IntegrityError as e:
            return json.dumps({"error": str(e), "type": "IntegrityError"})
        return department_json
    except Exception as e:
        print(str(e))
        return json.dumps({"error": str(e)})


def get_department(user, id: int | None = None, name: str | None = None):
    "Get departments by id or name. Returns all departments when no filter is given"
    if user is None:
        return json.dumps({"error": "User is required"})

    # Models often fill unused arguments with 0 or "", so only a real value counts
    id = int(id) if id else None
    name = (name or "").strip().lower()

    with Session(engine) as db:
        statement = select(Department).where(
            Department.creator_id == user.id, Department.deleted == False
        )
        if id is not None:
            statement = statement.where(Department.id == id)

        departments = db.exec(statement.order_by(Department.name)).all()

        if id is None and name:
            # Exact name first, then any department whose name contains it
            exact = [d for d in departments if d.name == name]
            departments = exact or [d for d in departments if name in d.name]

        if not departments:
            return {"error": "No department found"}

        return [
            DepartmentResponse.model_validate(d, from_attributes=True).model_dump()
            for d in departments
        ]


def find_department(db, user, id=None, name=None):
    "Find one of the user's (non-deleted) departments by id or name"
    statement = select(Department).where(
        Department.creator_id == user.id, Department.deleted == False
    )
    if id is not None:
        statement = statement.where(Department.id == id)
    else:
        statement = statement.where(Department.name == name.strip().lower())

    return db.exec(statement).first()


def update_department(
    user, updates: dict, id: int | None = None, name: str | None = None
):
    "Update a department"
    if id is None and name is None:
        return json.dumps({"error": "Department id or name is required"})

    try:
        data = DepartmentUpdateRequest(**updates)
    except ValueError as e:
        return json.dumps({"error": str(e)})

    with Session(engine) as db:
        department = find_department(db, user, id, name)

        if not department:
            return json.dumps({"error": "Department not found"})

        updates = data.model_dump(exclude_unset=True)
        if "name" in updates:
            updates["name"] = updates["name"].strip().lower()
            if len(updates["name"]) < 3:
                return json.dumps(
                    {"error": "Department name must be at least 3 characters"}
                )

        min_staff = updates.get("min_staff", department.min_staff)
        max_staff = updates.get("max_staff", department.max_staff)
        if min_staff > max_staff:
            return json.dumps({"error": "min_staff cannot be greater than max_staff"})

        for field, value in updates.items():
            setattr(department, field, value)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return json.dumps({"error": "A department with that name already exists"})

        db.refresh(department)

        return DepartmentResponse.model_validate(department, from_attributes=True)


def delete_department(user, id: int | None = None, name: str | None = None):
    "Soft delete a department. It can be restored by creating it again"
    if id is None and name is None:
        return json.dumps({"error": "Department id or name is required"})

    with Session(engine) as db:
        department = find_department(db, user, id, name)

        if not department:
            return json.dumps({"error": "Department not found"})

        department.deleted = True
        db.commit()

        return {"deleted": True, "id": department.id, "name": department.name}


def staff_json(staff: Staff):
    return {
        "id": staff.id,
        "first_name": staff.first_name,
        "last_name": staff.last_name,
        "email": staff.email,
        "position": staff.position,
        "contract_hours": staff.contract_hours,
        "min_hours": staff.min_hours,
        "shift_exclusion_list": [
            e.value for e in staff.exclusions if e.type == ExclusionType.shift
        ],
        "day_exclusion_list": [
            e.value for e in staff.exclusions if e.type == ExclusionType.day
        ],
    }


def create_staff(staff_objects: list[StaffDict] | StaffDict, user: User):
    if isinstance(staff_objects, dict):
        staff_objects = [staff_objects]

    created = []
    errors = []

    with Session(engine) as db:
        for stf in staff_objects:
            try:
                data = StaffCreateRequest(
                    first_name=stf["first_name"],
                    last_name=stf["last_name"],
                    email=stf["email"],
                    position=stf.get("position", "associate"),
                    contract_hours=stf.get("contract_hours", 40),
                    min_hours=stf.get("min_hours", 8),
                    shift_exclusions=stf.get("shift_exclusion_list", []),
                    day_exclusions=stf.get("day_exclusion_list", []),
                )
                check_staff_hours(
                    data.first_name,
                    data.contract_hours,
                    data.min_hours,
                    data.shift_exclusions,
                    data.day_exclusions,
                )
            except (ValueError, KeyError) as e:
                errors.append({"staff": stf, "error": str(e)})
                continue

            staff = Staff(
                first_name=data.first_name,
                last_name=data.last_name,
                position=data.position,
                contract_hours=data.contract_hours,
                email=data.email,
                min_hours=data.min_hours,
                creator_id=user.id,
            )
            staff.exclusions = [
                Exclusion(type=ExclusionType.shift, value=shift)
                for shift in data.shift_exclusions
            ] + [
                Exclusion(type=ExclusionType.day, value=day)
                for day in data.day_exclusions
            ]

            try:
                db.add(staff)
                db.commit()
            except IntegrityError:
                db.rollback()
                errors.append({"staff": stf, "error": "Email already exists"})
                continue

            db.refresh(staff)
            created.append(staff_json(staff))

    return {"created": created, "errors": errors}


def find_staff(db, user, id=None, email=None, name=None) -> list[Staff]:
    "Find the user's (non-deleted) staff by id, email or name. No filter returns everyone"
    with Session(engine) as db:
        statement = (
            select(Staff)
            .where(Staff.creator_id == user.id, Staff.deleted == False)
            .options(selectinload(Staff.exclusions))
        )
        # Models often fill unused arguments with 0 or "", so only a real value counts
        id = int(id) if id else None
        email = (email or "").strip()
        name = (name or "").strip()

        if id is not None:
            statement = statement.where(Staff.id == id)
        elif email:
            statement = statement.where(Staff.email == email)

        staff_list = db.exec(statement).all()

        if id is None and not email and name:
            staff_list = match_staff_name(staff_list, name)

        return staff_list


def match_staff_name(staff_list: list[Staff], query: str) -> list[Staff]:
    """
    Forgiving name search: each word of the query that starts a first or last
    name counts, so "benjamin", "Ben", "benjamin cook" and "staff benjamin" all
    find Benjamin Cook. Returns the staff matching the most words.
    """
    words = [w for w in query.lower().replace(",", " ").split() if len(w) >= 2]

    def score(stf: Staff) -> int:
        parts = f"{stf.first_name} {stf.last_name}".lower().split()
        return sum(any(part.startswith(w) for part in parts) for w in words)

    scored = [(score(stf), stf) for stf in staff_list]
    best = max((s for s, _ in scored), default=0)
    return [stf for s, stf in scored if s == best] if best else []


def find_one_staff(db, user, id=None, email=None, name=None):
    "Returns (staff, error). Errors if nothing or more than one staff matches"
    if id is None and not email and not name:
        return None, {"error": "Staff id, email or name is required"}

    staff_list = find_staff(db, user, id, email, name)

    if not staff_list:
        return None, {"error": "Staff not found"}

    if len(staff_list) > 1:
        return None, {
            "error": "More than one staff member matches. Ask the user which one.",
            "matches": [staff_json(stf) for stf in staff_list],
        }

    return staff_list[0], None


def get_staff(
    user, id: int | None = None, email: str | None = None, name: str | None = None
):
    "Get staff by id, email or name. Returns all staff when no filter is given"
    with Session(engine) as db:
        staff_list = find_staff(db, user, id, email, name)
        if not staff_list:
            return {"error": "No staff found"}

        return [staff_json(stf) for stf in staff_list]


def update_staff(
    user,
    updates: dict,
    id: int | None = None,
    email: str | None = None,
    name: str | None = None,
):
    "Update a staff member's details, hours or exclusions"
    with Session(engine) as db:
        staff, error = find_one_staff(db, user, id, email, name)
        if error:
            return error

        current = staff_json(staff)
        shift_exclusions = updates.get(
            "shift_exclusion_list", current["shift_exclusion_list"]
        )
        day_exclusions = updates.get(
            "day_exclusion_list", current["day_exclusion_list"]
        )

        try:
            data = StaffUpdateRequest(
                first_name=updates.get("first_name", staff.first_name),
                last_name=updates.get("last_name", staff.last_name),
                position=updates.get("position", staff.position),
                contract_hours=updates.get("contract_hours", staff.contract_hours),
                min_hours=updates.get("min_hours", staff.min_hours),
                shift_exclusions=shift_exclusions,
                day_exclusions=day_exclusions,
            )
            check_staff_hours(
                data.first_name,
                data.contract_hours,
                data.min_hours,
                data.shift_exclusions,
                data.day_exclusions,
            )
        except ValueError as e:
            return {"error": str(e)}

        for field in (
            "first_name",
            "last_name",
            "position",
            "contract_hours",
            "min_hours",
        ):
            setattr(staff, field, getattr(data, field))

        if "shift_exclusion_list" in updates or "day_exclusion_list" in updates:
            for exclusion in staff.exclusions:
                db.delete(exclusion)

            staff.exclusions = [
                Exclusion(type=ExclusionType.shift, value=shift)
                for shift in data.shift_exclusions
            ] + [
                Exclusion(type=ExclusionType.day, value=day)
                for day in data.day_exclusions
            ]

        db.commit()
        db.refresh(staff)

        return staff_json(staff)


def delete_staff(
    user, id: int | None = None, email: str | None = None, name: str | None = None
):
    "Soft delete a staff member"
    with Session(engine) as db:
        staff, error = find_one_staff(db, user, id, email, name)
        if error:
            return error

        staff.deleted = True
        db.commit()

        return {
            "deleted": True,
            "id": staff.id,
            "name": f"{staff.first_name} {staff.last_name}",
        }


def to_week_start(week_start: str):
    "Returns (monday of the given date as YYYY-MM-DD, error)"
    try:
        day = datetime.strptime(week_start, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None, {"error": "Week start must be a date in YYYY-MM-DD format"}

    return str(day - timedelta(days=day.weekday())), None


def schedule_json(db, user: User, week_start: str):
    week_end, generated_at, schedule = get_week_schedule(
        user=user, db=db, week_start=week_start
    )
    if not schedule:
        return {
            "week_start": week_start,
            "schedule": {},
            "message": "No schedule for this week",
        }

    department_names = {
        dept.id: dept.name
        for dept in db.exec(
            select(Department).where(Department.creator_id == user.id)
        ).all()
    }

    return {
        "week_start": week_start,
        "week_end": str(week_end),
        "generated_at": str(generated_at),
        "schedule": {
            day: {
                department_names.get(dept_id, dept_id): dict(shifts)
                for dept_id, shifts in departments.items()
            }
            for day, departments in schedule.items()
        },
    }


def ai_scheduler(week_start: str, user: User):
    "Generate (or refresh) the schedule for a week"
    week_start, error = to_week_start(week_start)
    if error:
        return error

    with Session(engine) as db:
        user = db.get(User, user.id)
        try:
            create_schedule(week_start, db, user)
        except ScheduleError as e:
            # 304: the week already has a schedule and nothing changed
            if e.status_code != 304:
                return {"error": e.message}

        return schedule_json(db, user, week_start)


def get_schedule(week_start: str, user: User):
    "Get the saved schedule for a week"
    week_start, error = to_week_start(week_start)
    if error:
        return error

    with Session(engine) as db:
        return schedule_json(db, db.get(User, user.id), week_start)


def ai_update_scheduler(
    week_start: str,
    day: str,
    shift: str,
    staff_ids: list[int],
    user: User,
    department_id: int | None = None,
    department_name: str | None = None,
):
    "Set the staff working a department's shift on a day, then re-balance the week"
    week_start, error = to_week_start(week_start)
    if error:
        return error

    day, shift = day.lower(), shift.lower()
    if day not in get_args(DAY) or shift not in get_args(SHIFTS):
        return {"error": "Invalid day or shift"}

    with Session(engine) as db:
        user = db.get(User, user.id)
        department = find_department(db, user, department_id, department_name or "")
        if not department:
            return {"error": "Department not found"}

        _, _, schedule = get_week_schedule(
            user=user, db=db, week_start=week_start, regenerate=True
        )
        if not schedule:
            return {"error": "No schedule for this week. Generate one first."}

        department_instances = DepartmentData.list_departments()
        staff_instances = [
            stf for stf in StaffData.list_staff_members() if not stf.unavailable
        ]

        department_instance = next(
            (dept for dept in department_instances if dept.id == department.id), None
        )
        staff_members = [stf for stf in staff_instances if stf.id in staff_ids]

        if department_instance is None:
            return {"error": "Department not found"}
        if len(staff_members) != len(set(staff_ids)):
            return {"error": "One or more staff members were not found"}

        schedule[day][department_instance][shift] = staff_members

        updated = update_schedule(schedule, department_instances, staff_instances)
        if not updated or not updated["result"]:
            return {"error": "That change would make the schedule invalid"}

        # Replace the week's saved rows with the updated schedule
        current_week = get_week(week_start, db, user)
        for row in db.exec(
            select(Schedule).where(Schedule.week_id == current_week.id)
        ).all():
            db.delete(row)
        db.flush()

        save_schedule(
            user=user, res=updated["result"], current_week=current_week, db=db
        )

        # Recalculate weekly hours (4 hours per shift)
        shifts_worked = Counter(
            row.staff_id
            for row in db.exec(
                select(Schedule).where(Schedule.week_id == current_week.id)
            ).all()
        )
        hours = {
            wh.staff_id: wh
            for wh in db.exec(
                select(StaffWeeklyHours).where(
                    StaffWeeklyHours.week_id == current_week.id
                )
            ).all()
        }
        for staff_id in set(hours) | set(shifts_worked):
            if staff_id not in hours:
                hours[staff_id] = StaffWeeklyHours(
                    staff_id=staff_id, week_id=current_week.id, creator_id=user.id
                )
                db.add(hours[staff_id])
            hours[staff_id].hours = 4 * shifts_worked[staff_id]

        db.commit()

        return schedule_json(db, user, week_start)


def delete_schedule(week_start: str, user: User):
    "Delete a week's schedule"
    week_start, error = to_week_start(week_start)
    if error:
        return error

    with Session(engine) as db:
        week = db.exec(
            select(ScheduleWeek).where(
                ScheduleWeek.week_start == week_start,
                ScheduleWeek.creator_id == user.id,
            )
        ).first()
        if not week:
            return {"error": "No schedule for this week"}

        for row in db.exec(select(Schedule).where(Schedule.week_id == week.id)).all():
            db.delete(row)
        for row in db.exec(
            select(StaffWeeklyHours).where(StaffWeeklyHours.week_id == week.id)
        ).all():
            db.delete(row)
        db.flush()
        db.delete(week)
        db.commit()

        return {"deleted": True, "week_start": week_start}


tools = [
    {
        "type": "function",
        "name": "create_department",
        "description": "A function for creating departments.",
        "parameters": {
            "type": "object",
            "properties": {
                "department_objects": {
                    "oneOf": [
                        departmentSchema,
                        {"type": "array", "items": departmentSchema},
                    ]
                },
            },
            "additionalProperties": False,
            "required": ["department_objects"],
        },
    },
    {
        "type": "function",
        "name": "get_department",
        "description": "A function for getting departments by id or name. Call it with no arguments to list all departments.",
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "number", "description": "The department ID."},
                "name": {
                    "type": "string",
                    "description": "The department name or part of it, e.g. 'shoes'. No other words.",
                },
            },
            "additionalProperties": False,
            "required": [],
        },
    },
    {
        "type": "function",
        "name": "update_department",
        "description": "A function for updating a department's name, minimum staff or maximum staff. Identify the department by id or name.",
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "number", "description": "The department ID."},
                "name": {
                    "type": "string",
                    "description": "The current department name.",
                },
                "updates": {
                    "type": "object",
                    "description": "Only the fields to change.",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The new department name.",
                        },
                        "min_staff": {"type": "integer", "minimum": 1},
                        "max_staff": {"type": "integer", "minimum": 1},
                    },
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
            "required": ["updates"],
        },
    },
    {
        "type": "function",
        "name": "delete_department",
        "description": "A function for deleting a department. Identify the department by id or name. Confirm with the user before calling.",
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "number", "description": "The department ID."},
                "name": {"type": "string", "description": "The department name."},
            },
            "additionalProperties": False,
            "required": [],
        },
    },
    {
        "type": "function",
        "name": "create_staff",
        "description": "A function for creating staff.",
        "parameters": {
            "type": "object",
            "properties": {
                "staff_objects": {
                    "oneOf": [
                        staffSchema,
                        {"type": "array", "items": staffSchema},
                    ]
                },
            },
            "additionalProperties": False,
            "required": ["staff_objects"],
        },
    },
    {
        "type": "function",
        "name": "get_staff",
        "description": "A function for getting staff by id, email or name. Call it with no arguments to list all staff.",
        "parameters": {
            "type": "object",
            "properties": staffLookupProperties,
            "additionalProperties": False,
            "required": [],
        },
    },
    {
        "type": "function",
        "name": "update_staff",
        "description": "A function for updating a staff member. Identify the staff by id, email or name. If more than one staff matches, ask the user which one.",
        "parameters": {
            "type": "object",
            "properties": {
                **staffLookupProperties,
                "updates": {
                    "type": "object",
                    "description": "Only the fields to change. Exclusion lists replace the existing ones.",
                    "properties": {
                        field: staffSchema["properties"][field]
                        for field in (
                            "first_name",
                            "last_name",
                            "position",
                            "contract_hours",
                            "min_hours",
                            "shift_exclusion_list",
                            "day_exclusion_list",
                        )
                    },
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
            "required": ["updates"],
        },
    },
    {
        "type": "function",
        "name": "delete_staff",
        "description": "A function for deleting a staff member. Identify the staff by id, email or name. Confirm with the user before calling.",
        "parameters": {
            "type": "object",
            "properties": staffLookupProperties,
            "additionalProperties": False,
            "required": [],
        },
    },
    {
        "type": "function",
        "name": "ai_scheduler",
        "description": "A function for generating the weekly shift schedule. Also refreshes an existing schedule after staff or department changes. Do not attempt to manually create the schedule",
        "parameters": {
            "type": "object",
            "properties": {"week_start": weekStartProperty},
            "required": ["week_start"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_schedule",
        "description": "A function for getting the saved shift schedule of a week.",
        "parameters": {
            "type": "object",
            "properties": {"week_start": weekStartProperty},
            "required": ["week_start"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "delete_schedule",
        "description": "A function for deleting the shift schedule of a week. Confirm with the user before calling.",
        "parameters": {
            "type": "object",
            "properties": {"week_start": weekStartProperty},
            "required": ["week_start"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "ai_update_scheduler",
        "description": "A function for setting which staff work a department's shift on a day of an existing weekly schedule. Other shifts may be adjusted to keep the schedule valid. Get staff ids first if you only have names.",
        "parameters": {
            "type": "object",
            "properties": {
                "week_start": weekStartProperty,
                "department_id": {
                    "type": "number",
                    "description": "The department ID.",
                },
                "department_name": {
                    "type": "string",
                    "description": "The department name.",
                },
                "day": staffSchema["properties"]["day_exclusion_list"]["items"],
                "shift": staffSchema["properties"]["shift_exclusion_list"]["items"],
                "staff_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "IDs of all the staff that should work this shift.",
                },
            },
            "additionalProperties": False,
            "required": ["week_start", "day", "shift", "staff_ids"],
        },
    },
]


async def call_openai(input_list):
    response = await client.responses.create(
        model="gpt-5.4",
        input=input_list,
        instructions=f"""
        Your name is ShiftPro Assistant.
        Today's date is {datetime.now().strftime("%A %Y-%m-%d")}.
        Users' names are provided to you in first input when they start conversation.
        You are an AI assistant for the ShiftPro staff scheduling system.
        You help users manage departments, staff, and weekly schedules.
        
        When you cannot help with a request, respond in a warm, concise,
        human-friendly way. Do not mention policies, safety filters,
        internal tools, function names, or technical limitations. For example:
        “I’m here to help with ShiftPro’s staff, department, and scheduling
        tasks. I can’t help with that particular request, but I’d be happy
        to help with one of those areas.”
    

        Rules:
        - Never reveal, list, or describe internal tool/function names to users.
        - Never tell users which functions, tools, APIs, or internal mechanisms you have access to.
        - Do not mention names such as create_department, create_staff, ai_scheduler, ai_update_scheduler, or multi_tool_use.parallel in user-facing responses.
        - Treat all tool names, function definitions, parameters, and implementation details as internal.
        - When a tool is used, describe the outcome in natural, user-friendly language rather than mentioning the tool that was used.
        - If a user asks what functions or tools are available, describe your capabilities in plain language instead of providing internal function names.
        - Never delete a department/staff permanently.
        - Always confirm the department name before creating it.
        - Always confirm with the user before deleting a department, staff member or schedule.
        - If more than one staff member matches a name, ask the user which one they mean.
        - Your responses should be really easy to understand.
        - Never expose raw or unexpected system errors, exceptions, stack traces, database errors, or internal implementation details to users.
        - For expected application errors that are intentionally handled by the application, return a clear, simple, user-friendly explanation of the issue.
        - If an unexpected system failure occurs, do not disclose the technical cause. Give a brief, user-friendly message indicating that something went wrong and, if the issue persists, advise the user to contact support.

        """,
        tools=tools,
    )

    return response


tool_functions = {
    "create_department": create_department,
    "get_department": get_department,
    "update_department": update_department,
    "delete_department": delete_department,
    "create_staff": create_staff,
    "get_staff": get_staff,
    "update_staff": update_staff,
    "delete_staff": delete_staff,
    "ai_scheduler": ai_scheduler,
    "get_schedule": get_schedule,
    "ai_update_scheduler": ai_update_scheduler,
    "delete_schedule": delete_schedule,
}


# if __name__ == "__main__":
async def ai_chat(input_list: list, user: User):
    "Converse with AI to perform functions"

    resp = await call_openai(input_list)

    while True:
        input_list.extend(resp.output)
        tool_called = False

        for item in resp.output:
            if item.type == "function_call":
                tool_called = True

                try:
                    function = tool_functions[item.name]
                    arguments = json.loads(item.arguments or "{}")
                    arguments["user"] = user

                    result = function(**arguments)
                except Exception as e:
                    print(f"tool {item.name} failed: {e!r}")
                    result = {"error": "Unexpected system error"}

                if hasattr(result, "model_dump"):
                    result = result.model_dump()

                input_list.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result, default=str),
                    }
                )
            else:
                if item.type == "message":
                    for content in item.content:
                        if content.type == "refusal":
                            print("The model refused:", content.refusal)

        if not tool_called:
            return resp.output_text
        resp = await call_openai(input_list)
