from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

SECRET = "mysecretkey123"  # TODO: put this in .env before deploying
ALGO   = "HS256"

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_pw(password):
    return pwd.hash(password)

def check_pw(plain, hashed):
    return pwd.verify(plain, hashed)

def make_token(user_id, role):
    data = {
        "sub":  str(user_id),
        "role": role,
        "exp":  datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(data, SECRET, algorithm=ALGO)

def get_current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        user_id = int(payload.get("sub"))
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def admin_only(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return current_user
