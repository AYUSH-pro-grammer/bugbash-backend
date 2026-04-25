from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.model import TestCase, Question
from schemas.schema import TestCaseCreate

router = APIRouter(prefix="/questions", tags=["testcases"])


@router.post("/{question_id}/testcases")
def add_testcase(question_id: int, tc: TestCaseCreate, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    testcase = TestCase(
        question_id=question_id,
        input=tc.input,
        expected_output=tc.expected_output,
        is_hidden=tc.is_hidden,
    )
    db.add(testcase)
    db.commit()
    db.refresh(testcase)
    return testcase


@router.get("/{question_id}/testcases")
def list_testcases(question_id: int, db: Session = Depends(get_db)):
    return db.query(TestCase).filter(TestCase.question_id == question_id).all()


@router.get("/{question_id}/testcases/{testcase_id}")
def get_testcase(question_id: int, testcase_id: int, db: Session = Depends(get_db)):
    testcase = (
        db.query(TestCase)
        .filter(TestCase.question_id == question_id, TestCase.id == testcase_id)
        .first()
    )
    if not testcase:
        raise HTTPException(status_code=404, detail="Test case not found")
    return testcase