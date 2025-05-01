from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import user
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=UserOut)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return user.create_user(db, user_data)