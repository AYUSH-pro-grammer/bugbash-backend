from pydantic import BaseModel
from typing import Optional




# -------- QUESTION --------
class QuestionCreate(BaseModel):
    title: str
    description: str
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    constraints: Optional[str] = None
    difficulty: Optional[str] = "easy"


# -------- TEST CASE --------
class TestCaseCreate(BaseModel):
    question_id: int
    input: str
    expected_output: str
    is_hidden: Optional[bool] = True


# -------- SUBMISSION --------
class SubmissionCreate(BaseModel):
    user_id: int
    question_id: int
    code: str
    language: str