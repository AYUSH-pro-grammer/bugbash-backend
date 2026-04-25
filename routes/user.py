from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db

from models.user import User
from schemas.user import UserCreate, UserLogin
from deps.auth import get_current_user, create_access_token
from deps.auth import verify_access_token
from deps.password import hash_password, verify_password  # assuming same file or adjust import



router = APIRouter(prefix="/users", tags=["Users"])


# -----------------------
# Helper: verify password
# -----------------------

# -----------------------
# REGISTER
# -----------------------
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):

    # check if email exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # check username
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )

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

    # 🔹 Step 1 — fetch user
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # 🔹 Step 2 — verify password safely
    try:
        is_valid = verify_password(user.password, db_user.hashed_password)
    except Exception as e:
        # 🔥 prevents 500 crash and exposes issue during dev
        print("PASSWORD VERIFY ERROR:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password verification failed"
        )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # 🔹 Step 3 — create token
    try:
        token = create_access_token({"sub": str(db_user.id)})
    except Exception as e:
        print("TOKEN ERROR:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token creation failed"
        )

    # 🔹 Step 4 — return response
    return {
        "access_token": token,
        "token_type": "bearer"
    }


# -----------------------
# GET CURRENT USER
# -----------------------
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


# -----------------------
# UPDATE PROFILE
# -----------------------
@router.put("/update")
def update_user(
    data: dict,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return {"message": "User updated successfully"}


# -----------------------
# DELETE USER
# -----------------------
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