from collections import Counter, defaultdict
from classes import *
import random
import copy
import time
import json

# create departments
shoes = Department("shoes", 1)
cashier = Department("cashier", 5, 2)
home = Department("home", 2)
ladies = Department("ladies", 2)
processing = Department("processing", 4, 2)
beauty = Department("beauty", 1)
jewellery = Department("jewellery", 1)

# create staff
kolade = Staff("kolade", "associate")
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
bukayo = Staff("bukayo", "associate")
bola = Staff("bola", "associate")
niran = Staff("niran", "associate")
divine = Staff("divine", "associate")
taiwo = Staff("taiwo", "associate")
sam = Staff("sam", "associate")
bosun = Staff("bosun", "associate")
claudia = Staff("claudia", "associate")
mimi = Staff("mimi", "associate")
oba = Staff("oba", "associate")

departments = Department.list_departments()
staff_members = Staff.list_staff_members()

days = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]
shifts = ["morning", "afternoon", "evening"]

domains = []
for day in days:
    for shift in shifts:
        for department in departments:
            domain = day + "_" + shift + "_" + department.name
            domains.append(domain)

assigned_domains = {}

_THRESHOLD_SHIFT = 14


def target_capacity(domain):
    day_time, dept = simplify_domain(domain)  # e.g. "monday_morning"
    # Parse the shift reliably instead of using 'in' substring checks
    _, shift = day_time.split("_", 1)  # shift = "morning" | "afternoon" | "evening"
    min_staff = getattr(dept, "min_staff", 0)
    return min_staff if shift == "morning" else dept.max_staff


def schedule_feasibility(
    departments, staff_list, days, shifts, hours=4, min_shifts=5, max_shifts=10
):
    # --- Total coverage check ---
    num_staff_per_shift = sum(department.min_staff for department in departments)
    num_shifts_per_week = len(days) * len(shifts)
    hours_required = num_staff_per_shift * num_shifts_per_week * hours
    hours_available = sum(stf.contract_hours for stf in staff_list)

    results = []
    results.append(f"Hours Available: {hours_available}")
    results.append(f"Hours Required: {hours_required}")

    if hours_available < hours_required:
        results.append("❌ Not enough total staff hours to cover shifts")
        # print("\n".join(results))

    # --- Staff distribution check ---
    avg_required_per_staff = hours_required / len(staff_list)

    for stf in staff_list:
        if stf.contract_hours < min_shifts * hours:
            results.append(
                f"⚠️ {stf.name} cannot meet minimum {min_shifts} shifts ({stf.contract_hours}h contract)"
            )
        if stf.contract_hours > max_shifts * hours:
            results.append(
                f"⚠️ {stf.name} may exceed maximum {max_shifts} shifts ({stf.contract_hours}h contract)"
            )

    # --- Department coverage check ---
    for dept in departments:
        dept_required = dept.min_staff * num_shifts_per_week * hours
        if sum(stf.contract_hours for stf in staff_list) < dept_required:
            results.append(
                f"❌ Not enough hours available to cover {dept.name}"
            )

    # print("\n".join(results))
    if len(results) == 2:  # only totals, no warnings
        results.append("✅ Feasible on both total and distribution checks")
        return True
    else:
        return False

def is_domain_valid(domain, assignment):
    _, department = simplify_domain(domain)
    staff_assigned = assignment.get(domain, [])
    # if len(staff_assigned) < department.max_staff:
    #     return True
    # return False
    have = len(assignment.get(domain, []))
    return have < target_capacity(domain)


def choose_domain(assignment):
    best, best_remaining = None, None
    for domain in domains:
        cap = target_capacity(domain)
        if not (is_domain_valid(domain, assignment)):
            continue
        _, dept = simplify_domain(domain)
        # remaining = dept.max_staff - len(assignment.get(domain, []))
        remaining = cap - len(assignment.get(domain, []))
        if best is None or remaining < best_remaining:
            best, best_remaining = domain, remaining
    return best


def all_mins_met(assignment):
    for d in domains:
        _, dept = simplify_domain(d)
        if len(assignment.get(d, [])) < getattr(dept, "min_staff", 0):
            return False
    return True


def simplify_domain(domain):
    """
    This function extracts the department from the domain, the department is usually the last thing in the string
    e.g monday_morning_shoes (day, time, department)
    """
    splits = domain.rsplit("_", 1)
    day_time = splits[0]
    name = splits[1]
    department = [
        department
        for department in departments
        if department.name == name
    ][0]
    return day_time, department


def consistent(assignment):
    """
    To check the consistency of a domain, we must ensure that
    1. Each department in the domain must meet its requirement for staff allocation
    2. Each staff cannot be in different departments same time
    3. There must be at least 2 team leads each day
    """
    shifts = Counter(staff for val in assignment.values() for staff in val)

    for key, staff in assignment.items():
        day_time, department = simplify_domain(key)

        "if any staff has worked over their max hours, remove staff"
        if any(
            shifts[stf] > _THRESHOLD_SHIFT for stf in staff
        ):  # because 12 shifts is 48hours
            return False

        "Each department must have its minimum num_of_staff and not exceed its max"
        if len(staff) > department.max_staff:
            return False

        "No duplicate staff in each shift"
        freq = Counter(staff)
        if any(freq[st] > 1 for st in staff):
            return False

        "Each staff must only be in one department per shift"
        for sec_key, sec_staff in assignment.items():
            if sec_key == key:
                continue

            if day_time in sec_key:
                for stf in staff:
                    if stf in assignment[sec_key]:
                        return False

    return True


# assignment will first be empty dictionary := {}
def backtrack(assignment):
    # if all items in domain exist in the assignment, that means each domain has been assigned a representative
    domain = choose_domain(assignment)
    if domain is None:
        used = {n for vals in assignment.values() for n in vals}
        if all_mins_met(assignment) and all(stf.name in used for stf in staff_members):
            return assignment
        return None

    # unfilled_domains = [d for d in domains if is_domain_valid(d, assignment)]

    shifts = Counter(staff for val in assignment.values() for staff in val)
    available_staff = [
        stf for stf in staff_members if shifts[stf.name] < _THRESHOLD_SHIFT
    ]
    # random.shuffle(available_staff)

    used_in_shift = defaultdict(set)
    for d, names in assignment.items():
        dt, _ = simplify_domain(d)
        used_in_shift[dt].update(names)

    # for domain in unfilled_domains:
    day_time, dept = simplify_domain(domain)
    for stf in available_staff:
        name = stf.name
        curr_staff_list = assignment.get(domain, [])

        # check the staff isnt in the domain
        if name in curr_staff_list:
            continue

        # change staff if day_time is same in domain
        if name in used_in_shift[day_time]:
            continue

        # if the current staff has reached his/her min_contract hours and there is someone else who hasnt, skip the current staff and go to the next
        # if shifts[name] >= 10:
        #     if any(shifts[staff] < 5 for staff in available_staff):
        #         continue

        # copy the assignment and keep original
        new_assignment = copy.deepcopy(assignment)

        if not new_assignment.get(domain):
            new_assignment[domain] = [name]
        else:
            new_assignment[domain].append(name)

        if consistent(new_assignment):
            result = backtrack(new_assignment)
            if result is not None:
                return result
    return None


def sort_assignment(assignment, day_order):
    # Sort the keys based on the day_order
    sorted_items = sorted(
        assignment.items(), key=lambda item: day_order.index(item[0].split("_")[0])
    )

    # Rebuild the dictionary with the new order
    return dict(sorted_items)


def json_conv(assignment):
    readable_solution = {
        domain: [s.name for s in assigned_staff]
        for domain, assigned_staff in assignment.items()
    }
    return json.dumps(readable_solution, indent=4)


if __name__ == "__main__":
    print(schedule_feasibility(departments, staff_members, days, shifts))
    # print(sum(stf.contract_hours for stf in staff_members))
    solution = sort_assignment(backtrack({}), days)
    myDict = defaultdict(lambda: defaultdict(dict))
    for key, values in solution.items():
        day, shift, dept = key.split("_")
        myDict[day][shift][dept] = values

    json_solution = json.dumps(myDict, indent=4)
    # print(json_solution)

    arr = []
    for k, v in solution.items():
        arr.extend(v)

    print(Counter(arr))
