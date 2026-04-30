import pytest
from ..app import is_feasibile, get_other_staff
from ..classes import Staff, Department


class BaseClass:
    """
    Class to setup test variables
    """

    def setup_method(self):
        self.shoes = Department("shoes", 1)
        self.mens = Department("men", 1)
        self.ladies = Department("ladies", max_num_staff=2, min_num_staff=2)

        self.kolade = Staff("Kolade", "associate", shift_exclusion_list=["evening"])
        self.kunle = Staff("Kunle", "associate", day_exclusion_list=["tuesday"])
        self.motun = Staff("Motun", "associate", shift_exclusion_list=["evening"])
        self.bola = Staff("Bola", "associate")
        self.core = Staff("Core", "associate")
        self.loli = Staff("loli", "associate")
        self.shem = Staff("shem", "associate")
        self.riri = Staff("riri", "associate")
        self.segun = Staff("segun", "associate")
        self.halafia = Staff("halafia", "associate")
        self.daoud = Staff("daoud", "associate")
        self.hasan = Staff("hasan", "associate")
        self.zara = Staff("zara", "associate")


class TestCheckFeasibility(BaseClass):
    """
    This class checks whether the current staff and shifts will lead to an assignment
    """

    # @pytest.mark.skip(reason='tried')
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
            is_feasibile([self.mens], [self.riri, self.halafia, self.segun, self.daoud])
            is False
        )
        assert is_feasibile([self.shoes, self.ladies], [self.bola, self.core]) is False
        # assertion for controlling max_hours as a staff shouldnt work more than 35 hours in a week
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

    # @pytest.mark.skip(reason='tried')
    def test_feasibility_is_true(self):
        """These checks should return True"""
        assert is_feasibile([self.mens], [self.bola], ["monday", "tuesday"]) is True
        assert is_feasibile([self.mens], [self.bola, self.core]) is True
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

# @pytest.mark.skip(reason='tried')
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
    shoes = Department("shoes", 1)
    ladies = Department("ladies", max_num_staff=2, min_num_staff=2)

    res1 = ["kunle", "motun", "core", "star"]
    res2 = ["bola", "core", "star"]

    assert all(staff in get_other_staff(assignment, shoes, "monday") for staff in res1)
    assert all(
        staff in get_other_staff(assignment, ladies, "wednesday") for staff in res2
    )
