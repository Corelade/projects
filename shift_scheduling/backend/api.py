from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Query,
    status,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from contextlib import asynccontextmanager
from db import SessionDep, create_db_and_tables, engine
from models import *
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from classes import StaffData
from utils import *
from structures import *
import logging, json, datetime, os, re
from structs.auth_struct import (
    AuthResponse,
    AuthUser,
    Credentials,
    Token,
    PortalCredentials,
    EmailRequest,
    PasswordRequest,
    AccountStatusResponse,
    # InviteSetup,
    # InviteResponse,
)
from auth.auth import (
    get_password_hash,
    get_user,
    verify_password,
    create_access_token,
    create_staff_access_token,
    # hash_invite_token,
    # new_invite_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    UserQuery,
    PortalQuery,
    PortalViewer,
    user_from_token,
)
from ai import ai_chat

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


def validate_password(password: str):
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


def admin_auth_response(user: User):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"user": user.username}, access_token_expires)
    return {
        "token": access_token,
        "user": {"id": user.id, "username": user.username, "role": "admin"},
    }


def staff_auth_response(staff: Staff):
    return {
        "token": create_staff_access_token(staff),
        "user": {
            "id": staff.id,
            "username": f"{staff.first_name} {staff.last_name}",
            "role": "staff",
        },
    }


@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(data: Credentials, db: SessionDep):
    username = data.username
    password = data.password

    USERNAME_PATTERN = r"^[a-zA-Z][a-zA-Z0-9._-]*$"

    validate_password(password)

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

    return admin_auth_response(user)


@app.post("/auth/refresh", response_model=AuthResponse)
def refresh_token(viewer: PortalQuery):
    "Swap a still-valid token (admin or staff) for a fresh one, so an active session doesn't expire"
    if viewer.staff:
        return staff_auth_response(viewer.staff)
    return admin_auth_response(viewer.user)


# ---------------------------------------------------------------------------
# Staff portal
# ---------------------------------------------------------------------------

# Invite links: for a real deployment where staff have working emails. Disabled
# while staff emails are placeholders; staff use /portal/create-password instead.
# INVALID_INVITE = "This invite link is invalid or has expired. Ask your manager for a new one."


# def staff_from_invite(token: str, db) -> Staff:
#     staff = db.exec(
#         select(Staff).where(Staff.invite_token_hash == hash_invite_token(token))
#     ).first()

#     if (
#         not staff
#         or staff.deleted
#         or staff.invite_expires_at is None
#         or staff.invite_expires_at < datetime.datetime.now()
#     ):
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=INVALID_INVITE)

#     return staff


def portal_staff(viewer: PortalViewer, staff_id: int | None, db) -> Staff:
    "The staff member whose portal is being viewed. Staff only see themselves"
    if viewer.staff:
        if staff_id is not None and staff_id != viewer.staff.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own schedule",
            )
        return viewer.staff

    if staff_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Choose a staff member to view",
        )

    staff = db.get(Staff, staff_id)
    if not staff or staff.deleted or staff.creator_id != viewer.user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")

    return staff


@app.post("/portal/login", response_model=AuthResponse)
def portal_login(data: PortalCredentials, db: SessionDep):
    "Staff-only sign in, by email. Admins sign in at /auth/login"
    staff = db.exec(
        select(Staff).where(Staff.email == data.email.strip(), Staff.deleted == False)
    ).first()

    if staff and staff.password is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You haven't created a password yet. Use Create password first.",
        )

    if not staff or not verify_password(data.password, staff.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    return staff_auth_response(staff)


# Invite links: for a real deployment where staff have working emails. Disabled
# while staff emails are placeholders; staff use /portal/create-password instead.
# @app.get("/portal/invite")
# def get_invite(token: str, db: SessionDep):
#     "Who an invite link is for, so the setup page can greet them"
#     staff = staff_from_invite(token, db)
#     return {
#         "first_name": staff.first_name,
#         "last_name": staff.last_name,
#         "email": staff.email,
#     }


# @app.post("/portal/setup", response_model=AuthResponse)
# def setup_account(data: InviteSetup, db: SessionDep):
#     "Staff create (or reset) their password from an invite link, and are signed in"
#     staff = staff_from_invite(data.token, db)
#     validate_password(data.password)

#     staff.password = get_password_hash(data.password)
#     staff.invite_token_hash = None
#     staff.invite_expires_at = None
#     db.commit()
#     db.refresh(staff)

#     return staff_auth_response(staff)


def active_staff_by_email(email: str, db) -> Staff:
    staff = db.exec(
        select(Staff).where(Staff.email == email.strip(), Staff.deleted == False)
    ).first()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No staff member has that email. Check it with your manager.",
        )
    return staff


# NOTE: without real, verified emails nothing proves the person typing an email
# is that staff member. Fine while emails are placeholders; for a real
# deployment, put email verification (or the invite links above) back in front
# of create-password and reset-password.


@app.post("/portal/account-status", response_model=AccountStatusResponse)
def account_status(data: EmailRequest, db: SessionDep):
    "Whether this staff email already has a password, so the UI knows to create or sign in"
    staff = active_staff_by_email(data.email, db)
    return {"has_account": staff.has_account}


@app.post("/portal/create-password", response_model=AuthResponse)
def create_password(data: PasswordRequest, db: SessionDep):
    "First-time set-up: staff without a password create one, and are signed in"
    staff = active_staff_by_email(data.email, db)

    if staff.has_account:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have a password. Sign in, or use Forgot password to set a new one.",
        )

    validate_password(data.password)
    staff.password = get_password_hash(data.password)
    db.commit()
    db.refresh(staff)

    return staff_auth_response(staff)


@app.post("/portal/reset-password", response_model=AuthResponse)
def reset_password(data: PasswordRequest, db: SessionDep):
    "Forgot password: staff who already have a password set a new one, and are signed in"
    staff = active_staff_by_email(data.email, db)

    if not staff.has_account:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You haven't created a password yet. Use Create password instead.",
        )

    validate_password(data.password)
    staff.password = get_password_hash(data.password)
    db.commit()
    db.refresh(staff)

    return staff_auth_response(staff)


@app.get("/portal/me", response_model=PortalProfileResponse)
def portal_profile(db: SessionDep, viewer: PortalQuery, staff_id: int | None = None):
    staff = portal_staff(viewer, staff_id, db)

    return {
        "id": staff.id,
        "first_name": staff.first_name,
        "last_name": staff.last_name,
        "email": staff.email,
        "position": staff.position,
        "contract_hours": staff.contract_hours,
        "min_hours": staff.min_hours,
        "day_exclusions": [
            e.value for e in staff.exclusions if e.type == ExclusionType.day
        ],
        "shift_exclusions": [
            e.value for e in staff.exclusions if e.type == ExclusionType.shift
        ],
        "has_account": staff.has_account,
    }


@app.get("/portal/schedule", response_model=PortalWeekResponse)
def portal_schedule(
    week_start: str, db: SessionDep, viewer: PortalQuery, staff_id: int | None = None
):
    staff = portal_staff(viewer, staff_id, db)

    try:
        start = datetime.datetime.strptime(week_start, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="week_start must be a date in YYYY-MM-DD format",
        )

    week = db.exec(
        select(ScheduleWeek).where(
            ScheduleWeek.week_start == start,
            ScheduleWeek.creator_id == staff.creator_id,
        )
    ).first()

    rows = []
    if week:
        rows = db.exec(
            select(Schedule)
            .where(Schedule.week_id == week.id, Schedule.staff_id == staff.id)
            .options(selectinload(Schedule.department))
        ).all()

    shift_order = {"morning": 0, "afternoon": 1, "evening": 2}
    rows = sorted(rows, key=lambda r: (r.week_date, shift_order.get(r.time, 3)))

    return {
        "week_start": start,
        "week_end": start + timedelta(days=6),
        "published": bool(week and week.complete),
        "hours": 4 * len(rows),
        "shifts": [
            {
                "date": row.week_date,
                "day": row.week_day,
                "shift": row.time,
                "department_id": row.department_id,
                "department_name": row.department.name,
            }
            for row in rows
        ],
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

    availability_changed = set_staff_exclusions(
        db,
        staff_instance,
        days=(
            data.day_exclusions or []
            if "day_exclusions" in data.model_fields_set
            else None
        ),
        shifts=(
            data.shift_exclusions or []
            if "shift_exclusions" in data.model_fields_set
            else None
        ),
    )

    if availability_changed:
        notify(
            db,
            staff_id=staff_instance.id,
            kind="availability_updated",
            message="Your manager updated your availability.",
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


# Invite links: for a real deployment where staff have working emails. Disabled
# while staff emails are placeholders; staff use /portal/create-password instead.
# @app.post("/staff/{id}/invite", response_model=InviteResponse)
# def invite_staff(id: int, db: SessionDep, user: UserQuery):
#     """
#     A one-time link for the staff member to set their password. Issuing a new
#     one replaces the old, and doubles as a password reset for an active account.
#     """
#     staff = db.get(Staff, id)

#     if not staff or staff.deleted or staff.creator_id != user.id:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")

#     token, token_hash, expires_at = new_invite_token()
#     staff.invite_token_hash = token_hash
#     staff.invite_expires_at = expires_at
#     db.commit()

#     return {"token": token, "expires_at": expires_at.isoformat()}


# ---------------------------------------------------------------------------
# Availability requests and notifications
# ---------------------------------------------------------------------------

REQUEST_KINDS = ("pending", "approved", "rejected", "cancelled")


def staff_only(viewer: PortalViewer) -> Staff:
    "Requests are the staff member's own; an admin viewing the portal can't make them"
    if not viewer.staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can do this. Change availability from the Staff page.",
        )
    return viewer.staff


def full_name(staff: Staff) -> str:
    return f"{staff.first_name} {staff.last_name}"


def request_json(request: AvailabilityRequest) -> dict:
    current_days, current_shifts = staff_exclusions(request.staff)
    return {
        "id": request.id,
        "staff_id": request.staff_id,
        "staff_name": full_name(request.staff),
        "status": request.status,
        "day_exclusions": request.day_exclusions,
        "shift_exclusions": request.shift_exclusions,
        "current_day_exclusions": current_days,
        "current_shift_exclusions": current_shifts,
        "note": request.note,
        "admin_note": request.admin_note,
        "created_at": request.created_at,
        "reviewed_at": request.reviewed_at,
    }


def validate_availability(staff: Staff, days: list[str], shifts: list[str]):
    try:
        check_staff_hours(
            staff.first_name, staff.contract_hours, staff.min_hours, shifts, days
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


def notification_list(db, *, user_id: int | None = None, staff_id: int | None = None):
    "Latest 20 notifications for one recipient, plus their total unread count"
    recipient = (
        Notification.recipient_user_id == user_id
        if user_id is not None
        else Notification.recipient_staff_id == staff_id
    )
    items = db.exec(
        select(Notification)
        .where(recipient)
        .order_by(Notification.created_at.desc(), Notification.id.desc())
        .limit(20)
    ).all()
    unread = len(
        db.exec(select(Notification.id).where(recipient, Notification.read_at == None)).all()
    )
    return {
        "unread": unread,
        "items": [
            {
                "id": n.id,
                "kind": n.kind,
                "message": n.message,
                "request_id": n.request_id,
                "read": n.read_at is not None,
                "created_at": n.created_at,
            }
            for n in items
        ],
    }


def mark_read(db, ids: list[int] | None, *, user_id=None, staff_id=None):
    recipient = (
        Notification.recipient_user_id == user_id
        if user_id is not None
        else Notification.recipient_staff_id == staff_id
    )
    statement = select(Notification).where(recipient, Notification.read_at == None)
    if ids is not None:
        statement = statement.where(Notification.id.in_(ids))

    now = datetime.datetime.now()
    for n in db.exec(statement).all():
        n.read_at = now
    db.commit()


# --- staff side


@app.get(
    "/portal/availability-requests", response_model=list[AvailabilityRequestResponse]
)
def my_availability_requests(db: SessionDep, viewer: PortalQuery):
    staff = staff_only(viewer)
    requests = db.exec(
        select(AvailabilityRequest)
        .where(AvailabilityRequest.staff_id == staff.id)
        .order_by(AvailabilityRequest.created_at.desc(), AvailabilityRequest.id.desc())
        .limit(20)
    ).all()
    return [request_json(r) for r in requests]


@app.post(
    "/portal/availability-requests",
    response_model=AvailabilityRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def request_availability_change(
    data: AvailabilityRequestCreate, db: SessionDep, viewer: PortalQuery
):
    "Create a request, or replace the pending one. The admin is notified"
    staff = staff_only(viewer)
    days = list(dict.fromkeys(data.day_exclusions))
    shifts = list(dict.fromkeys(data.shift_exclusions))

    current_days, current_shifts = staff_exclusions(staff)
    if sorted(days) == sorted(current_days) and sorted(shifts) == sorted(current_shifts):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That's already your availability.",
        )

    validate_availability(staff, days, shifts)

    request = db.exec(
        select(AvailabilityRequest).where(
            AvailabilityRequest.staff_id == staff.id,
            AvailabilityRequest.status == "pending",
        )
    ).first()
    replacing = request is not None

    if request is None:
        request = AvailabilityRequest(staff_id=staff.id, creator_id=staff.creator_id)
        db.add(request)

    request.day_exclusions = days
    request.shift_exclusions = shifts
    request.note = (data.note or "").strip() or None
    request.created_at = datetime.datetime.now()
    db.flush()

    notify(
        db,
        user_id=staff.creator_id,
        kind="availability_requested",
        message=(
            f"{full_name(staff)} updated their availability request."
            if replacing
            else f"{full_name(staff)} requested an availability change."
        ),
        request_id=request.id,
    )
    db.commit()
    db.refresh(request)

    return request_json(request)


@app.post(
    "/portal/availability-requests/{id}/cancel",
    response_model=AvailabilityRequestResponse,
)
def cancel_availability_request(id: int, db: SessionDep, viewer: PortalQuery):
    staff = staff_only(viewer)
    request = db.get(AvailabilityRequest, id)

    if not request or request.staff_id != staff.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    if request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only a pending request can be cancelled.",
        )

    request.status = "cancelled"
    request.reviewed_at = datetime.datetime.now()
    db.commit()
    db.refresh(request)

    return request_json(request)


@app.get("/portal/notifications", response_model=NotificationListResponse)
def my_notifications(db: SessionDep, viewer: PortalQuery):
    return notification_list(db, staff_id=staff_only(viewer).id)


@app.post("/portal/notifications/read", status_code=status.HTTP_204_NO_CONTENT)
def read_my_notifications(data: MarkReadRequest, db: SessionDep, viewer: PortalQuery):
    mark_read(db, data.ids, staff_id=staff_only(viewer).id)


# --- admin side


def admin_request(id: int, db, user: User) -> AvailabilityRequest:
    "A pending request for one of this admin's (non-deleted) staff"
    request = db.get(AvailabilityRequest, id)

    if not request or request.creator_id != user.id or request.staff.deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    if request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"This request has already been {request.status}.",
        )

    return request


@app.get("/availability-requests", response_model=list[AvailabilityRequestResponse])
def list_availability_requests(
    db: SessionDep, user: UserQuery, status_filter: str | None = Query(None, alias="status")
):
    statement = (
        select(AvailabilityRequest)
        .join(Staff)
        .where(AvailabilityRequest.creator_id == user.id, Staff.deleted == False)
        .order_by(AvailabilityRequest.created_at.desc(), AvailabilityRequest.id.desc())
        .limit(100)
    )
    if status_filter:
        if status_filter not in REQUEST_KINDS:
            raise HTTPException(status_code=400, detail="Unknown status")
        statement = statement.where(AvailabilityRequest.status == status_filter)

    return [request_json(r) for r in db.exec(statement).all()]


@app.post(
    "/availability-requests/{id}/approve", response_model=AvailabilityRequestResponse
)
def approve_availability_request(
    id: int, data: AvailabilityApprove, db: SessionDep, user: UserQuery
):
    "Apply the request, or the admin's adjusted version of it, and notify the staff member"
    request = admin_request(id, db, user)
    staff = request.staff

    days = list(
        dict.fromkeys(
            data.day_exclusions
            if data.day_exclusions is not None
            else request.day_exclusions
        )
    )
    shifts = list(
        dict.fromkeys(
            data.shift_exclusions
            if data.shift_exclusions is not None
            else request.shift_exclusions
        )
    )
    adjusted = sorted(days) != sorted(request.day_exclusions) or sorted(shifts) != sorted(
        request.shift_exclusions
    )

    validate_availability(staff, days, shifts)
    set_staff_exclusions(db, staff, days, shifts)

    request.status = "approved"
    request.admin_note = (data.admin_note or "").strip() or None
    request.reviewed_at = datetime.datetime.now()

    message = (
        "Your availability change was approved with some changes by your manager."
        if adjusted
        else "Your availability change was approved."
    )
    if request.admin_note:
        message += f" Note: {request.admin_note}"
    notify(
        db,
        staff_id=staff.id,
        kind="availability_approved",
        message=message,
        request_id=request.id,
    )

    db.commit()
    db.refresh(request)

    return request_json(request)


@app.post(
    "/availability-requests/{id}/reject", response_model=AvailabilityRequestResponse
)
def reject_availability_request(
    id: int, data: AvailabilityReject, db: SessionDep, user: UserQuery
):
    request = admin_request(id, db, user)

    request.status = "rejected"
    request.admin_note = (data.admin_note or "").strip() or None
    request.reviewed_at = datetime.datetime.now()

    message = "Your availability change was declined."
    if request.admin_note:
        message += f" Reason: {request.admin_note}"
    notify(
        db,
        staff_id=request.staff_id,
        kind="availability_rejected",
        message=message,
        request_id=request.id,
    )

    db.commit()
    db.refresh(request)

    return request_json(request)


@app.get("/notifications", response_model=NotificationListResponse)
def admin_notifications(db: SessionDep, user: UserQuery):
    return notification_list(db, user_id=user.id)


@app.post("/notifications/read", status_code=status.HTTP_204_NO_CONTENT)
def read_admin_notifications(data: MarkReadRequest, db: SessionDep, user: UserQuery):
    mark_read(db, data.ids, user_id=user.id)


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


class ChatTranscript:
    "An AskAI chat collected in memory while its socket is open, saved once at the end"

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.started_at = datetime.datetime.now()
        self.entries: list[dict] = []

    def add(self, role: str, content: str, *, is_error: bool = False, **tool):
        self.entries.append(
            {
                "role": role,
                "content": content or "",
                "is_error": is_error,
                "created_at": datetime.datetime.now(),
                **tool,
            }
        )

    def add_tools(self, trace: list[dict]):
        for call in trace:
            try:
                output = json.loads(call["output"])
                # Some tools return an already-JSON string; look one level in
                if isinstance(output, str):
                    output = json.loads(output)
            except (TypeError, ValueError):
                output = None
            failed = isinstance(output, dict) and "error" in output
            self.add(
                "tool",
                call["output"][:4000],
                is_error=failed,
                tool_name=call["name"],
                tool_arguments=call["arguments"],
            )

    def save(self):
        "Nothing is saved for a chat where the user never said anything"
        if not any(e["role"] == "user" for e in self.entries):
            return
        try:
            with Session(engine) as db:
                chat = AiChat(
                    user_id=self.user_id,
                    started_at=self.started_at,
                    ended_at=datetime.datetime.now(),
                    message_count=sum(e["role"] in ("user", "assistant") for e in self.entries),
                    tool_call_count=sum(e["role"] == "tool" for e in self.entries),
                    error_count=sum(e["is_error"] for e in self.entries),
                )
                chat.messages = [
                    AiChatMessage(position=i, **entry)
                    for i, entry in enumerate(self.entries)
                ]
                db.add(chat)
                db.commit()
        except Exception as e:
            # Losing a transcript must never surface as a chat error
            print(f"could not save AI chat: {e!r}")


@app.websocket("/chat_ws")
async def chat_endpoint(websocket: WebSocket):
    # Browsers can't set headers on a WebSocket, so the JWT comes as ?token=.
    # A short session: don't hold a DB connection for the socket's lifetime.
    token = websocket.query_params.get("token")
    with Session(engine) as db:
        user = user_from_token(token, db) if token else None

    # Accept before closing so the client sees 4401, not a bare 1006.
    await websocket.accept()
    if user is None:
        await websocket.close(code=4401, reason="Unauthorized")
        return

    # The chat lives as long as this socket (the client doesn't persist it), so
    # it's kept in memory here and saved once, when the socket closes.
    transcript = ChatTranscript(user.id)

    try:
        while True:
            message = await websocket.receive_json()
            # The client sends {id, role: user|ai|error, text}; OpenAI wants
            # {role: user|assistant, content}. Error bubbles aren't conversation.
            input_list = [
                {
                    "role": "assistant" if item["role"] == "ai" else "user",
                    "content": item["text"],
                }
                for item in message.get("input_list", [])
                if item.get("role") in ("user", "ai")
            ]
            user_text = message.get("current_message") or next(
                (i["content"] for i in reversed(input_list) if i["role"] == "user"), ""
            )
            transcript.add("user", user_text)

            trace = []
            try:
                ai_response = await ai_chat(input_list=input_list, user=user, trace=trace)
                transcript.add_tools(trace)
                transcript.add("assistant", ai_response)
                await websocket.send_json({"message": ai_response})
            except WebSocketDisconnect:
                raise
            except Exception as e:
                # print(f"chat error: {e!r}")
                # await websocket.send_json(
                #     {"error": "Something went wrong. Please try again."}
                # )
                transcript.add_tools(trace)
                transcript.add("error", repr(e)[:1000], is_error=True)
                input_list.append(
                    {
                        "role": "assistant",
                        "error": "Something went wrong. Please try again.",
                    }
                )
                trace = []
                ai_response = await ai_chat(input_list=input_list, user=user, trace=trace)
                transcript.add_tools(trace)
                transcript.add("assistant", ai_response)
                await websocket.send_json({"message": ai_response})
    except WebSocketDisconnect:
        pass
    finally:
        # Any way the chat ends — tab closed, reload, sign out, or a failure above.
        transcript.save()
