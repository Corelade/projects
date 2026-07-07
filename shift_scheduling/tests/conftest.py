from fastapi.testclient import TestClient
from api import app
from db import get_db_session
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.engine import URL
import os

db_username = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_TEST_NAME")

TEST_DB_URL = URL.create(
    drivername="mysql+pymysql",
    username='root',
    password='test_password',
    host="localhost",
    database='test_db',
)


test_engine = create_engine(TEST_DB_URL, echo=False)


def test_db_session():
    with Session(test_engine) as session:
        yield session

app.dependency_overrides[get_db_session] = test_db_session

client = TestClient(app)
