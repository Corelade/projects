import random

# TODO
"""
 - Define classes for DepartmentData and StaffData
 - Staff members have availability days
 - Some Departments should only require staff during specific shifts like only evenings or afternoons and evenings or morning, afternoon and evenings
"""

# NOTE
"""
     - Two different staff can have same name 
"""


class StaffData:
    """
    Each staff has a
    - Name
    - Contracted hours
    - Availability
    - Position (Associate, Management, Team Lead, Loss Protection) To Be Fully Implemented
    """

    staff_members: list["StaffData"] = []
    next_id = 1

    def __init__(
        self,
        name: str,
        id: int | None = None,
        position: str = "associate",
        shift_exclusion_list: list = [],
        day_exclusion_list: list = [],
        contract_hours: int = 40,
    ):
        self.id = id
        # self.name = name
        self.name = name.lower()
        self.position = position.lower()
        self.contract_hours = contract_hours
        self.min_hours = 8
        self.hours_worked = 0
        self.shift_exclusion_list = shift_exclusion_list
        self.day_exclusion_list = day_exclusion_list
        self.working = False
        
        # contract hours must be at least 8 hours
        if self.contract_hours < 8:
            raise ValueError("Contract hours must be at least 8 hours")

        if not self._is_feasible():
            raise ValueError(
                "Contract hours exceed the staff member's available working hours."
            )

        if not self.id:
            self.id = StaffData.next_id
            StaffData.next_id += 1

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

    def _is_feasible(self):
        """
        Function to check if the initialization parameters are valid

         - Daily hours is the number of hours/shifts that a Staff can do daily: 12 is the maxinum num of hours a Staff can do daily (4 hour per shift * 3 shifts)
         - Available days is to check the days a Staff is available to work: 7 is the number of days in a week
        """
        daily_hours = 12 - (4 * len(self.shift_exclusion_list))
        available_days = 7 - len(self.day_exclusion_list)

        avail_hours = daily_hours * available_days

        # the contract hours should be more than the available hours they can work
        return (
            self.contract_hours <= avail_hours
            and avail_hours != 0
            and self.contract_hours != 0
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, StaffData):
            return self.id == other.id
        raise ValueError("Obects are of different types. Requires same obect of type StaffData")

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)


class DepartmentData:
    """
    Each department has a
    - Name
    - Maximum number of staff at every given shift
    """

    departments: list["DepartmentData"] = []
    next_id = 1

    def __init__(
        self,
        department_name: str,
        max_num_staff: int,
        min_num_staff: int = 1,
        id: int = None,
    ):
        self.id = id
        self.department_name = department_name.lower()
        self.max_num_staff = max_num_staff
        self.min_num_staff = min_num_staff
        self.priority = ["afternoon", "evening"]
        self.staff_list = []
        if self.department_name in [
            d.department_name for d in DepartmentData.departments
        ]:
            raise ValueError("Department name exists already.")

        if not self.id:
            self.id = DepartmentData.next_id
            DepartmentData.next_id += 1
        self.__class__.departments.append(self)

    @classmethod
    def list_departments(cls):
        return cls.departments

    def add_staff(self, staff: StaffData):
        self.staff_list.append(staff)

    def is_valid(self, num_staff):
        # return self.min_num_staff <= len(self.staff_list) <= self.max_num_staff
        return self.min_num_staff <= num_staff <= self.max_num_staff

    def is_full(self):
        return self.min_num_staff == len(self.staff_list)

    def __str__(self):
        return self.department_name
        # return self.id

    def __repr__(self) -> str:
        return self.department_name

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DepartmentData):
            return self.department_name == other.department_name
        raise ValueError(
            "Obects are of different types. Requires same obect of type DepartmentData"
        )

    def __hash__(self) -> int:
        return hash(self.department_name)
