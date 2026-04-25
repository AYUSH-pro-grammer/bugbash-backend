from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Playground(Base):
    __tablename__ = "playgrounds"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    title = Column(String, nullable=False, default="Untitled Playground")
    language = Column(String, nullable=False, default="python")
    code = Column(Text, nullable=False, default="")
    stdin = Column(Text, nullable=False, default="")

    last_output = Column(Text, nullable=True)
    last_error = Column(Text, nullable=True)

    is_public = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    creator = relationship("User", backref="playgrounds")