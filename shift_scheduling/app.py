from classes import DepartmentData, StaffData
import copy
import random
from collections import defaultdict
import json
from itertools import zip_longest
from typing import Literal

shift_time = ["morning", "afternoon", "evening"]
DAY_OF_WEEK = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def to_normal_dict(d):
    if isinstance(d, dict):
        result = {str(k): to_normal_dict(v) for k, v in d.items()}
        # print(json.dumps(result, indent=4))
        return result
    return d


def is_feasibile(
    depts: list[DepartmentData],
    staff_arr: list[StaffData],
    DAY_OF_WEEK=DAY_OF_WEEK,
):
    """
    This function checks if the current departments and staff available will yield a result

    1 dept -> 1 person - True
    1 dept -> 2 persons - True
    1 dept -> 3 persons - True
    1 dept -> 4 persons -> False
    2 dept [min_staff, [1, 1]] -> 7 persons -> False
    2 dept [min_staff, [1, 2]] -> 7 persons -> False
    2 dept [min_staff, [1, 2]] -> 9 persons -> True


    1 dept -> 1 person ["evening"] - False
    1 dept -> 2 person ["evening", "evening"] - False

    2 dept [min_staff, [1, 2]] -> 2 person -> False
    """

    if not depts or not staff_arr:
        print("No Departments or Staff")
        # return {
        #     'success': False,
        #     'message': message
        # }
        return False

    NUM_SHIFTS = 3
    # this gets the total number of shifts that need filling
    shifts_to_fill = 0
    # max_shifts_to_fill = 0
    for dept in depts:
        req_hours = dept.min_num_staff * NUM_SHIFTS
        shifts_to_fill += req_hours

    # check for required hours and staff hours
    "Each department is open for 12 hours a day"
    NUM_HOURS = 12
    """check for average working hour is within capacity"""
    # avail_hours = len(depts) * NUM_HOURS * len(DAY_OF_WEEK)
    required_hours = sum(
        dept.min_num_staff * NUM_HOURS * len(DAY_OF_WEEK) for dept in depts
    )
    available_capacity = sum(stf.contract_hours for stf in staff_arr)
    min_required_hours = sum(stf.min_hours for stf in staff_arr)
    # print(required_hours, available_capacity, min_available_capacity)
    if required_hours > available_capacity:
        print(
            f"Required Hours -> '{required_hours}' is more than Available Capacity -> '{available_capacity}'"
        )
        return False

    if required_hours < min_required_hours:
        print(
            f"Required Hours -> '{required_hours}' is greater than number of available hours"
        )
        return False

    for day in DAY_OF_WEEK:
        unfilled = defaultdict(int)
        # available_hours = 0
        for stf in staff_arr:

            if day in stf.day_exclusion_list:
                for tme in shift_time:
                    unfilled[tme] += 1
                continue
            for tme in shift_time:
                if tme not in stf.shift_exclusion_list:
                    # available_hours += 4
                    unfilled[tme] -= 1
                else:
                    unfilled[tme] += 1

        if max(unfilled.values()) > 0:
            # print("Unfilled present", unfilled)
            print("Not enough staff for", day)
            return False

    total_min_staff = sum(department.min_num_staff for department in depts)

    if total_min_staff > len(staff_arr):
        print(
            "Total number of required staff is greater than total number of available staff"
        )
        return False

    return True


def get_valid_staff(staff_list: list[StaffData]):
    """
    This function takes the overall staff list and returns a valid staff member for assignment
    """

    copied_staff_list = copy.deepcopy(staff_list)
    available_staff = [staff for staff in copied_staff_list if staff.is_valid()]

    if not available_staff:
        return None

    return available_staff


def get_other_staff(
    assignment: dict[str, dict[str, dict]], domain: DepartmentData, cur_day
):
    """
    Checks already assigned staff for a given day that are in other departments
    """
    assigned_staff_arr = [
        staff
        for day, val in assignment.items()
        for dept, shifts in val.items()
        if day == cur_day  # check for current day
        if dept != domain.department_name  # only other departments
        for staff_list in shifts.values()  # all shifts
        for staff in staff_list
    ]
    return assigned_staff_arr


def is_valid(
    assignment: dict,
    domain: DepartmentData,
    tme: Literal['morning', 'afternoon', 'evening'],
    staff: StaffData,
    day: str,
    use_id: bool = True,
):
    # checks to see if an assigment is valid

    """
    - One domain can not have more than its maximum capacity
    - One staff can not be in more than one department on same day
    """
    # print(f'CHECKING VALIDATION FOR "{domain}"')
    # print(dict(assignment))
    # print("Num of staff in assignment", len(assignment[domain]))
    # print("Max allowable staff", domain.max_num_staff, "\n")

    # if not staff.is_valid():
    #     print(staff, staff.hours_worked, end='\n')
    #     print(assignment)
    #     time.sleep(10)
    #     return False

    # one domain can not have more than its max_cap
    if domain.max_num_staff < len(assignment[day][domain.department_name][tme]):
        # print(
        #     f"Error -> {domain} requires {domain.max_num_staff} but got {len(assignment[domain][tme])}",
        #     "\n",
        # )
        return False

    # same staff cant be assigned to same domain more than once
    # print(
    #     assignment[domain.department_name],
    #     ":",
    #     assignment[domain.department_name][tme]
    #     "->",
    #     assignment[domain.department_name][tme].count(staff.id),
    #     "\n",
    # )
    if use_id:
        staff_count = assignment[day][domain.department_name][tme].count(staff.id)
    else:
        staff_count = assignment[day][domain.department_name][tme].count(staff.name)
    if staff_count > 1:
        # print(
        #     f"Error -> StaffData:{staff} appears {assignment[domain.department_name][tme].count(staff)} times",
        #     "\n",
        # )
        return False

    if tme in staff.shift_exclusion_list:
        return False

    # one staff can not be in more than one domain
    "exclude the current domain and check staff not in other domains"
    # other_assignment = {dom: val for dom, val in assignment.items() if dom != domain}
    # assigned_staff_arr = other_assignment.values()
    assigned_staff_arr = get_other_staff(assignment, domain, day)
    # print("ASR", assigned_staff_arr, "\n")
    # for staff_list in assigned_staff_arr:
    # print(
    #     staff.id,
    #     assigned_staff_arr,
    #     staff.id in assigned_staff_arr,
    # )
    # print(f"Assigned StaffData Array -> {assigned_staff_arr}", "\n")
    'if use_id == True'
    value = staff.id if use_id else staff.name
    if value in assigned_staff_arr:
        # print(f"Error -> {staff} already in assigned_staff_arr", "\n")
        return False

    # if staff in [staff_list for staff_list in assigned_staff_arr]:
    #     return False

    return True


seen = defaultdict(lambda: defaultdict(int))


def backtrack(
    assignment,
    departments: list[DepartmentData],
    staff: list[StaffData],
    domains,
    use_id: bool = True,
):
    # print([(st, st.hours_worked) for st in staff])
    # before running the main function, check if there is a solution
    # if not is_feasibile():
    #     return {}

    """
    check for the required number of staff is available
    """
    min_required_staff = sum(
        dept.min_num_staff * len(shift_time) * len(DAY_OF_WEEK) for dept in departments
    )
    # print(min_required_staff)

    """
    This will count the total number of staff across all shifts
     - Might break when some staff dont work on some specific days
    """
    # assigned_staff_count = sum(len(staff_list) for staff_list in assignment.values())
    assigned_staff_count = set(
        [
            stf
            for day, val in assignment.items()
            for department in val.values()
            for staff_list in department.values()
            for stf in staff_list
        ]
    )

    num_assigned_staff = len(
        [
            stf
            for day, val in assignment.items()
            for department in val.values()
            for staff_list in department.values()
            for stf in staff_list
        ]
    )
    # print('x ->', len(num_assigned_staff))
    # print(staff)
    # if all(stf.is_valid() for stf in staff):

    # print("Current Assignment ->", dict(assignment), '\n')

    # recurse over a function
    "assigned_staff: []"
    # if all department.is_valid() terminate recurs i.e if all depts has required num of staff

    # Choose unassigned domain | domain that isnt valid
    # valid_domains = [v for v in domains if len(assignment[v]) < v.max_num_staff]
    valid_domains = [
        (day, dom, tme)
        for day, val in domains.items()
        for dom in val
        for tme in shift_time
        if (
            (
                tme in dom.priority
                and len(assignment[day][dom.department_name][tme]) < dom.max_num_staff
            )
            or (
                tme not in dom.priority
                and len(assignment[day][dom.department_name][tme]) < dom.min_num_staff
            )
            # len(assignment[day][dom.department_name][tme]) < dom.max_num_staff
        )
    ]

    """
    ASSIGNMENT SATISFACTION CHECKS
    """

    if (
        (not valid_domains)
        or (len(assigned_staff_count) == len(staff))
        and (num_assigned_staff > min_required_staff)
        and all(
            len(assignment[day][dom.department_name][tme]) > 0
            for day, val in domains.items()
            for dom in val
            for tme in shift_time
        )
    ):
        # if len(assigned_staff_count) == len(staff):
        if all(st.hours_worked >= st.min_hours for st in staff):
            # if all(st.is_valid() for st in staff):
            return assignment

    """
    ASSIGNMENT SATISFACTION CHECKS
    """

    weights = [
        (
            10
            if (len(assignment[day][dom.department_name][tme]) == 0)
            else 1 / len(assignment[day][dom.department_name][tme])
        )
        for (day, dom, tme) in valid_domains
    ]
    # print(valid_domains)

    # if all domains have been filled
    # print(len(valid_domains))
    # if len(valid_domains) == 0:
    #     print("----HERE----")
    #     # print("Valid Domains", len(valid_domains))
    #     return assignment

    # print("Unassigned Domains ->", valid_domains, "\n")
    # print("Weights are", weights, "\n")
    day, dom, tme = random.choices(valid_domains, weights, k=1)[0]
    # print("'Selected Domain' ->", dom, "->", tme, "\n")

    "instead of looping over all staff everyday, get a random staff out of available staff"
    # stf = get_valid_staff(staff)
    # if stf is None:
    #     return None

    # valid_staff = [
    #     stf
    #     for stf in staff
    #     if stf.id not in set(get_other_staff(assignment, dom, day))
    # ]
    # random.shuffle(valid_staff)

    # print("Assignment ->", to_normal_dict(assignment), "\n")
    # print(
    #     [
    #         (s, s.hours_worked)
    #         for s in sorted(domains[day][dom][tme], key=lambda s: s.hours_worked)
    #     ]
    # )
    # for stf in sorted(domains[day][dom][tme], key= lambda s: s.hours_worked):
    # staff_copy = copy.copy(staff)
    # print('staff_copy', [s.hours_worked for s in staff_copy])
    # print('original staff', [s.hours_worked for s in staff])
    # print('domain staff', [s.hours_worked for s in domains[day][dom][tme]])

    # print('sorted staff', [s.hours_worked for s in sorted(staff, key=lambda s:s.hours_worked)])
    for stf in sorted(staff, key=lambda s: s.hours_worked):
        # for stf in domains[day][dom][tme]:
        stf.hours_worked += 4
        if not stf.is_valid():
            stf.hours_worked -= 4
            continue
        # for stf in valid_staff:
        # print("cur dom", dom)
        # other_staff = set(get_other_staff(assignment, dom, day))
        # if stf.id in other_staff:
        #     continue

        "clone assignment"
        new_assignment = copy.deepcopy(assignment)
        # print(new_assignment)
        # print("first", to_normal_dict(new_assignment))
        if use_id:
            new_assignment[day][dom.department_name][tme].append(stf.id)
        else:
            new_assignment[day][dom.department_name][tme].append(stf.name)
        # print(day, dom.department_name, tme, stf)
        # print(new_assignment)
        # time.sleep(10)

        # for other_tme in ['morning', 'afternoon', 'evening']:
        #     # if other_tme != tme:
        #     if (day, dom, other_tme) in valid_domains:
        #         new_assignment[day][dom.department_name][other_tme].append(stf.id)
        # print("Trying", new_assignment, "\n")
        # print(
        #     f"Second -> New Assignment of {stf} to ({dom}, {tme}) -> {to_normal_dict(new_assignment)}",
        #     "\n",
        # )

        # print(
        #     "checking validity...\nIs Valid? ",
        # )
        # stf.hours_worked += 4
        if is_valid(new_assignment, dom, tme, stf, day, use_id=use_id):
            # seen[dom][stf.id] += 4
            # print(
            #     f"New Assignment of {stf} to ({dom}, {tme}) -> {to_normal_dict(new_assignment)}",
            #     "\n",
            # )
            # time.sleep(5)
            result = backtrack(new_assignment, departments, staff, domains, use_id)
            if result:
                return result
        stf.hours_worked -= 4
        # print("before", to_normal_dict(new_assignment), "\n")
        # print(f"Removing {stf.id} from {dom.department_name} - {tme}")
        # new_assignment[dom.department_name][tme].remove(stf)
        # print("after", to_normal_dict(new_assignment))
        # i += 1
        # if i == 2:
        #     break
        # print("\n")
    return None


# if __name__ == "__main__":
def main(departments: list[DepartmentData], staff: list[StaffData], use_id=True):
    for stf in staff:
        stf.hours_worked = 0

    domains = {
        day: {
            department: {tme: [stf for stf in staff] for tme in shift_time}
            for department in departments
        }
        for day in DAY_OF_WEEK
    }

    if not is_feasibile(departments, staff):
        # print("Not Feasible")
        return None
    else:
        assignment: dict[str, dict[str, dict[str, list]]] = {
            day: {
                dept.department_name: {shift: [] for shift in shift_time}
                for day, val in domains.items()
                for dept in val
            }
            for day in DAY_OF_WEEK
        }
        res = to_normal_dict(
            backtrack(assignment, departments, staff, domains, use_id)
        )
        return res
        # print(json.dumps(to_normal_dict(assignment), indent=4))
        # print([(stf.id, stf.hours_worked) for stf in staff], "\n")
        # print(sum(stf.hours_worked for stf in staff)/ len(staff))
    # print(to_normal_dict(seen))


def validate_input(prompt: str, val_type: type = int):
    while True:
        answer = input(f"{prompt}")
        if val_type == int:
            if not answer.isnumeric():
                if answer.strip().lower() == "c":
                    return None
                print("Invalid input! Only Numerics allowed!!!")
                continue
        # if not isinstance(answer, val_type):
        #     # raise TypeError("Invalid type")
        #     print("Invalid type")
        #     # return False
        #     continue
        return int(answer)
        # return True


def print_schedule(res):
    for day in res:
        print(f"{day:<15}|{' Morning':<15}|{' Afternoon':<15}|{' Evening':<15}")
        print("-" * 60)
        for dept in res[day]:
            morning_staff = ",".join(map(str, (res[day][dept]["morning"])))
            afternoon_staff = ",".join(map(str, (res[day][dept]["afternoon"])))
            evening_staff = ",".join(map(str, (res[day][dept]["evening"])))
            print(
                f"{dept:<15}|"
                f"{morning_staff:<15}|"
                f"{afternoon_staff:<15}|"
                f"{evening_staff:<15}"
            )
        print("\n")


if __name__ == "__main__":
    departments: list[DepartmentData] = DepartmentData.list_departments()
    staff: list[StaffData] = StaffData.list_staff_members()

    # while True:
    print("Welcome to SchedulePro\n".center(50, " "))

    print("Menu Items".center(50, " "))
    print("-" * 50)

    prompt_dict = {
        "1": "Press 1 to display current departments and staff",
        "2": "Press 2 to add new Department",
        "3": "Press 3 to add new Staff",
        "4": "Press 4 to edit department",
        "5": "Press 5 to edit staff",
        "6": "Press 6 to delete instance",
        "7": "Press 7 to run Scheduler",
    }

    def create_dept(
        id: int = None,
        title: str = "Add New Departments (c to cancel)",
        create_new_instance: bool = True,
    ):
        print(f"\n{title}")
        department_name = input("Enter Department Name: ").strip().lower()
        if department_name == "c":
            return None
        min_staff = validate_input("Enter Minimum number of staff: ")
        if min_staff is None:
            return None
        max_staff = validate_input("Enter Maximum number of staff: ")
        if max_staff is None:
            return None

        if min_staff > max_staff:
            print(
                "\nInvalid -> Minimum Number of Staff cannot exceed max number of staff\n"
            )
            return None

        if create_new_instance:
            try:
                DepartmentData(
                    id=id,
                    department_name=department_name,
                    min_num_staff=min_staff,
                    max_num_staff=max_staff,
                )
                return True
            except ValueError as e:
                print("\n", str(e))

        return department_name, min_staff, max_staff

    def create_staff(
        id: int = None,
        title: str = "Add New Staff (c to cancel)",
        create_new_instance: bool = True,
    ):
        print(f"\n{title}")
        staff_name = input("Enter Staff Name: ").strip().lower()
        if staff_name == "c":
            return None
        while True:
            contract_hours = validate_input("Enter contract hours: ")
            if contract_hours is None:
                # break
                return None
            if not 8 <= contract_hours <= 40:
                print("Contract hours must be at least 8 at most 40")
                continue
            # break

            day_exclusions = set()
            day_availability_prompt = (
                input("Do you have any day you will be unavailable (y/n)? ")
                .strip()
                .lower()
            )
            if day_availability_prompt == "c":
                return True
            if day_availability_prompt == "y":
                print(f"\nWhat days are you unavailable -> {(DAY_OF_WEEK)}? ")
                while True:
                    unavailable_day = input("Enter day: ").strip().lower()
                    if unavailable_day == "c":
                        break
                    if unavailable_day not in DAY_OF_WEEK:
                        print("Invalid day")
                    else:
                        day_exclusions.add(unavailable_day)

                    cont = input("Add another day (y/n)? ")
                    if cont == "y":
                        continue
                    break
            elif day_availability_prompt == "n":
                pass
            else:
                print("Invalid Response")

            shift_exclusions = set()
            shift_availability_prompt = (
                input("Do you have any shift you will be unavailable (y/n)? ")
                .strip()
                .lower()
            )
            if shift_availability_prompt == "c":
                return None
            if shift_availability_prompt == "y":
                print(f"\nWhat shifts are you unavailable -> {(shift_time)}? ")
                while True:
                    unavailable_shift = input("Enter shift: ").strip().lower()
                    if unavailable_shift == "c":
                        break
                    if unavailable_shift not in shift_time:
                        print("Invalid shift")
                    else:
                        shift_exclusions.add(unavailable_shift)

                    cont = input("Add another shift (y/n)? ")
                    if cont == "y":
                        continue
                    break

                break
            elif shift_availability_prompt == "n":
                break
            else:
                print("Invalid Response")
                break

        if create_new_instance:
            try:
                StaffData(
                    id=id,
                    name=staff_name,
                    contract_hours=contract_hours,
                    shift_exclusion_list=list(shift_exclusions),
                    day_exclusion_list=list(day_exclusions),
                )
            except ValueError as e:
                print("\nInvalid User ->", str(e))
                print("")

        return staff_name, contract_hours, day_exclusions, shift_exclusions

    def draw_table(table: str) -> str:
        print("-" * 42)
        if table == "department":
            print(f"{'| ID':<20}|{'Department Name':^20}|")
            print("-" * 42)
            for department in departments:
                print(str(department.id).ljust(20, " "), end="")
                print(str(department).center(20, " "))
        else:
            print(f"{'| ID':<20}|{'Staff Name':^20}|")
            print("-" * 42)
            for staff_member in staff:
                print(str(staff_member.id).ljust(20, " "), end="")
                print(str(staff_member).center(20, " "))

        print("\n")

    def select_department(action: str = "edit"):
        dept_prompt = input(
            f"Enter ID or Name of department to {action} (c to cancel): "
        )
        if dept_prompt.strip().lower() == "c":
            return None
        if dept_prompt.isnumeric():
            dept_id = int(dept_prompt)
            dept = [
                department for department in departments if department.id == dept_id
            ]
        else:
            dept_name = dept_prompt.strip().lower()
            dept = [
                department
                for department in departments
                if department.department_name == dept_name
            ]

        if dept:
            return dept[0]
        print("Department does not exist")
        return None

    def select_staff(action: str = "edit"):
        staff_prompt = input(f"Enter ID or Name of staff to {action}: ")
        if staff_prompt.strip().lower() == "c":
            return None
        if staff_prompt.isnumeric():
            staff_id = int(staff_prompt)
            staff_instance_arr = [
                staff_member for staff_member in staff if staff_member.id == staff_id
            ]
        else:
            staff_name = staff_prompt.strip().lower()
            staff_instance_arr = [
                staff_member
                for staff_member in staff
                if staff_member.name == staff_name
            ]
        if staff_instance_arr:
            staff_instance = staff_instance_arr[0]
            print(
                f"\nStaff Name -> {staff_instance.name}\nContract Hours -> {staff_instance.contract_hours}\nDays Unavailable -> {staff_instance.day_exclusion_list}\nShifts Unavailable -> {staff_instance.shift_exclusion_list}\n"
            )
            return staff_instance

        print("Staff does not exist")
        return None

    while True:
        # while True:
        try:
            for key, val in prompt_dict.items():
                print(val)
            action_prompt = input("\nWhat would you like to do? ")
            if action_prompt == "":
                print("")
                continue
            if action_prompt not in prompt_dict:
                print("Invalid Action!!! Try Again")
                continue
            # break

            if action_prompt == "1":
                print("\nDisplay current Departments and Staff -> ")
                print("-" * 42)
                print(f"{'| Departments':<20}|{'Staff':^20}|")
                print("-" * 42)

                for department, staff_member in zip_longest(
                    departments, staff, fillvalue=""
                ):
                    print(str(department).ljust(20, " "), end="")
                    print(str(staff_member).center(20, " "))

                print("\n")

            elif action_prompt == "2":
                # while True:
                # if create_dept():
                create_dept()
                #     break
                # break
                print("\n")

            elif action_prompt == "3":
                while True:
                    if create_staff():
                        break
                    break
                print("\n")

            elif action_prompt == "4":
                draw_table("department")

                if not departments:
                    print("Maybe start with creating departments\n")
                    continue

                print("Edit Department by Name or ID\n")

                while True:
                    dept = select_department()
                    if dept is None:
                        break
                    if dept:
                        print(
                            f"\nDepartment Name -> {dept.department_name}\nMinimum Number of Staff -> {dept.min_num_staff}\nMaximum Number of Staff -> {dept.max_num_staff}"
                        )
                        while True:
                            result = create_dept(
                                title="Edit Department (c to cancel)",
                                create_new_instance=False,
                            )
                            if result is None:
                                break
                            new_name, new_min, new_max = result
                            if new_name:
                                dept.department_name = new_name
                                dept.min_num_staff = new_min
                                dept.max_num_staff = new_max
                                break

                            print("\n")
                    else:
                        print("Department does not exist")
                        continue

            elif action_prompt == "5":
                draw_table("staff")

                if not staff:
                    print("No Staff available\n")
                    continue

                print("Edit Staff by Name or ID\n")

                while True:
                    staff_instance = select_staff()
                    if staff_instance is None:
                        break
                    break

                while True:
                    result = create_staff(
                        title="Edit Staff (c to cancel)", create_new_instance=False
                    )
                    if result is None:
                        print("\n")
                        break

                    new_name, contract_hours, days_unavailable, shifts_unavailable = (
                        result
                    )

                    if new_name:
                        staff_instance.name = new_name
                        staff_instance.contract_hours = contract_hours
                        if days_unavailable:
                            staff_instance.day_exclusion_list = list(days_unavailable)
                        if shifts_unavailable:
                            staff_instance.shift_exclusion_list = list(
                                shifts_unavailable
                            )
                        print("\n")
                        break

                    print("\n")

            elif action_prompt == "6":
                delete_prompt = validate_input(
                    "1 to delete Department, 2 to delete Staff (c to cancel): "
                )
                if delete_prompt is None:
                    continue

                elif delete_prompt == 1:
                    draw_table("department")
                    dept = select_department(action="delete")
                    if dept is None:
                        print("\n")
                        continue
                    else:
                        DepartmentData.departments.remove(dept)
                        print("\n")
                elif delete_prompt == 2:
                    draw_table("staff")
                    staff_instance = select_staff(action="delete")
                    if staff_instance is None:
                        print("\n")
                        continue
                    else:
                        StaffData.staff_members.remove(staff_instance)
                        print("\n")

                else:
                    print("Invalid Response")
                    continue

            elif action_prompt == "7":
                res = main(departments, staff)
                res_name = main(departments, staff, use_id=False)
                # print("")
                # print(res)
                # print("")
                # print(res_name)
                print("")
                print_schedule(res_name)

            else:
                print("Invalid Prompt\n")

        except KeyboardInterrupt:
            quit()

# if __name__ == "__main__":
#     departments: list[DepartmentData] = DepartmentData.list_departments()
#     staff: list[StaffData] = StaffData.list_staff_members()

#     # create departments
#     shoes = DepartmentData("shoes", 1)
#     cashier = DepartmentData("cashier", 5, 2)
#     home = DepartmentData("home", 2)

#     # create staff
#     kolade = StaffData(
#         "kolade",
#         position="associate",
#         shift_exclusion_list=["evening"],
#         contract_hours=20,
#     )
#     motun = StaffData("motun", position="associate")
#     core = StaffData("core", position="associate", contract_hours=20)
#     kunle = StaffData("kunle", position="associate")
#     dara = StaffData("dara", position="associate")
#     lanre = StaffData("lanre", position="associate")
#     tayo = StaffData("tayo", position="associate")
#     loli = StaffData("loli", position="associate")
#     shem = StaffData("shem", position="associate")
#     riri = StaffData("riri", position="associate")


#     domains = {department: staff for department in departments}

#     domains = {
#         day: {
#             department: {tme: [stf for stf in staff] for tme in shift_time}
#             for department in departments
#         }
#         for day in DAY_OF_WEEK
#     }
#     res = main(departments, staff, use_id=True)
#     print(res)
#     # print(json.dumps(res, indent=2))
