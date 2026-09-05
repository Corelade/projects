import pytest
from ..app import *
from ..classes import StaffData, DepartmentData


class BaseClass:
    """
    Class to setup test variables
    """

    def setup_method(self, method):
        DepartmentData.reset()
        StaffData.reset()
        DepartmentData.next_id = 1
        StaffData.next_id = 1

        self.shoes = DepartmentData("shoes", 1)
        self.mens = DepartmentData("men", 1)
        self.ladies = DepartmentData("ladies", max_staff=2, min_staff=2)
        self.home = DepartmentData("home", 1)

        self.kolade = StaffData("Kolade", "associate", shift_exclusion_list=["evening"])
        self.kunle = StaffData("Kunle", "associate", day_exclusion_list=["tuesday"])
        self.motun = StaffData("Motun", "associate", shift_exclusion_list=["evening"])
        self.bola = StaffData("Bola", "associate")
        self.core = StaffData("Core", "associate")
        self.loli = StaffData("loli", "associate")
        self.shem = StaffData("shem", "associate")
        self.riri = StaffData("riri", "associate")
        self.segun = StaffData("segun", "associate")
        self.halafia = StaffData("halafia", "associate")
        self.daoud = StaffData("daoud", "associate")
        self.hasan = StaffData("hasan", "associate")
        self.zara = StaffData("zara", "associate")

    def teardown_method(self):
        StaffData.reset()
        DepartmentData.reset()


class TestStaffData(BaseClass):
    def test_staff_feasibility_invalid(self):
        with pytest.raises(ValueError):
            StaffData(
                name="Kolade",
                position="associate",
                shift_exclusion_list=["morning", "afternoon"],
                day_exclusion_list=[
                    "monday",
                    "tueday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                ],
                contract_hours=40,
            )

        with pytest.raises(ValueError):
            StaffData(
                name="Kolade",
                position="associate",
                contract_hours=0,
            )

    def test_staff_feasibility_valid(self):
        self.kolade = StaffData(
            name="Kolade",
            position="associate",
            shift_exclusion_list=["morning"],
            day_exclusion_list=[
                "monday",
            ],
            contract_hours=40,
        )
        assert self.kolade is not None
        assert self.kolade.name == "kolade"

    def test_same_staff_fail(self):
        "Test that compares id of two instances of StaffData object"
        self.k1 = StaffData(
            name="Kolade",
            position="associate",
            contract_hours=35,
        )

        self.k2 = StaffData(
            name="Kolade",
            position="associate",
            contract_hours=35,
        )
        assert self.k1 != self.k2

        # with pytest.raises(ValueError):
        assert self.k1 != self.shoes


class TestDepartmentData:
    pass


class TestCheckFeasibility(BaseClass):
    """
    This class checks whether the current staff and shifts will lead to an assignment
    """

    # @pytest.mark.skip(reason="tried")
    def test_feasibility_is_false(self):
        """All of the checks here should return False"""
        # if no staff nor dept
        # assert is_feasibile([], []) is False
        with pytest.raises(ScheduleError):
            assert is_feasibile([], [])
        # assert is_feasibile(
        #     [self.shoes], [self.bola, self.core, self.loli, self.riri, self.shem]
        # ) #more available staff than depts required
        with pytest.raises(ScheduleError):
            assert (
                is_feasibile([self.shoes], [self.kolade, self.kunle]) is False
            )  # Kunle not available tuesday, kolade not available tuesday evening
        with pytest.raises(ScheduleError):
            assert (
                is_feasibile([self.shoes], [self.kunle]) is False
            )  # Kunle not available tuesday
        with pytest.raises(ScheduleError):
            assert (
                is_feasibile([self.shoes], [self.kolade]) is False
            )  # kolade not available during evenings which leave empty unfilled space
        with pytest.raises(ScheduleError):
            assert (
                is_feasibile([self.shoes, self.mens], [self.kolade]) is False
            )  # num of department_staff required is less than staff available
        with pytest.raises(ScheduleError):
            assert (
                is_feasibile([self.shoes], [self.kolade, self.motun]) is False
            )  # both staff not available evenings and will leave empty space
        with pytest.raises(ScheduleError):
            assert (
                is_feasibile(
                    [self.mens],
                    [self.riri, self.halafia, self.segun, self.daoud],
                    DAY_OF_WEEK=["monday"],
                )
                is False
            )  # too many staff available
        with pytest.raises(ScheduleError):
            assert (
                is_feasibile([self.shoes, self.ladies], [self.bola, self.core]) is False
            )
        # assertion for controlling max_hours as a staff shouldnt work more than contract hours in a week
        with pytest.raises(ScheduleError):
            assert (
                is_feasibile(
                    [self.mens],
                    [self.bola],
                    DAY_OF_WEEK=[
                        "monday",
                        "tuesday",
                        "wednesday",
                        "thursday",
                    ],
                )
                is False
            )

        # not enough hours
        with pytest.raises(ScheduleError):
            assert is_feasibile([self.mens], [self.bola, self.core])

    # @pytest.mark.skip(reason="tried")
    def test_feasibility_is_true(self):
        """These checks should return True"""
        assert is_feasibile([self.mens], [self.bola], ["monday", "tuesday"]) is True
        assert is_feasibile([self.mens], [self.bola, self.core, self.kunle]) is True
        assert (
            is_feasibile(
                [self.shoes], [self.bola, self.riri, self.loli, self.shem, self.segun]
            )
            is True
        )
        # checking two depts with one department requiring at least 2 people at all times
        assert (
            is_feasibile(
                [self.shoes, self.ladies],
                [
                    self.bola,
                    self.core,
                    self.loli,
                    self.shem,
                    self.riri,
                    self.segun,
                    self.halafia,
                    self.daoud,
                    self.hasan,
                ],
            )
            is True
        )


class TestStaffValidity:
    def setup_method(self):
        StaffData.reset()

        self.motun = StaffData("motun", position="associate")
        self.bola = StaffData("Bola", position="associate")
        self.core = StaffData("Core", position="associate")
        self.loli = StaffData("loli", position="associate")

    def test_get_valid_staff_pass(self):
        for _ in range(11):
            self.motun.add_hours()
            self.bola.add_hours()
            self.loli.add_hours()

        valid_staff = get_valid_staff(StaffData.staff_members)

        assert self.core in valid_staff
        assert len(valid_staff) == 1

    def test_no_valid_get_staff(self):
        valid_staff = get_valid_staff([])
        assert valid_staff is None

    def teardown_method(self):
        del self.bola
        del self.core
        del self.loli
        del self.motun


# @pytest.mark.skip(reason="skip")
def test_get_other_staff():
    assignment = {
        "monday": {
            "shoes": {
                "morning": ["kolade"],
                "afternoon": ["kolade"],
                "evening": ["kolade"],
            },
            "ladies": {
                "morning": ["kunle", "motun"],
                "afternoon": ["kunle", "motun"],
                "evening": ["kunle", "motun"],
            },
            "home": {"morning": ["core"], "afternoon": ["core"], "evening": ["star"]},
        },
        "tuesday": {
            "shoes": {"morning": ["femi"], "afternoon": ["femi"], "evening": ["femi"]},
            "ladies": {
                "morning": ["lanre", "motun"],
                "afternoon": ["lanre", "motun"],
                "evening": ["lanre", "motun"],
            },
            "home": {
                "morning": ["kunle"],
                "afternoon": ["kunle"],
                "evening": ["kunle"],
            },
        },
        "wednesday": {
            "shoes": {"morning": ["bola"], "afternoon": ["bola"], "evening": ["bola"]},
            "ladies": {
                "morning": ["niran", "kolade"],
                "afternoon": ["niran", "kolade"],
                "evening": ["niran", "kolade"],
            },
            "home": {"morning": ["core"], "afternoon": ["core"], "evening": ["star"]},
        },
    }
    shoes = DepartmentData("shoes", 1)
    ladies = DepartmentData("ladies", max_staff=2, min_staff=2)

    res1 = ["kunle", "motun", "core", "star"]
    res2 = ["bola", "core", "star"]

    assert all(staff in get_other_staff(assignment, shoes, "monday") for staff in res1)
    assert all(
        staff in get_other_staff(assignment, ladies, "wednesday") for staff in res2
    )


class TestValidAssignments(BaseClass):
    # @pytest.mark.skip
    def test_invalid_assignment(self):
        assignment = {
            "monday": {
                self.shoes: {
                    "morning": [self.kolade, self.kunle],
                    "afternoon": [self.kolade],
                    "evening": [self.kolade],
                },
                self.ladies: {
                    "morning": [self.kunle, self.motun],
                    "afternoon": [self.kunle, self.motun],
                    "evening": [self.kunle, self.motun],
                },
                self.mens: {
                    "morning": [self.core],
                    "afternoon": [self.core],
                    "evening": [self.core],
                },
            },
        }

        validity = is_valid(
            assignment,
            self.shoes,
            "morning",
            self.kunle,
            "monday",
        )
        validity_two = is_valid(
            assignment,
            self.shoes,
            "morning",
            self.bola,
            "monday",
        )
        validity_three = is_valid(
            assignment,
            self.shoes,
            "morning",
            self.kolade,
            "monday",
        )
        assert validity is False
        assert validity_two is False
        assert validity_three is False

    def test_valid_assignment(self):
        assignment = {
            "monday": {
                self.shoes: {
                    "morning": [self.kolade],
                    "afternoon": [self.kolade],
                    "evening": [self.segun],
                },
                self.ladies: {
                    "morning": [self.kunle, self.motun],
                    "afternoon": [self.kunle, self.motun],
                    "evening": [self.halafia, self.daoud],
                },
                self.home: {
                    "morning": [self.core],
                    "afternoon": [self.core],
                    "evening": [self.core],
                },
            },
        }

        validity = is_valid(
            assignment,
            self.shoes,
            "morning",
            self.kolade,
            "monday",
        )
        assert validity is True


class TestUtilityFunctions(BaseClass):
    def setup_method(self, method):
        super().setup_method(method)

        self.assignment = {
            "monday": {
                self.shoes: {
                    "morning": [self.kolade, self.kunle],
                    "afternoon": [self.kolade],
                    "evening": [self.kolade],
                },
                self.ladies: {
                    "morning": [self.riri, self.motun],
                    "afternoon": [self.riri, self.motun],
                    "evening": [self.riri, self.motun],
                },
                self.mens: {
                    "morning": [self.core],
                    "afternoon": [self.core],
                    "evening": [self.core],
                },
            },
        }

    def test_get_staff_in_day(self):
        staff_set = get_staff_in_day(assignment=self.assignment, query_day="monday")
        assert self.kolade in staff_set
        assert self.kunle in staff_set
        assert self.motun in staff_set
        assert self.core in staff_set
        assert self.zara not in staff_set

    def test_get_staff_shift_count_in_day(self):
        kolade_shift_count = get_staff_shift_count_in_day(
            staff_member=self.kolade, assignment=self.assignment, query_day="monday"
        )
        kunle_shift_count = get_staff_shift_count_in_day(
            staff_member=self.kunle, assignment=self.assignment, query_day="monday"
        )
        assert kolade_shift_count == 3
        assert kunle_shift_count == 1


class TestUpdateSchedule:
    def setup_method(self, method):
        StaffData.reset()
        DepartmentData.reset()

        self.departments = DepartmentData.list_departments()
        self.staff_members = StaffData.list_staff_members()

        self.shoes = DepartmentData("shoes", 1)

        # self.bola = StaffData("Bola", "associate")
        self.shem = StaffData("shem", "associate")
        self.core = StaffData("core", "associate")
        self.loli = StaffData("loli", "associate")

    def teardown_method(self, method):
        StaffData.reset()
        DepartmentData.reset()

    # @pytest.mark.skip
    def test_update_remove_staff(self):
        self.bola = StaffData("Bola", "associate")

        res = scheduler(self.departments, self.staff_members)
        assigned_staff = get_assignment_staff(res)

        assert self.loli in assigned_staff

        StaffData.remove_staff(self.loli)  # removal here

        updated_res = update_schedule(res, self.departments, self.staff_members)
        assigned_staff = get_assignment_staff(updated_res["result"])

        assert self.loli not in assigned_staff

    # @pytest.mark.skip
    def test_update_add_staff(self):
        res = scheduler(self.departments, self.staff_members)

        self.bola = StaffData("Bola", "associate")
        StaffData.remove_staff(self.loli)

        updated_res = update_schedule(res, self.departments, self.staff_members)
        assigned_staff = get_assignment_staff(updated_res["result"])

        assert self.bola in assigned_staff

    def test_update_reduce_staff_hours(self):
        res = scheduler(self.departments, self.staff_members)
        self.core.contract_hours = 20

        updated_res = update_schedule(res, self.departments, self.staff_members)[
            "result"
        ]
        assigned_staff_occurence = [
            stf
            for day, val in updated_res.items()
            for department in val.values()
            for staff_list in department.values()
            for stf in staff_list
        ]

        assert (
            4 * assigned_staff_occurence.count(self.core)
        ) <= self.core.contract_hours

    def test_update_remove_department(self):
        res = scheduler(self.departments, self.staff_members)
        DepartmentData.remove_department(self.shoes)

        self.men = DepartmentData("men", 1)

        updated_res = update_schedule(
            res, self.departments, self.staff_members, print_assignment=True
        )["result"]

        assignment_departments = [
            dept for day, val in updated_res.items() for dept in val
        ]

        assert self.men in assignment_departments
        assert self.shoes not in assignment_departments

        # to finalize this, ypu have to remove contract hours for any deleted department

    def test_update_add_department(self):
        res = scheduler(self.departments, self.staff_members)

        self.men = DepartmentData("men", 1)

        self.segun = StaffData("segun", "associate")
        self.halafia = StaffData("halafia", "associate")

        updated_res = update_schedule(res, self.departments, self.staff_members)[
            "result"
        ]
        assignment_departments = get_assignment_departments(updated_res)
        assignment_staff = get_assignment_staff(updated_res)

        assert updated_res is not None
        assert all(dept in assignment_departments for dept in self.departments)
        assert all(stf in assignment_staff for stf in self.staff_members)

    def test_update_department_max_staff_reduce(self):
        self.shoes.max_staff = 2

        self.core.min_hours = 12
        # self.daoud = StaffData("daoud", "associate", min_hours=20)
        self.hasan = StaffData("hasan", "associate", min_hours=20)
        self.zara = StaffData("zara", "associate", min_hours=20)

        res = scheduler(self.departments, self.staff_members)

        self.shoes.max_staff = 1

        with pytest.raises(ScheduleError):
            update_schedule(res, self.departments, self.staff_members)[
                "result"
            ]

    # @pytest.mark.skip
    def test_update_min_staff_increase(self):

        res = scheduler(self.departments, self.staff_members)

        self.daoud = StaffData("daoud", "associate")
        self.hasan = StaffData("hasan", "associate")
        self.zara = StaffData("zara", "associate")

        self.shoes.min_staff = 2
        self.shoes.max_staff = 2

        updated_res = update_schedule(res, self.departments, self.staff_members)[
            "result"
        ]

        assert updated_res is not None

    # @pytest.mark.skip
    def test_update_change_staff_day_availability(self):
        res = scheduler(self.departments, self.staff_members)
        # print(res)

        # self.zara = StaffData("zara", "associate")
        self.loli.day_exclusion_list = ["monday", "friday"]
        self.core.day_exclusion_list = ["wednesday"]

        updated_res = update_schedule(
            assignment=res, departments=self.departments, staff=self.staff_members
        )["result"]

        # print('-'*10)
        # print('Test Update Change Staff Day Availability')
        # print(json.dumps(to_normal_dict(updated_res), indent=4))
        # print('-'*10)

        assert updated_res is not None

        assert self.loli not in get_staff_in_day(
            assignment=updated_res, query_day="monday"
        )
        assert self.loli not in get_staff_in_day(
            assignment=updated_res, query_day="friday"
        )
        assert self.core not in get_staff_in_day(
            assignment=updated_res, query_day="wednesday"
        )

    def test_update_change_staff_shift_availability(self):
        # self.zara = StaffData("zara", "associate")
        self.loli.shift_exclusion_list = ["morning"]
        res = scheduler(self.departments, self.staff_members)

        self.loli.shift_exclusion_list = ["evening"]
        # self.core.day_exclusion_list = ["wednesday"]

        updated_res = update_schedule(
            assignment=res, departments=self.departments, staff=self.staff_members
        )["result"]

        # print('-'*10)
        # print('Test Update Change Staff Day Availability')
        # print(json.dumps(to_normal_dict(updated_res), indent=4))
        # print('-'*10)

        assert updated_res is not None

        assert self.loli not in get_staff_in_shifts(
            assignment=updated_res, query_shift="evening"
        )

    def test_update_no_change(self):
        res = scheduler(self.departments, self.staff_members)

        updated_res = update_schedule(res, self.departments, self.staff_members)

        assert updated_res["result"] == res
        assert updated_res["regenerated"] is False
