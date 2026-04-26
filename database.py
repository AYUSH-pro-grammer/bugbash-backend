from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os


SQLALCHEMY_DATABASE_URL = "postgresql://avnadmin:AVNS_qDNWH3GpsnK69lyAGWJ@pg-40f0ce4-hackerpro1428-fe94.c.aivencloud.com:16550/defaultdb?sslmode=require"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,           # small pool
    max_overflow=2,        # limit burst
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

