from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session
from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine import URL

load_dotenv()
import os

db_username = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")


# sqlite_file_name = "database.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"

# connect_args = {"check_same_thread": False}
# engine = create_engine(url=sqlite_url, connect_args=connect_args)

DB_URL = URL.create(
    drivername="mysql+pymysql",
    username=db_username,
    password=db_password,
    host="localhost",
    database=db_name,
)

# DB_URL = f"mysql+mysqlconnector://{db_username}:{db_password}@localhost/{db_name}"
engine = create_engine(DB_URL, echo=False)

Base = declarative_base()


def get_db_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


SessionDep = Annotated[Session, Depends(get_db_session)]
