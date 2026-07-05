import pytest
from ..app import is_feasibile, get_other_staff, get_valid_staff, is_valid
from ..classes import StaffData, DepartmentData


class BaseClass:
    """
    Class to setup test variables
    """

    def setup_method(self, method):
        DepartmentData.departments.clear()
        StaffData.staff_members.clear()
        DepartmentData.next_id = 1
        StaffData.next_id = 1

        self.shoes = DepartmentData("shoes", 1)
        self.mens = DepartmentData("men", 1)
        self.ladies = DepartmentData("ladies", max_num_staff=2, min_num_staff=2)

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
        StaffData.staff_members.clear()
        DepartmentData.departments.clear()


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

        with pytest.raises(ValueError):
            assert self.k1 == self.shoes


class TestDepartmentData:
    pass


class TestCheckFeasibility(BaseClass):
    """
    This class checks whether the current staff and shifts will lead to an assignment
    """

    # @pytest.mark.skip(reason="tried")
    def test_feasibility_is_false(self):
        """All of the checks here should return False"""
        assert is_feasibile([], []) is False  # if no staff nor dept
        assert (
            is_feasibile([self.shoes], [self.kolade, self.kunle]) is False
        )  # Kunle not available tuesday, kolade not available tuesday evening
        assert (
            is_feasibile([self.shoes], [self.kunle]) is False
        )  # Kunle not available tuesday
        assert (
            is_feasibile([self.shoes], [self.kolade]) is False
        )  # kolade not available during evenings which leave empty unfilled space
        assert (
            is_feasibile([self.shoes, self.mens], [self.kolade]) is False
        )  # num of department_staff required is less than staff available
        assert (
            is_feasibile([self.shoes], [self.kolade, self.motun]) is False
        )  # both staff not available evenings and will leave empty space
        assert (
            is_feasibile(
                [self.mens],
                [self.riri, self.halafia, self.segun, self.daoud],
                DAY_OF_WEEK=["monday"],
            )
            is False
        )  # too many staff available
        assert is_feasibile([self.shoes, self.ladies], [self.bola, self.core]) is False
        # assertion for controlling max_hours as a staff shouldnt work more than contract hours in a week
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

    # @pytest.mark.skip(reason="tried")
    def test_feasibility_is_true(self):
        """These checks should return True"""
        assert is_feasibile([self.mens], [self.bola], ["monday", "tuesday"]) is True
        assert is_feasibile([self.mens], [self.bola, self.core]) is False
        assert is_feasibile([self.mens], [self.bola, self.core, self.kunle]) is True
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
        self.motun = StaffData("motun", "associate")
        self.bola = StaffData("Bola", "associate")
        self.core = StaffData("Core", "associate")
        self.loli = StaffData("loli", "associate")

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
    ladies = DepartmentData("ladies", max_num_staff=2, min_num_staff=2)

    res1 = ["kunle", "motun", "core", "star"]
    res2 = ["bola", "core", "star"]

    assert all(staff in get_other_staff(assignment, shoes, "monday") for staff in res1)
    assert all(
        staff in get_other_staff(assignment, ladies, "wednesday") for staff in res2
    )


class TestValidAssignments(BaseClass):
    def test_invalid_assignment(self):
        assignment = {
            "monday": {
                "shoes": {
                    "morning": ["kolade", "kunle"],
                    "afternoon": ["kolade"],
                    "evening": ["kolade"],
                },
                "ladies": {
                    "morning": ["kunle", "motun"],
                    "afternoon": ["kunle", "motun"],
                    "evening": ["kunle", "motun"],
                },
                "home": {
                    "morning": ["core"],
                    "afternoon": ["core"],
                    "evening": ["star"],
                },
            },
        }

        validity = is_valid(
            assignment, self.shoes, "morning", self.kunle, "monday", use_id=False
        )
        validity_two = is_valid(
            assignment, self.shoes, "morning", self.bola, "monday", use_id=False
        )
        validity_three = is_valid(
            assignment, self.shoes, "morning", self.kolade, "monday", use_id=False
        )
        assert validity is False
        assert validity_two is False
        assert validity_three is False

    def test_valid_assignment(self):
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
                "home": {
                    "morning": ["core"],
                    "afternoon": ["core"],
                    "evening": ["star"],
                },
            },
        }

        validity = is_valid(
            assignment, self.shoes, "morning", self.kolade, "monday", use_id=False
        )
        assert validity is False
