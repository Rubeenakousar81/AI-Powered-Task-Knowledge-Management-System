from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import User, ActivityLog
from app.auth_helper import hash_pw, check_pw, make_token, get_current_user, admin_only

router = APIRouter()

class RegisterBody(BaseModel):
    name: str
    email: str
    password: str
    role: str = "user"

class LoginBody(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(body: RegisterBody, db: Session = Depends(get_db)):
    # check if email already used
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name     = body.name,
        email    = body.email,
        password = hash_pw(body.password),
        role     = body.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Account created!", "user_id": user.id}


@router.post("/login")
def login(body: LoginBody, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()

    if not user or not check_pw(body.password, user.password):
        raise HTTPException(status_code=401, detail="Wrong email or password")

    token = make_token(user.id, user.role)

    # log this action
    db.add(ActivityLog(user_id=user.id, action="login", detail=f"{user.email} logged in"))
    db.commit()

    return {
        "access_token": token,
        "token_type":   "bearer",
        "user_id":      user.id,
        "name":         user.name,
        "role":         user.role
    }


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id":    current_user.id,
        "name":  current_user.name,
        "email": current_user.email,
        "role":  current_user.role
    }


@router.get("/users")
def get_users(db: Session = Depends(get_db), admin = Depends(admin_only)):
    users = db.query(User).all()
    return [{"id": u.id, "name": u.name, "email": u.email, "role": u.role} for u in users]
