from models import *
from datetime import date, timedelta
from sqlmodel import select, Session
from db import engine
from app import scheduler, print_schedule
from classes import StaffData, DepartmentData


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


def get_week(db):
    # pass the db as argument

    # with Session(engine) as db:
    statement = (
        select(ScheduleWeek)
        # .where(ScheduleWeek.complete == False)
        .order_by(ScheduleWeek.week_start.desc())
    )

    latest_week = db.exec(statement).first()
    today = date.today()
    current_week_start = today - timedelta(days=today.weekday())
    current_week_end = current_week_start + timedelta(days=6)

    # No week in db
    if not latest_week:
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(6)

        week = ScheduleWeek(week_start=week_start, week_end=week_end)
        db.add(week)
        db.commit()
        db.refresh(week)

        return week

    # latest week is in past
    if latest_week.week_start < current_week_start:

        new_week = ScheduleWeek(
            week_start=current_week_start,
            week_end=current_week_end,
        )

        db.add(new_week)
        db.commit()
        db.refresh(new_week)

        return new_week

    # current week schedule not done
    if not latest_week.complete:
        return latest_week

    # current week complete
    next_start = latest_week.week_start + timedelta(days=7)
    next_end = next_start + timedelta(days=6)

    new_week = ScheduleWeek(
        week_start=next_start,
        week_end=next_end,
    )

    db.add(new_week)
    db.commit()
    db.refresh(new_week)

    return new_week


def initialize():
    with Session(engine) as db:
        staff_list = db.exec(select(Staff)).all()
        # print(staff_list)
        for staff in staff_list:
            shift_exclusions = []
            day_exclusions = []
            if staff.exclusions:
                for exclusion in staff.exclusions:
                    if exclusion.type == "shift":
                        shift_exclusions.append(exclusion.value)
                    elif exclusion.type == "day":
                        day_exclusions.append(exclusion.value)
            _ = StaffData(
                staff.first_name,
                staff.id,
                staff.position,
                shift_exclusions,
                day_exclusions,
                staff.contract_hours,
            )

        staff_list = StaffData.list_staff_members()

        department_statement = db.exec(select(Department)).all()
        for department in department_statement:
            _ = DepartmentData(
                department_name=department.name,
                min_num_staff=department.min_staff,
                max_num_staff=department.max_staff,
            )

        department_list = DepartmentData.list_departments()

        return staff_list, department_list


def create_schedule():
    with Session(engine) as db:
        current_week = get_week(db)

        staff_list, department_list = initialize()
        # print(staff_list, department_list)
        # print('')
        res = scheduler(department_list, staff_list, use_id=False)

        if res:
            staff_map = {
                staff.first_name: staff for staff in db.exec(select(Staff)).all()
            }
            department_map = {
                department.name: department
                for department in db.exec(select(Department)).all()
            }
            
            # print(staff_map.keys())
            # print('')
            # print('-'*30)
            for day in res:
                week_date = get_date_from_week(current_week.week_start, day)
                for department_name in res[day]:
                    dept = department_map[department_name]
                    for shift in res[day][department_name]:
                        for staff_id in res[day][department_name][shift]:
                            staff = staff_map[staff_id]
                            schedule = Schedule(
                                week=current_week,
                                department=dept,
                                week_date=week_date,
                                week_day=day,
                                staff=staff,
                                time=shift,
                            )
                            db.add(schedule)

            current_week.complete = True

            db.commit()
            db.refresh(current_week)

            return res

    return None


# week = get_week()
if __name__ == '__main':
    res = create_schedule()
    print_schedule(res)
