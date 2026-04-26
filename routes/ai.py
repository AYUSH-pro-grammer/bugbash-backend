import json
from sqlalchemy.orm import Session
from models.model import Question
from models.model import TestCase
from models.model import Assignment, AssignmentQuestion


from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from service.aiask import ask


def generate_and_store_content(ai_response: str, db: Session):
    try:
        data = json.loads(ai_response)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON from AI")

    created_questions = []

    try:
        # 1. Create Questions
        for q in data["questions"]:
            question = Question(
                title=q["title"],
                description=q["description"],
                difficulty=q["difficulty"]
            )
            db.add(question)
            db.flush()

            # 2. Create Testcases
            for tc in q["testcases"]:
                testcase = TestCase(
                    question_id=question.id,
                    input=tc["input"],
                    expected_output=tc["output"]  # ✅ FIXED
                )
                db.add(testcase)

            created_questions.append(question)

        # 3. Create Assignment
        assignment_data = data["assignment"]

        assignment = Assignment(
            title=assignment_data["title"],
            syllabus=assignment_data["description"]  # ✅ match your schema
        )
        db.add(assignment)
        db.flush()

        # 4. Link Questions (IMPORTANT FIX)
        for idx, q in enumerate(created_questions):
            link = AssignmentQuestion(
                assignment_id=assignment.id,
                question_id=q.id,
                position=idx + 1,
                marks=10  # default marks
            )
            db.add(link)

        db.commit()

        return {
            "assignment_id": assignment.id,
            "question_ids": [q.id for q in created_questions]
        }

    except Exception as e:
        db.rollback()
        raise e

router = APIRouter()


@router.post("/create/assignment")
def create_assignment(prompt: str, db: Session = Depends(get_db)):
    try:
        # 1. Call AI
        ai_response = ask(prompt)

        # 2. Store in DB
        result = generate_and_store_content(ai_response, db)

        return {
            "status": "success",
            "data": result
        }

    except ValueError as e:
        # JSON error from AI
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))