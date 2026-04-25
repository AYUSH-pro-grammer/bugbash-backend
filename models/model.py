from datetime import datetime
from database import Base

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship



class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String)
    description = Column(Text)

    input_format = Column(Text)
    output_format = Column(Text)
    constraints = Column(Text)

    example = Column(Text)
    explanation = Column(Text)

    difficulty = Column(String)

    tags = Column(Text)


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"))

    input = Column(Text)
    expected_output = Column(Text)

    is_hidden = Column(Boolean, default=True)



class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))

    code = Column(Text)
    language = Column(String)

    status = Column(String)
    total_passed = Column(Integer)
    total_cases = Column(Integer)



class SubmissionResult(Base):
    __tablename__ = "submission_results"

    id = Column(Integer, primary_key=True)

    submission_id = Column(Integer, ForeignKey("submissions.id"))
    test_case_id = Column(Integer, ForeignKey("test_cases.id"))

    status = Column(String)
    output = Column(Text)
    expected_output = Column(Text)

    execution_time = Column(String)
    memory = Column(String)


class LatestSubmission(Base):
    __tablename__ = "latest_submissions"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    submission_id = Column(Integer, ForeignKey("submissions.id"))


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True)

    title = Column(String)
    syllabus = Column(Text)

    start_time = Column(DateTime)
    end_time = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)


class AssignmentQuestion(Base):
    __tablename__ = "assignment_questions"

    id = Column(Integer, primary_key=True)

    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))

    position = Column(Integer)
    marks = Column(Integer)