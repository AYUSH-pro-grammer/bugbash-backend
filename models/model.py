from datetime import datetime
from database import Base

from sqlalchemy import Column, Integer, String, Text

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    input_format = Column(Text)
    output_format = Column(Text)
    constraints = Column(Text)
    difficulty = Column(String)



from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import relationship

class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    input = Column(Text)
    expected_output = Column(Text)
    is_hidden = Column(Boolean, default=True)


from sqlalchemy import ForeignKey

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

class LatestSubmission(Base):
    __tablename__ = "latest_submissions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    question_id = Column(Integer)
    submission_id = Column(Integer)

