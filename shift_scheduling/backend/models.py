from sqlmodel import Field, Relationship, SQLModel
from enum import Enum
from datetime import date, datetime
from pydantic import EmailStr, ConfigDict, model_validator
from structures import ExclusionType
from sqlalchemy import UniqueConstraint, Column, JSON, Text

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

    # Staff portal account. password stays None until the staff member creates
    # one (has_account below). The invite columns belong to the invite-link
    # flow, which is disabled while staff emails are placeholders.
    password: str | None = Field(default=None, nullable=True)
    invite_token_hash: str | None = Field(default=None, nullable=True, index=True)
    invite_expires_at: datetime | None = Field(default=None, nullable=True)

    exclusions: list["Exclusion"] = Relationship(back_populates="staff")
    schedules: list["Schedule"] = Relationship(back_populates="staff")

    weekly_hours_worked: list["StaffWeeklyHours"] = Relationship(back_populates="staff")

    creator: User = Relationship(back_populates="staff")

    @property
    def has_account(self) -> bool:
        return self.password is not None


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


class AvailabilityRequest(SQLModel, table=True):
    """
    A staff member asking to change their availability. Holds the full requested
    state (not a diff); at most one is pending per staff member.
    """

    id: int | None = Field(primary_key=True, default=None)
    staff_id: int = Field(foreign_key="staff.id", index=True)
    # The admin who owns the staff member, and so reviews the request
    creator_id: int = Field(foreign_key="user.id", index=True)

    day_exclusions: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    shift_exclusions: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    note: str | None = Field(default=None, sa_column=Column(Text, nullable=True))

    status: str = Field(default="pending", index=True)  # pending | approved | rejected | cancelled
    admin_note: str | None = Field(default=None, sa_column=Column(Text, nullable=True))

    created_at: datetime = Field(default_factory=datetime.now)
    reviewed_at: datetime | None = Field(default=None, nullable=True)

    staff: Staff = Relationship()


class Notification(SQLModel, table=True):
    "An in-app notification for exactly one recipient: an admin (user) or a staff member"

    id: int | None = Field(primary_key=True, default=None)
    recipient_user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    recipient_staff_id: int | None = Field(default=None, foreign_key="staff.id", index=True)

    kind: str
    message: str = Field(sa_column=Column(Text, nullable=False))
    request_id: int | None = Field(default=None, foreign_key="availabilityrequest.id")

    read_at: datetime | None = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.now)


class AiChat(SQLModel, table=True):
    """
    One finished AskAI conversation, saved once when its WebSocket closes. The
    counts are denormalised so insights (busy users, flaky tools) are cheap.
    """

    id: int | None = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id", index=True)

    started_at: datetime
    ended_at: datetime

    message_count: int = Field(default=0)  # user + assistant messages
    tool_call_count: int = Field(default=0)
    error_count: int = Field(default=0)  # failed tool calls and failed replies

    messages: list["AiChatMessage"] = Relationship(back_populates="chat")


class AiChatMessage(SQLModel, table=True):
    "One entry in a saved chat: a user message, an assistant reply, a tool call, or an error"

    id: int | None = Field(primary_key=True, default=None)
    chat_id: int = Field(foreign_key="aichat.id", index=True)
    position: int  # order within the chat

    role: str  # user | assistant | tool | error
    content: str = Field(sa_column=Column(Text, nullable=False))

    # Tool calls only: what the model asked for, and whether it came back as an error
    tool_name: str | None = Field(default=None, nullable=True, index=True)
    tool_arguments: dict | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    is_error: bool = Field(default=False)

    created_at: datetime

    chat: AiChat = Relationship(back_populates="messages")
