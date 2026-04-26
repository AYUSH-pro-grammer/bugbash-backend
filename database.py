from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os


SQLALCHEMY_DATABASE_URL = "postgresql://avnadmin:AVNS_J6JOHXHbT2cFtb2vY7A@pg-2a5cbd6-my-7dc7.c.aivencloud.com:26166/defaultdb?sslmode=require"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,          # max persistent connections
    max_overflow=10,      # extra temporary connections
    pool_timeout=30,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

