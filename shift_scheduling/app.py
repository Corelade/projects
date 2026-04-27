from .classes import Department, Staff
import copy
import random
from collections import defaultdict
import json
import time

# create departments
shoes = Department("shoes", 1)
cashier = Department("cashier", 5, 2)
home = Department("home", 2)
ladies = Department("ladies", 2)
processing = Department("processing", 4, 2)
beauty = Department("beauty", 1)
jewellery = Department("jewellery", 1)

# create staff
kolade = Staff("kolade", "associate", ["evening"])
motun = Staff("motun", "associate")
core = Staff("core", "associate")
kunle = Staff("kunle", "associate")
dara = Staff("dara", "associate")
lanre = Staff("lanre", "associate")
tayo = Staff("tayo", "associate")
loli = Staff("loli", "associate")
shem = Staff("shem", "associate")
riri = Staff("riri", "associate")
segun = Staff("segun", "associate")
halafia = Staff("halafia", "associate")
ayo = Staff("ayo", "associate")
daoud = Staff("daoud", "associate")
hasan = Staff("hasan", "associate")
zara = Staff("zara", "associate")
# bukayo = Staff("bukayo", "associate")
# bola = Staff("bola", "associate")
# niran = Staff("niran", "associate")
# divine = Staff("divine", "associate")
# taiwo = Staff("taiwo", "associate")
# sam = Staff("sam", "associate")
# bosun = Staff("bosun", "associate")
# claudia = Staff("claudia", "associate")
# mimi = Staff("mimi", "associate")
# oba = Staff("oba", "associate")

departments: list[Department] = Department.list_departments()  # domiables
staff: list[Staff] = Staff.list_staff_members()

# domains = {department: staff for department in departments}

shift_time = ["morning", "afternoon", "evening"]
DAY_OF_WEEK = ["monday", "tuesday", "wednesday", "thursday", "friday"]
domains = {
    day: {
        department: {tme: [stf for stf in staff] for tme in shift_time}
        for department in departments
    }
    for day in DAY_OF_WEEK
}
# domains = {
#     department: {tme: [stf for stf in staff] for tme in shift_time}
#     for department in departments
# }

# printable_tmed_domains = {
#     day: {
#         department.department_name: {
#             tme: [stf.name for stf in staff] for tme in shift_time
#         }
#         for department in departments
#     }
#     for day in DAY_OF_WEEK
# }

# print(domains)
# print(max(len(stf_list) for stf_list in tmed_domains[shoes].values()))
# print(json.dumps(printable_tmed_domains, indent=4))
# print(printable_tmed_domains)

# print({dom:val for dom,val in domains.items() if dom != cashier}.values())

# NUM_HOURS = 12
# required_hours = NUM_HOURS * len(departments)
# available_hours = sum(stf.contract_hours for stf in staff)

# print('Required Hours', required_hours, '\n', 'Available Hours', available_hours)

# valid_domains = [
#     (day, dom, tme)
#     for day, val in domains.items()
#     for dom in val
#     for tme in shift_time
#     if (
#         (tme in dom.priority and len(domains[day][dom][tme]) <= dom.max_num_staff)
#         or (tme not in dom.priority and len(domains[day][dom][tme]) <= dom.min_num_staff)
#     )
# ]
# print(valid_domains)


def to_normal_dict(d):
    if isinstance(d, dict):
        result = {str(k): to_normal_dict(v) for k, v in d.items()}
        # print(json.dumps(result, indent=4))
        return result
    return d


def is_feasibile(depts: list[Department], staff_arr: list[Staff]):
    """
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
        return False

    NUM_SHIFTS = 3
    # this gets the total number of shifts that need filling
    shifts_to_fill = 0
    for dept in depts:
        req_hours = dept.min_num_staff * NUM_SHIFTS
        shifts_to_fill += req_hours

    if shifts_to_fill < len(staff_arr):
        # i.e too many staff available
        print("too many staff")
        return False
    # print(shifts_to_fill, len(staff_arr))

    # if total_num_staff > total_max_staff:
    #     print(
    #         "Total number of available staff is more than total number of required staff"
    #     )
    #     return False

    # print(f"Staff number should be between {total_min_staff} and {total_max_staff}")
    # return False

    # check for required hours and staff hours
    "Each department is open for 12 hours a day"
    NUM_HOURS = 12
    # required_hours = NUM_HOURS * len(depts)

    for day in DAY_OF_WEEK:
        unfilled = defaultdict(int)
        # available_hours = 0
        for stf in staff_arr:
            # available_hours = sum(
            #     stf.contract_hours
            #     for stf in staff_arr
            #     if (day not in stf.day_exclusion_list)
            #     or (tme not in stf.shift_exclusion_list)
            # )
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

        # if available_hours < required_hours:
        #     print(
        #         f"Required Hours for {day}->",
        #         required_hours,
        #         "\nAvailable Hours ->",
        #         available_hours,
        #     )
        #     return False

    # if total_min_staff <= total_num_staff <= total_max_staff:
    #     return True

    total_min_staff = sum(department.min_num_staff for department in depts)
    # total_max_staff = sum(department.max_num_staff for department in depts)

    # total_num_staff = len(staff_arr)

    if total_min_staff > len(staff_arr):
        print(
            "Total number of required staff is greater than total number of available staff"
        )
        return False

    # print('unknown')
    return True


def valid_staff(staff_list):
    """
    This function takes the overall staff list and returns a valid staff member for assignment
    """

    copied_staff_list = copy.deepcopy(staff_list)
    available_staff = [staff for staff in copied_staff_list if not staff.is_valid()]

    return random.choice(available_staff)


def get_other_staff(assignment, domain: Department, cur_day):
    '''
    Checks already assigned staff for a given day that are in other departments
    '''
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


def is_valid(assignment: dict, domain: Department, tme, staff: Staff, day: str):
    # checks to see if an assigment is valid

    """
    - One domain can not have more than its maximum capacity
    - One staff can not be in more than one domain
    """
    # print(f'CHECKING VALIDATION FOR "{domain}"')
    # print(dict(assignment))
    # print("Num of staff in assignment", len(assignment[domain]))
    # print("Max allowable staff", domain.max_num_staff, "\n")

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
    #     assignment[domain.department_name][tme].count(staff.name),
    #     "\n",
    # )
    if assignment[day][domain.department_name][tme].count(staff.name) > 1:
        # print(
        #     f"Error -> Staff:{staff} appears {assignment[domain.department_name][tme].count(staff)} times",
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
    #     staff.name,
    #     assigned_staff_arr,
    #     staff.name in assigned_staff_arr,
    # )
    # print(f"Assigned Staff Array -> {assigned_staff_arr}", "\n")
    if staff.name in assigned_staff_arr:
        # print(f"Error -> {staff} already in assigned_staff_arr", "\n")
        return False
    # if staff in [staff_list for staff_list in assigned_staff_arr]:
    #     return False

    return True


seen = defaultdict(lambda: defaultdict(int))


def backtrack(assignment):
    # before running the main function, check if there is a solution
    # if not is_feasibile():
    #     return {}

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
    # if all staff has been assigned to departments
    if len(assigned_staff_count) == len(staff):
        # print("HEREEEE")
        return assignment

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
        )
    ]
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

    # print("Assignment ->", to_normal_dict(assignment), "\n")
    for stf in domains[day][dom][tme]:
        # print("cur dom", dom)
        other_staff = set(get_other_staff(assignment, dom, day))
        if stf.name in other_staff:
            continue

        new_assignment = copy.deepcopy(assignment)
        # print(new_assignment)
        # print("first", to_normal_dict(new_assignment))
        new_assignment[day][dom.department_name][tme].append(stf.name)
        # print("Trying", new_assignment, "\n")
        # print(
        #     f"Second -> New Assignment of {stf} to ({dom}, {tme}) -> {to_normal_dict(new_assignment)}",
        #     "\n",
        # )

        # print(
        #     "checking validity...\nIs Valid? ",
        # )
        if is_valid(new_assignment, dom, tme, stf, day):
            # seen[dom][stf.name] += 4
            # print(
            #     f"New Assignment of {stf} to ({dom}, {tme}) -> {to_normal_dict(new_assignment)}",
            #     "\n",
            # )
            # time.sleep(5)
            result = backtrack(new_assignment)
            if result:
                return result
        # print("before", to_normal_dict(new_assignment), "\n")
        # print(f"Removing {stf.name} from {dom.department_name} - {tme}")
        # new_assignment[dom.department_name][tme].remove(stf)
        # print("after", to_normal_dict(new_assignment))
        # i += 1
        # if i == 2:
        #     break
        # print("\n")
    return None


if __name__ == "__main__":
    if not is_feasibile(departments, staff):
        pass
    else:
        assignment = {
            day: {
                dept.department_name: {shift: [] for shift in shift_time}
                for day, val in domains.items()
                for dept in val
            }
            for day in DAY_OF_WEEK
        }
        # print(json.dumps(to_normal_dict(assignment), indent=4))
        res = to_normal_dict(backtrack(assignment))
        print(json.dumps(res, indent=2))
    # print(to_normal_dict(seen))


"""
TODO

- Priority should have highest number of staff e.g if evening shift is priority, it will have more staff assigned than less priority. This could be done by maybe assigning weights again to the shifts so higher weight has more chance of being chosen
"""
