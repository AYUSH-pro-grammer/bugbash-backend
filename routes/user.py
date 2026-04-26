from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.user import UserCreate, UserLogin

from deps.auth import get_current_user, create_access_token
from deps.password import hash_password, verify_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):

    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    if len(user.password) > 72:
        raise HTTPException(status_code=400, detail="Password too long (max 72 characters)")

    new_user = User(
        username=user.username,
        email=user.email,
        firstname=user.firstname,
        lastname=user.lastname,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user_id": new_user.id
    }


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(db_user.id)})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
def get_me(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "bio": user.bio,
        "profile_image": user.profile_image
    }


@router.put("/update")
def update_user(
    data: dict,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    allowed_fields = {"username", "firstname", "lastname", "bio", "profile_image"}

    for key, value in data.items():
        if key in allowed_fields:
            setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return {"message": "User updated successfully"}


@router.delete("/delete")
def delete_user(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}








from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

GOOGLE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com"

@router.post("/google-login")
def google_login(payload: dict, db: Session = Depends(get_db)):
    try:
        token = payload.get("token")

        if not token:
            raise HTTPException(status_code=400, detail="Token missing")

        # ✅ Verify token with Google
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo.get("email")
        name = idinfo.get("name", "")
        picture = idinfo.get("picture")

        if not email:
            raise HTTPException(status_code=400, detail="Invalid Google token")

        # ✅ Check if user exists
        user = db.query(User).filter(User.email == email).first()

        if not user:
            # 🔥 create user automatically
            username = email.split("@")[0]

            user = User(
                username=username,
                email=email,
                firstname=name.split(" ")[0] if name else "",
                lastname=" ".join(name.split(" ")[1:]) if name else "",
                hashed_password="",  # no password for google users
                profile_image=picture
            )

            db.add(user)
            db.commit()
            db.refresh(user)

        # ✅ Create your JWT
        token = create_access_token({"sub": str(user.id)})

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")
    