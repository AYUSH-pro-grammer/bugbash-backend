# schemas/assignment.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class AssignmentCreate(BaseModel):
    title: str
    syllabus: Optional[str] = None
    start_time: datetime
    end_time: datetime


class AssignmentQuestionAdd(BaseModel):
    question_id: int
    position: int
    marks: int


class AssignmentResponse(BaseModel):
    id: int
    title: str
    syllabus: Optional[str]
    start_time: datetime
    end_time: datetime

    class Config:
        from_attributes = True