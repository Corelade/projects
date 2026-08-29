from models import *
from datetime import date, timedelta
from sqlmodel import select, Session
from db import engine
from app import scheduler, print_schedule, update_schedule, get_assignment_staff
from classes import StaffData, DepartmentData
from collections import defaultdict, Counter
from sqlalchemy.orm import selectinload, with_loader_criteria


def week_str_to_object(week_start: str):
    week_date_object = datetime.strptime(week_start, "%Y-%m-%d")
    return week_date_object


def get_date_from_week(week_start: date, day: str) -> date:
    days_map = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    return week_start + timedelta(days=days_map[day.lower()])


def save_schedule(*, res, current_week, db):
    '''This function saves a schedule to the database'''
    staff_map = {staff.id: staff for staff in db.exec(select(Staff)).all()}
    department_map = {
        department.id: department
        for department in db.exec(select(Department)).all()
    }
    
    for day in res:
        week_date = get_date_from_week(current_week.week_start, day)
        for dept in res[day]:
            for shift in res[day][dept]:
                for stf in res[day][dept][shift]:
                    existing = db.exec(
                        select(Schedule).where(
                            Schedule.week_id == current_week.id,
                            Schedule.week_date == week_date,
                            Schedule.week_day == day,
                            Schedule.time == shift,
                            Schedule.department_id == dept.id,
                            Schedule.staff_id == stf.id,
                        )
                    ).first()
                    if not existing:
                        schedule = Schedule(
                            week=current_week,
                            week_date=week_date,
                            week_day=day,
                            time=shift,
                            department=department_map[dept.id],
                            staff=staff_map[stf.id],
                        )

                        db.add(schedule)
    
    db.commit()


def get_week(week_start: str, db):
    with Session(engine) as db:
        week_statement = select(ScheduleWeek).where(
            ScheduleWeek.week_start == week_start
        )
        week = db.exec(week_statement).first()

        if not week:
            week_end = week_str_to_object(week_start) + timedelta(days=6)
            week = ScheduleWeek(week_start=week_start, week_end=week_end)
            db.add(week)
            db.commit()
            db.refresh(week)

        return week


def initialize(current_week):
    """This function is to convert department and staff from database to class instances of DepartmentData/StaffData"""

    StaffData.reset()
    DepartmentData.reset()

    with Session(engine) as db:
        # if include_deleted:
        statement = select(Staff).options(
            selectinload(Staff.weekly_hours_worked),
            with_loader_criteria(
                StaffWeeklyHours,
                StaffWeeklyHours.week_id == current_week.id,
            ),
        )
        # else:
        #     statement = (
        #         select(Staff)
        #         .filter(Staff.deleted == False)
        #         .options(
        #             selectinload(Staff.weekly_hours_worked),
        #             with_loader_criteria(
        #                 StaffWeeklyHours,
        #                 StaffWeeklyHours.week_id == current_week.id,
        #             ),
        #         )
        #     )

        staff_list = db.exec(statement).all()

        for staff in staff_list:
            shift_exclusions = []
            day_exclusions = []
            if staff.exclusions:
                for exclusion in staff.exclusions:
                    if exclusion.type == "shift":
                        shift_exclusions.append(exclusion.value)
                    elif exclusion.type == "day":
                        day_exclusions.append(exclusion.value)
            sd = StaffData(
                staff.first_name,
                staff.position,
                shift_exclusions,
                day_exclusions,
                staff.contract_hours,
                staff.min_hours,
                staff.id,
                unavailable=staff.deleted,
            )

            sd.hours_worked = (
                staff.weekly_hours_worked[0].hours if staff.weekly_hours_worked else 0
            )
            # print(sd, sd.hours_worked)

        # return None

        staff_list = StaffData.list_staff_members()

        department_statement = db.exec(
            select(Department).filter(Department.deleted == False)
        ).all()
        for department in department_statement:
            _ = DepartmentData(
                name=department.name,
                min_staff=department.min_staff,
                max_staff=department.max_staff,
                id=department.id,
            )

        department_list = DepartmentData.list_departments()
        # print(staff_list, department_list)

        return staff_list, department_list


def create_schedule(week_start, db):
    """This function uses the StaffData/DepartmentData to create a schedule"""

    # TODO instead of using class instances, just use model obects

    # with Session(engine) as db:
    current_week = get_week(week_start, db)

    staff_list, department_list = initialize(current_week)

    if not current_week.complete:
        res = scheduler(department_list, staff_list)
    else:
        _, _, schedule_res = get_week_schedule(
            week_start=week_start, db=db, regenerate=True
        )
        available_staff_list = [st for st in staff_list if not st.unavailable]
        updated_res = update_schedule(
            schedule_res, department_list, available_staff_list
        )
        if not updated_res["regenerated"]:
            return None
        res = updated_res["result"]

    assigned_staff_dict = Counter(get_assignment_staff(res, unique=False))
    # print(assigned_staff_dict)

    whs = db.exec(
        select(StaffWeeklyHours)
        .where(StaffWeeklyHours.week_id == current_week.id)
        .options(selectinload(StaffWeeklyHours.staff))
    ).all()

    wh_map = {wh.staff_id: wh for wh in whs}

    for stf, shifts_worked in assigned_staff_dict.items():
        weekly_hours = wh_map.get(stf.id)

        if weekly_hours:
            weekly_hours.hours = 4 * shifts_worked
        else:
            weekly_hours = StaffWeeklyHours(
                staff_id=stf.id,
                week_id=current_week.id,
                hours=4 * shifts_worked,
            )
            # print(f'wh created for {stf.name}')
            db.add(weekly_hours)
            wh_map[stf.id] = weekly_hours

    whs = db.exec(
        select(StaffWeeklyHours)
        .where(StaffWeeklyHours.week_id == current_week.id)
        .options(selectinload(StaffWeeklyHours.staff))
    ).all()
    assigned_staff_ids = {stf.id for stf in assigned_staff_dict}

    for wh in whs:
        if wh.staff_id not in assigned_staff_ids:
            wh.hours = 0
        # print(wh.staff.first_name, wh.hours)

    for staff in staff_list:
        if staff.unavailable:
            # print(staff, staff.id)
            staff_scheds = db.exec(
                select(Schedule).where(
                    Schedule.week_id == current_week.id,
                    Schedule.staff_id == staff.id,
                )
            ).all()
            for staff_sched in staff_scheds:
                # print(f'deleting {staff.name}: {staff_sched.id} -> {staff_sched}')
                db.delete(staff_sched)

    if res:
        save_schedule(res=res, current_week=current_week, db=db)

        current_week.complete = True

        db.commit()
        db.refresh(current_week)

        return res

    return None


def get_week_schedule(*, db, week_start: str, regenerate: bool = False):
    """This function is to get the json format of a week's schedule. Consumed by api"""
    # def get_week_schedule(week_start: str, db=None, regenerate: bool = False):
    schedule_res = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    # with Session(engine) as db:
    schedule_statement = (
        select(Schedule)
        .join(ScheduleWeek)
        # .join(StaffWeeklyHours)
        .where(ScheduleWeek.week_start == week_start)
        .options(
            selectinload(Schedule.staff),
            selectinload(Schedule.department),
            selectinload(Schedule.week).selectinload(
                ScheduleWeek.staff_weekly_hours_worked
            ),
        )
    )

    schedule_list: list[Schedule] = db.exec(schedule_statement).all()
    week_end, generated_at, schedule = "", "", {}

    if schedule_list:
        week_end, generated_at = (
            schedule_list[0].week.week_end,
            schedule_list[0].week.generated_at,
        )

        for schedule in schedule_list:
            day = schedule.week_day
            shift = schedule.time
            staff_obj = schedule.staff
            staff_name = f"{staff_obj.first_name} {staff_obj.last_name}"
            dept = (
                schedule.department_id if not regenerate else schedule.department.name
            )
            staff_id = staff_obj.id
            dept_obj = schedule.department

            if not regenerate:
                schedule_res[day][dept][shift].append(
                    {"staff_id": staff_id, "staff_name": staff_name}
                )
            else:
                current_week = get_week(week_start, db)
                staff_list, department_list = initialize(current_week)

                staff_instance_list = [st for st in staff_list if st.id == staff_obj.id]
                # if staff_instance_list:
                staff_instance = staff_instance_list[0]

                # staff_instance = None
                department_instance = [
                    dept for dept in department_list if dept.id == dept_obj.id
                ][0]
                schedule_res[day][department_instance][shift].append(staff_instance)

    return week_end, generated_at, schedule_res


# if __name__ == "__main__":
#     res = create_schedule()
#     if res:
#         print_schedule(res)
