from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.model import Assignment, AssignmentQuestion, Question
from schemas.schema import AssignmentCreate, AssignmentQuestionCreate

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post("")
def create_assignment(data: AssignmentCreate, db: Session = Depends(get_db)):
    assignment = Assignment(**data.dict())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("")
def list_assignments(db: Session = Depends(get_db)):
    return db.query(Assignment).order_by(Assignment.id.desc()).all()


@router.get("/{assignment_id}")
def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@router.post("/add-question")
def add_question(data: AssignmentQuestionCreate, db: Session = Depends(get_db)):
    aq = AssignmentQuestion(**data.dict())
    db.add(aq)
    db.commit()
    db.refresh(aq)
    return aq


@router.get("/{assignment_id}/questions")
def get_assignment_questions(assignment_id: int, db: Session = Depends(get_db)):
    return (
        db.query(AssignmentQuestion)
        .filter(AssignmentQuestion.assignment_id == assignment_id)
        .order_by(AssignmentQuestion.position)
        .all()
    )