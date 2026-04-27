from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.model import Assignment, AssignmentQuestion, Question
from schemas.assignment import AssignmentCreate, AssignmentQuestionAdd
from deps.auth import get_current_user

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post("")
def create_assignment(
    data: AssignmentCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    

    assignment = Assignment(
        user_id=user_id,
        title=data.title,
        syllabus=data.syllabus,
        start_time=data.start_time,
        end_time=data.end_time
    )



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

    questions = (
        db.query(AssignmentQuestion, Question)
        .join(Question, AssignmentQuestion.question_id == Question.id)
        .filter(AssignmentQuestion.assignment_id == assignment_id)
        .order_by(AssignmentQuestion.position)
        .all()
    )

    return {
        "assignment": assignment,
        "questions": [
            {
                "id": q.id,
                "title": q.title,
                "difficulty": q.difficulty,
                "marks": aq.marks,
                "position": aq.position
            }
            for aq, q in questions
        ]
    }


@router.get("/my/assignment/list")
def my_assignment_list(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assignment_data = db.query(Assignment).filter(Assignment.user_id == user_id).all()
    
    return assignment_data

@router.post("/{assignment_id}/questions")
def add_question_to_assignment(
    assignment_id: int,
    data: AssignmentQuestionAdd,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if assignment.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    question = db.query(Question).filter(Question.id == data.question_id).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    existing = db.query(AssignmentQuestion).filter(
        AssignmentQuestion.assignment_id == assignment_id,
        AssignmentQuestion.question_id == data.question_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Question already added")

    aq = AssignmentQuestion(
        assignment_id=assignment_id,
        question_id=data.question_id,
        position=data.position,
        marks=data.marks
    )

    db.add(aq)
    db.commit()
    db.refresh(aq)

    return {"message": "Question added to assignment"}


@router.delete("/{assignment_id}/questions/{question_id}")
def remove_question_from_assignment(
    assignment_id: int,
    question_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if assignment.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    aq = db.query(AssignmentQuestion).filter(
        AssignmentQuestion.assignment_id == assignment_id,
        AssignmentQuestion.question_id == question_id
    ).first()

    if not aq:
        raise HTTPException(status_code=404, detail="Mapping not found")

    db.delete(aq)
    db.commit()

    return {"message": "Question removed"}





@router.delete("/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if assignment.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    # 🔥 DELETE CHILD FIRST
    db.query(AssignmentQuestion).filter(
        AssignmentQuestion.assignment_id == assignment_id
    ).delete()

    db.delete(assignment)
    db.commit()

    return {"message": "Assignment deleted"}