import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Credentials come from the environment; the default is for local development only.
DATABASE_URL = os.getenv(
    "DATABASE_URL", "mysql+pymysql://root:admin1234@localhost:3306/taskboard"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    with SessionLocal() as db:
        yield db
