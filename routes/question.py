from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.model import Question
from schemas.schema import QuestionCreate

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post("")
def create_question(q: QuestionCreate, db: Session = Depends(get_db)):
    question = Question(**q.dict())
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@router.get("")
def list_questions(db: Session = Depends(get_db)):
    return db.query(Question).order_by(Question.id.desc()).all()


@router.get("/{question_id}")
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.patch("/{question_id}")
def update_question(question_id: int, payload: QuestionCreate, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    for key, value in payload.dict().items():
        setattr(question, key, value)

    db.commit()
    db.refresh(question)
    return question


@router.delete("/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    db.delete(question)
    db.commit()
    return {"message": "Question deleted"}

