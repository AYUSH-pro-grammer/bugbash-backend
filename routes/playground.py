from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.playground import Playground

from schemas.playground import (
    PlaygroundCreate,
    PlaygroundUpdate,
    PlaygroundRunRequest,
    PlaygroundResponse,
)
from service.execute import run_code, get_language_code

router = APIRouter(prefix="/playgrounds", tags=["playgrounds"])


def _execute(language: str, code: str, stdin: str = ""):
    compiler = get_language_code(language)
    return run_code(code, stdin, compiler)


@router.post("/", response_model=PlaygroundResponse)
def create_playground(payload: PlaygroundCreate, db: Session = Depends(get_db)):
    playground = Playground(
        user_id=payload.user_id,
        title=payload.title,
        language=payload.language,
        code=payload.code,
        stdin=payload.stdin,
        is_public=payload.is_public,
    )
    db.add(playground)
    db.commit()
    db.refresh(playground)
    return playground


@router.get("/", response_model=list[PlaygroundResponse])
def list_playgrounds(db: Session = Depends(get_db)):
    return db.query(Playground).order_by(Playground.id.desc()).all()


@router.get("/{playground_id}", response_model=PlaygroundResponse)
def get_playground(playground_id: int, db: Session = Depends(get_db)):
    playground = db.query(Playground).filter(Playground.id == playground_id).first()
    if not playground:
        raise HTTPException(status_code=404, detail="Playground not found")
    return playground


@router.patch("/{playground_id}", response_model=PlaygroundResponse)
def update_playground(
    playground_id: int,
    payload: PlaygroundUpdate,
    db: Session = Depends(get_db),
):
    playground = db.query(Playground).filter(Playground.id == playground_id).first()
    if not playground:
        raise HTTPException(status_code=404, detail="Playground not found")

    data = payload.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(playground, key, value)

    db.commit()
    db.refresh(playground)
    return playground







@router.post("/{playground_id}/run", response_model=PlaygroundResponse)
def run_playground(
    playground_id: int,
    payload: PlaygroundRunRequest,
    db: Session = Depends(get_db),
):
    playground = db.query(Playground).filter(Playground.id == playground_id).first()

    if not playground:
        raise HTTPException(status_code=404, detail="Playground not found")

    try:
        code_to_run = payload.code if payload.code is not None else playground.code
        stdin_to_run = payload.stdin if payload.stdin is not None else playground.stdin
        language_to_run = payload.language if payload.language is not None else playground.language

        result = run_code(
            code=code_to_run,
            input_data=stdin_to_run,
            language=language_to_run,
        )

        output = result.get("output") or ""
        error = result.get("error") or ""

        playground.last_output = output.strip()
        playground.last_error = error.strip() if error else None

    except Exception as e:
        playground.last_output = None
        playground.last_error = str(e)

    db.commit()
    db.refresh(playground)
    return playground

