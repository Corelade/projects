import pytest
from tests.conftest import client, test_engine
from sqlmodel import SQLModel, Session
from models import User, Department
from auth.auth import create_access_token
from datetime import timedelta
from fastapi import status

# TODO
"""
    - Write tests for Staff CRUD
"""


def create_user_token_header(username, db) -> tuple[User, str, dict]:
    user = User(username=username, password="hashed-password")
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"user": user.username}, timedelta(minutes=15))

    headers = {"Authorization": f"Bearer {token}"}
    return user, token, headers


class BaseTestClass:
    def setup_method(self):
        SQLModel.metadata.create_all(test_engine)
        self.db = Session(test_engine)
        self.setup_user()
        self.setup_departments()
        self.setup_staff()

        self.shoes = {
            "name": "shoes",
            "min_staff": 1,
            "max_staff": 1,
        }

        self.ladies = {"name": "ladies", "min_staff": 3, "max_staff": 7}

        self.invalid_headers = {
            "Authorization": f"Bearer {"randomtoken72gubewhr3qgbr3yog"}"
        }

    def setup_user(self):
        self.user, self.token, self.headers = create_user_token_header(
            "user_one", self.db
        )

        self.user_two, self.token_two, self.headers_two = create_user_token_header(
            "user_two", self.db
        )

    def setup_departments(self):
        self.shoes = {
            "name": "shoes",
            "min_staff": 1,
            "max_staff": 1,
        }

        self.ladies = {
            "name": "ladies",
            "min_staff": 3,
            "max_staff": 7,
        }

    def setup_staff(self):
        self.staff_one = {
            "first_name": "stf1",
            "last_name": "one",
            "position": "associate",
            "contract_hours": 40,
            "day_exclusions": [],
            "shift_exclusions": [],
            "email": "stf_one@shiftpro.com",
            "min_hours": 8,
        }

        self.staff_two = {
            "first_name": "stf2",
            "last_name": "two",
            "position": "associate",
            "contract_hours": 40,
            "day_exclusions": [],
            "shift_exclusions": [],
            "email": "stf_two@shiftpro.com",
            "min_hours": 8,
        }

        self.staff_three = {
            "first_name": "stf3",
            "last_name": "three",
            "position": "associate",
            "contract_hours": 40,
            "day_exclusions": [],
            "shift_exclusions": [],
            "email": "stf_three@shiftpro.com",
            "min_hours": 8,
        }

    def teardown_method(self):
        del self.shoes
        self.db.close()
        SQLModel.metadata.drop_all(test_engine)


# class TestCreateStaff(BaseTestClass):
#     def setup_method(self):
#         super().setup_method()

#         self.data = {
#             "first_name": "kol",
#             "last_name": "Ade",
#             "position": "associate",
#             "contract_hours": 40,
#             "day_exclusions": [],
#             "shift_exclusions": [],
#             "email": "invalid-email",
#             "min_hours": 8,
#         }

#     def teardown_method(self):
#         super().teardown_method()
#         del self.data

#     # @pytest.mark.skip
#     def test_create_staff_invalid_email(self):
#         response = client.post("/create-staff", json=self.data)
#         assert response.status_code == 422

#     # @pytest.mark.xfail
#     def test_create_staff_success(self):
#         self.data["first_name"] = "kun"
#         self.data["email"] = "he@me.com"
#         response = client.post("/create-staff", json=self.data)
#         assert response.status_code == 200

#     # @pytest.mark.xfail
#     def test_create_staff_null_fail(self):
#         self.data["first_name"] = None
#         response = client.post("/create-staff", json=self.data)
#         assert response.status_code == 422

#     # @pytest.mark.xfail
#     def test_invalid_json_body(self):
#         "Returns an error if one of the contents in self.data is missing"
#         self.data.pop("last_name")
#         response = client.post("/create-staff", json=self.data)
#         assert response.status_code == 422

#     # @pytest.mark.xfail
#     def test_same_email_fail(self):
#         self.kun = {
#             "first_name": "kun",
#             "last_name": "Ade",
#             "position": "associate",
#             "contract_hours": 40,
#             "day_exclusions": [],
#             "shift_exclusions": [],
#             "email": "kun@me.com",
#             "min_hours": 8,
#         }

#         client.post("/create-staff", json=self.kun)

#         self.kol = {
#             "first_name": "kol",
#             "last_name": "Ade",
#             "position": "associate",
#             "contract_hours": 40,
#             "day_exclusions": [],
#             "shift_exclusions": [],
#             "email": "kun@me.com",
#             "min_hours": 8,
#         }

#         response = client.post("/create-staff", json=self.kun)
#         print(response.json())
#         assert response.status_code == 400


# class TestListStaff(BaseTestClass):
#     def setup_method(self):
#         super().setup_method()

#         self.kun = {
#             "first_name": "kun",
#             "last_name": "Ade",
#             "position": "associate",
#             "contract_hours": "40",
#             "day_exclusions": [],
#             "shift_exclusions": [],
#             "email": "kun@me.com",
#             "min_hours": 8,
#         }

#         self.kol = {
#             "first_name": "kol",
#             "last_name": "Ade",
#             "position": "associate",
#             "contract_hours": "40",
#             "day_exclusions": [],
#             "shift_exclusions": [],
#             "email": "kol@me.com",
#             "min_hours": 8,
#         }

#     def teardown_method(self):
#         super().teardown_method()
#         del self.kol
#         del self.kun

#     # @pytest.mark.xfail
#     def test_staff_list(self):
#         client.post("/create-staff", json=self.kol)
#         client.post("/create-staff", json=self.kun)

#         response = client.get("/list_staff")
#         staff_list = [s["first_name"] for s in response.json()]
#         assert response.status_code == 200
#         assert all(name in staff_list for name in ["kol", "kun"])


class TestCreateDepartment(BaseTestClass):
    def setup_method(self):
        super().setup_method()

    def teardown_method(self):
        super().teardown_method()

    # @pytest.mark.skip
    def test_create_department_success(self):
        response = client.post(
            "/create_department", json=self.shoes, headers=self.headers
        )
        assert response.status_code == status.HTTP_201_CREATED

    # @pytest.mark.skip
    def test_create_duplicate_department_name_same_user(self):
        "This test should fail becuase two departments from same user can not have same name"
        client.post("/create_department", json=self.shoes, headers=self.headers)
        self.shoes_duplicate = {
            "name": "shoes",
            "min_staff": 1,
            "max_staff": 1,
        }
        response_two = client.post(
            "/create_department", json=self.shoes_duplicate, headers=self.headers
        )

        assert response_two.status_code == status.HTTP_409_CONFLICT

    def test_create_duplicate_department_name_different_user(self):
        "This test should pass because two departments from different user can have same name"
        client.post("/create_department", json=self.shoes, headers=self.headers)
        self.shoes_duplicate = {
            "name": "shoes",
            "min_staff": 1,
            "max_staff": 1,
        }

        response_two = client.post(
            "/create_department", json=self.shoes_duplicate, headers=self.headers_two
        )

        assert response_two.status_code == status.HTTP_201_CREATED

    # @pytest.mark.skip
    def test_missing_field_pass(self):
        "This tests for absence of missing field (excluding name) and should pass"
        self.shoes.pop("min_staff")
        response = client.post(
            "/create_department", json=self.shoes, headers=self.headers
        )
        assert response.status_code == status.HTTP_201_CREATED

    # @pytest.mark.skip
    def test_missing_field_fail(self):
        self.shoes.pop("name")
        response = client.post(
            "/create_department", json=self.shoes, headers=self.headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestListDepartment(BaseTestClass):
    def setup_method(self):
        super().setup_method()

    def test_list_departments(self):
        client.post("/create_department", json=self.shoes, headers=self.headers)
        client.post("/create_department", json=self.ladies, headers=self.headers)

        user_one_list = client.get("/departments", headers=self.headers)
        user_two_list = client.get("/departments", headers=self.headers_two)

        assert user_one_list.status_code == status.HTTP_200_OK
        assert user_two_list.status_code == status.HTTP_200_OK
        assert len(user_one_list.json()) == 2
        assert len(user_two_list.json()) == 0


class TestUpdateDepartment(BaseTestClass):
    def test_update_department_success(self):
        response = client.post(
            "/create_department", json=self.shoes, headers=self.headers
        )
        response_ladies = client.post(
            "/create_department", json=self.ladies, headers=self.headers
        )
        shoes_id = response.json()["id"]
        ladies_id = response_ladies.json()["id"]

        self.shoes = {"name": "shoes", "min_staff": 1, "max_staff": 2}
        self.ladies = {"min_staff": 4}

        response = client.patch(
            f"/departments/{shoes_id}", json=self.shoes, headers=self.headers
        )
        response_ladies = client.patch(
            f"/departments/{ladies_id}", json=self.ladies, headers=self.headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["max_staff"] == 2

        assert response_ladies.status_code == status.HTTP_200_OK
        assert response_ladies.json()["min_staff"] == 4
        assert response_ladies.json()["max_staff"] == 7

    def test_update_department_fail(self):
        # Invalid department
        json = {"name": "mens"}
        response = client.patch("/departments/5", json=json, headers=self.headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        response = client.post(
            "/create_department", json=self.shoes, headers=self.headers
        )
        id = response.json()["id"]

        # invalid min_staff / max_staff
        json = {"min_staff": 0, "max_staff": 1}
        resp = client.patch(f"/departments/{id}", json=json, headers=self.headers)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        # min_staff > max_staff
        json = {"min_staff": 2, "max_staff": 1}
        resp = client.patch(f"/departments/{id}", json=json, headers=self.headers)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        # Not authenticated

        json = {"min_staff": 1, "max_staff": 3}
        resp = client.patch(
            f"/departments/{id}", json=json, headers=self.invalid_headers
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteDepartment(BaseTestClass):
    def test_delete_department(self):
        resp = client.post("/create_department", json=self.shoes, headers=self.headers)
        id = resp.json()["id"]

        # department not found
        del_resp = client.delete("/departments/5", headers=self.headers)
        assert del_resp.status_code == status.HTTP_404_NOT_FOUND

        # unauthorised
        del_resp = client.delete(f"/departments/{id}", headers=self.headers_two)
        assert del_resp.status_code == status.HTTP_403_FORBIDDEN

        # unauthenticated
        del_resp = client.delete(f"/departments/{id}", headers=self.invalid_headers)
        assert del_resp.status_code == status.HTTP_401_UNAUTHORIZED

        # deletion success
        del_resp = client.delete(f"/departments/{id}", headers=self.headers)
        assert del_resp.status_code == status.HTTP_200_OK


class TestGenerateSchedule(BaseTestClass):
    def setup_method(self):
        super().setup_method()

        self.weekRequest = {"week_start": "2026-08-31"}

    def setup_departments(self):
        super().setup_departments()

        self.d1 = client.post(
            "/create_department", json=self.shoes, headers=self.headers
        )

    def setup_staff(self):
        super().setup_staff()

        client.post("/create_staff", json=self.staff_one, headers=self.headers)
        client.post("/create_staff", json=self.staff_two, headers=self.headers)
        client.post("/create_staff", json=self.staff_three, headers=self.headers)

    def test_generate_schedule(self):

        generated_schedule = client.post(
            "/schedule/generate", json=self.weekRequest, headers=self.headers
        )

        assert generated_schedule.json()["schedule"] != {}

        # get week schedule and should be equal to schedule generated

        week_schedule = client.get(
            "/schedule", params=self.weekRequest, headers=self.headers
        )

        assert week_schedule.json() == generated_schedule.json()

    def test_no_schedule_different_user(self):
        "A user creates a schedule and another user can not view it"
        client.post("/schedule/generate", json=self.weekRequest, headers=self.headers)

        week_schedule = client.get(
            "/schedule", params=self.weekRequest, headers=self.headers_two
        )

        assert week_schedule.json()["schedule"] == {}

    def test_no_department_present(self):
        client.delete(f"/departments/{self.d1.json()['id']}", headers=self.headers)

        resp = client.post(
            "/schedule/generate", json=self.weekRequest, headers=self.headers
        )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_generate_schedule_fail(self):
        '1 dept - 1 Staff -> Fail'
        
        client.post("/create_department", json=self.shoes, headers=self.headers_two)

        self.staff_one = {
            "first_name": "stf1",
            "last_name": "one",
            "position": "associate",
            "contract_hours": 40,
            "day_exclusions": [],
            "shift_exclusions": [],
            "email": "stf_one_2@shiftpro.com",
            "min_hours": 8,
        }

        client.post("/create_staff", json=self.staff_one, headers=self.headers_two)

        generated_schedule = client.post(
            "/schedule/generate", json=self.weekRequest, headers=self.headers_two
        )

        generated_schedule.status_code == status.HTTP_400_BAD_REQUEST
