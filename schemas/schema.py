from pydantic import BaseModel
from typing import Optional


class QuestionCreate(BaseModel):
    title: str
    description: str

    input_format: Optional[str] = None
    output_format: Optional[str] = None
    constraints: Optional[str] = None

    example: Optional[str] = None
    explanation: Optional[str] = None

    difficulty: Optional[str] = "easy"
    tags: Optional[str] = None


class QuestionOut(QuestionCreate):
    id: int

    class Config:
        from_attributes = True




class TestCaseCreate(BaseModel):
    input: str
    expected_output: str
    is_hidden: Optional[bool] = True


class TestCaseOut(TestCaseCreate):
    id: int

    class Config:
        from_attributes = True


class SubmissionCreate(BaseModel):
    question_id: int
    code: str
    language: str


class SubmissionOut(BaseModel):
    id: int
    user_id: int
    question_id: int

    status: str
    total_passed: int
    total_cases: int

    class Config:
        from_attributes = True

class SubmissionResultOut(BaseModel):
    test_case_id: int
    status: str
    output: str
    expected_output: str

    execution_time: Optional[str] = None
    memory: Optional[str] = None

    class Config:
        from_attributes = True


class AssignmentCreate(BaseModel):
    title: str
    syllabus: Optional[str] = None

    start_time: Optional[str] = None
    end_time: Optional[str] = None


class AssignmentQuestionCreate(BaseModel):
    assignment_id: int
    question_id: int
    position: int
    marks: int

