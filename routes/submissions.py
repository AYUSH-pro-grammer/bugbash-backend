from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.model import Submission, TestCase
from schemas.schema import SubmissionCreate
from service.execute import run_code

router = APIRouter(tags=["submissions"])



from deps.auth import get_current_user
from models.model import Submission, TestCase, SubmissionResult, LatestSubmission


@router.post("/submit")
def submit_code(
    data: SubmissionCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    testcases = db.query(TestCase).filter(TestCase.question_id == data.question_id).all()

    passed = 0
    total = len(testcases)
    results = []

    submission = Submission(
        user_id=user_id,
        question_id=data.question_id,
        code=data.code,
        language=data.language,
        status="Pending",
        total_passed=0,
        total_cases=total,
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    for tc in testcases:
        result = run_code(data.code, tc.input, data.language)

        output = (result.get("output") or "").strip()
        expected = (tc.expected_output or "").strip()
        error = (result.get("error") or "").strip()

        ok = output == expected and not error
        if ok:
            passed += 1

        res_obj = SubmissionResult(
            submission_id=submission.id,
            test_case_id=tc.id,
            status="Accepted" if ok else "Wrong Answer",
            output=output,
            expected_output=expected,
            execution_time=result.get("time"),
            memory=result.get("memory"),
        )

        db.add(res_obj)

        results.append({
            "testcase_id": tc.id,
            "input": tc.input if not tc.is_hidden else "Hidden",
            "expected_output": tc.expected_output if not tc.is_hidden else "Hidden",
            "output": output if not tc.is_hidden else "Hidden",
            "status": "Accepted" if ok else "Wrong Answer",
            "error": error,
        })

    submission.status = "Accepted" if passed == total else "Wrong Answer"
    submission.total_passed = passed

    # 🔥 update latest submission
    latest = db.query(LatestSubmission).filter(
        LatestSubmission.user_id == user_id,
        LatestSubmission.question_id == data.question_id
    ).first()

    if latest:
        latest.submission_id = submission.id
    else:
        db.add(LatestSubmission(
            user_id=user_id,
            question_id=data.question_id,
            submission_id=submission.id
        ))

    db.commit()

    return {
        "submission": submission,
        "results": results,
    }

    
@router.get("/questions/{question_id}/submissions")
def list_question_submissions(question_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Submission)
        .filter(Submission.question_id == question_id)
        .order_by(Submission.id.desc())
        .all()
    )


@router.get("/submissions/{submission_id}")
def get_submission(submission_id: int, db: Session = Depends(get_db)):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


@router.get("/users/{user_id}/submissions")
def list_user_submissions(user_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Submission)
        .filter(Submission.user_id == user_id)
        .order_by(Submission.id.desc())
        .all()
    )