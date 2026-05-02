import random

# Define classes for Departments and Staff

# Some departments should only require staff during specific shifts like only evenings or afternoons and evenings or morning, afternoon and evenings

# Some staff members have availability days


class Staff:
    """
    Each staff has a
    - Name
    - Contracted hours
    - Position (Associate, Management, Team Lead, Loss Protection)
    - Availability (To Be Implemented)
    """

    # i'm to add staff availability, i.e some staff can only work on some certain days

    staff_members: list["Staff"] = []

    def __init__(
        self,
        name: str,
        position: str,
        shift_exclusion_list: list = [],
        day_exclusion_list: list = [],
        contract_hours: int = 40,
    ):
        self.name = name.lower()
        self.position = position.lower()
        self.contract_hours = contract_hours
        self.min_hours = 8
        self.hours_worked = 0
        self.shift_exclusion_list = shift_exclusion_list
        self.day_exclusion_list = day_exclusion_list
        self.working = False

        self.__class__.staff_members.append(self)

    @classmethod
    def list_staff_members(cls):
        return cls.staff_members

    def add_hours(self):
        self.hours_worked += 4
        # return self.hours_worked

    def remove_hours(self):
        self.hours_worked -= 4
        # return self.hours_worked

    def is_valid(self):
        # return self.min_hours <= self.hours_worked <= self.contract_hours
        return self.hours_worked <= self.contract_hours

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Staff):
            return self.name == other.name
        return NotImplemented

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)


class Department:
    """
    Each department has a
    - Name
    - Maximum number of staff at every given shift
    """

    departments = []

    def __init__(
        self,
        department_name: str,
        max_num_staff: int,
        min_num_staff: int = 1,
    ):
        self.department_name = department_name.lower()
        self.__class__.departments.append(self)
        self.max_num_staff = max_num_staff
        self.min_num_staff = min_num_staff
        self.priority = ["afternoon", "evening"]
        self.staff_list = []

    @classmethod
    def list_departments(cls):
        return cls.departments

    def add_staff(self, staff: Staff):
        self.staff_list.append(staff)

    def is_valid(self, num_staff):
        # return self.min_num_staff <= len(self.staff_list) <= self.max_num_staff
        return self.min_num_staff <= num_staff <= self.max_num_staff

    def is_full(self):
        return self.min_num_staff == len(self.staff_list)

    def __str__(self):
        return self.department_name

    def __repr__(self) -> str:
        return self.department_name

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Department):
            return self.department_name == other.department_name
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.department_name)
