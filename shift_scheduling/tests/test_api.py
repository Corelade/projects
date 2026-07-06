import pytest
from tests.conftest import client, test_engine
from sqlmodel import SQLModel


class BaseTestClass:
    def setup_method(self):
        SQLModel.metadata.drop_all(test_engine)
        SQLModel.metadata.create_all(test_engine)

    def teardown_method(self):
        SQLModel.metadata.drop_all(test_engine)


class TestCreateStaff(BaseTestClass):
    def setup_method(self):
        super().setup_method()

        self.data = {
            "first_name": "kol",
            "last_name": "Ade",
            "position": "associate",
            "contract_hours": "40",
            "day_exclusions": [],
            "shift_exclusions": [],
            "email": "invalid-email",
        }

    def teardown_method(self):
        super().teardown_method()
        del self.data

    def test_create_staff_invalid_email(self):
        response = client.post("/create-staff", json=self.data)
        assert response.status_code == 422

    def test_create_staff_success(self):
        self.data["first_name"] = "kun"
        self.data["email"] = "he@me.com"
        response = client.post("/create-staff", json=self.data)
        print(response.json())
        assert response.status_code == 200

    def test_create_staff_null_fail(self):
        self.data["first_name"] = None
        response = client.post("/create-staff", json=self.data)
        assert response.status_code == 422

    def test_invalid_json_body(self):
        "Returns an error if one of the contents in self.data is missing"
        self.data.pop("last_name")
        response = client.post("/create-staff", json=self.data)
        assert response.status_code == 422

    def test_same_email_fail(self):
        self.kun = {
            "first_name": "kun",
            "last_name": "Ade",
            "position": "associate",
            "contract_hours": "40",
            "day_exclusions": [],
            "shift_exclusions": [],
            "email": "kun@me.com",
        }

        client.post("/create-staff", json=self.kun)

        self.kol = {
            "first_name": "kol",
            "last_name": "Ade",
            "position": "associate",
            "contract_hours": "40",
            "day_exclusions": [],
            "shift_exclusions": [],
            "email": "kun@me.com",
        }

        response = client.post("/create-staff", json=self.kun)
        assert response.status_code == 400


class TestListStaff(BaseTestClass):
    def setup_method(self):
        super().setup_method()

        self.kun = {
            "first_name": "kun",
            "last_name": "Ade",
            "position": "associate",
            "contract_hours": "40",
            "day_exclusions": [],
            "shift_exclusions": [],
            "email": "kun@me.com",
        }

        self.kol = {
            "first_name": "kol",
            "last_name": "Ade",
            "position": "associate",
            "contract_hours": "40",
            "day_exclusions": [],
            "shift_exclusions": [],
            "email": "kol@me.com",
        }

    def teardown_method(self):
        super().teardown_method()
        del self.kol
        del self.kun

    def test_staff_list(self):
        client.post("/create-staff", json=self.kol)
        client.post("/create-staff", json=self.kun)

        response = client.get("/list_staff")
        staff_list = [s["first_name"] for s in response.json()]
        assert response.status_code == 200
        assert all(name in staff_list for name in ["kol", "kun"])


class TestCreateDepartment(BaseTestClass):
    def setup_method(self):
        super().setup_method()

        self.shoes = {"name": "shoes", "min_staff": 1, "max_staff": 1}

    def teardown_method(self):
        super().teardown_method()

        del self.shoes

    def test_create_department_success(self):
        response = client.post("/create_department", json=self.shoes)
        assert response.status_code == 200

    def test_create_duplicate_name(self):
        "This test should fail becuase two departments can not have same name"
        client.post("/create_department", json=self.shoes)
        self.shoes_duplicate = {"name": "shoes", "min_staff": 1, "max_staff": 1}
        response = client.post("/create_department", json=self.shoes_duplicate)
        assert response.status_code == 400
        
    def test_missing_field_pass(self):
        "This tests for absence of missing field (excluding name) and should pass "
        self.shoes.pop("min_staff")
        response = client.post("/create_department", json=self.shoes)
        assert response.status_code == 200
        
    def test_misisng_field_fail(self):
        self.shoes.pop("name")
        response = client.post("/create_department", json=self.shoes)
        assert response.status_code == 422