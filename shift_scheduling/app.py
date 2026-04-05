from classes import Department, Staff
import copy
import random
from collections import defaultdict

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
# daoud = Staff("daoud", "associate")
# hasan = Staff("hasan", "associate")
# zara = Staff("zara", "associate")
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

departments = Department.list_departments()  # variables
staff = Staff.list_staff_members()

domains = {department: staff for department in departments}
# print(domains)

# print({dom:val for dom,val in domains.items() if dom != cashier}.values())


def is_feasibile():
    total_min_staff = sum(department.min_num_staff for department in departments)
    total_max_staff = sum(department.max_num_staff for department in departments)

    total_num_staff = len(staff)

    if total_min_staff <= total_num_staff <= total_max_staff:
        return True

    if total_min_staff > total_num_staff:
        print(
            "Total number of required staff is greater than total number of available staff"
        )

    if total_num_staff > total_max_staff:
        print(
            "Total number of available staff is more than total number of required staff"
        )

    print(f"Staff number should be between {total_min_staff} and {total_max_staff}")
    return False


def choose_staff(staff_list):
    """
    This function takes the overall staff list and returns a valid staff member for assignment
    """

    copied_staff_list = copy.deepcopy(staff_list)
    available_staff = [staff for staff in copied_staff_list if not staff.is_valid()]

    return random.choice(available_staff)


def is_valid(assignment, domain, staff):
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
    if domain.max_num_staff < len(assignment[domain]):
        return False

    # same staff cant be assigned to same domain more than once
    if assignment[domain].count(staff) > 1:
        return False

    # one staff can not be in more than one domain
    "exclude the current domain and check staff not in other domains"
    other_assignment = {dom: val for dom, val in assignment.items() if dom != domain}
    assigned_staff_arr = other_assignment.values()
    for staff_list in assigned_staff_arr:
        if staff in staff_list:
            return False
    # if staff in [staff_list for staff_list in assigned_staff_arr]:
    #     return False

    return True

seen = set()
def backtrack(assignment):
    # before running the main function, check if there is a solution
    if not is_feasibile():
        return {}
    
    # print("Current Assignment ->", dict(assignment), '\n')

    # recurse over a function
    "assigned_staff: []"
    # if all department.is_valid() terminate recurs i.e if all depts has required num of staff

    # Choose unassigned domain | domain that isnt valid
    valid_domains = [v for v in domains if len(assignment[v]) < v.max_num_staff]
    weights = [
        10 if len(assignment[dom]) == 0 else 1 / len(assignment[dom])
        for dom in valid_domains
    ]

    if len(valid_domains) == 0:
        return True
    
    assigned_staff_count = sum(len(staff_list) for staff_list in assignment.values())
    if assigned_staff_count == len(staff):
        return True

    # print("Unassigned Domains ->", valid_domains, "\n")
    # print("Weights are", weights, "\n")
    var = random.choices(valid_domains, weights, k=1)[0]
    # print("'Selected Domain' ->", var, "\n")

    for stf in domains[var]:
        if stf in seen:
            continue
        new_assignment = assignment.copy()
        new_assignment[var].append(stf)

        if is_valid(new_assignment, var, stf):
            seen.add(stf)
            # print(
            #     f"'New Assignment for {str(var).capitalize()}' ->",
            #     dict(new_assignment),
            #     "is valid",
            #     "\n",
            # )
            result = backtrack(new_assignment)
            if result:
                return assignment
        new_assignment[var].remove(stf)
        print("\n")
    return None


if __name__ == "__main__":
    assignment_dict = defaultdict(list)
    res = backtrack(assignment_dict)
    print(dict(res))
