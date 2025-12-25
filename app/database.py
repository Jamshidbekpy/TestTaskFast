from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.settings import settings

DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI


if not DATABASE_URL:
    raise ValueError("SQLALCHEMY_DATABASE_URI is not set!")

engine = create_engine(str(DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass
