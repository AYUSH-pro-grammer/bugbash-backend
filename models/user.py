from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    email = Column(String, unique=True, nullable=True)

    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)


    profile_image = Column(String, nullable=True, default="default_profile.png")
    bio = Column(String, nullable=True, default="")
    is_active = Column(Boolean, default=True)



