from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import user, company
from app.auth import security, jwt

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = user.get_user_by_email(db, form_data.username)
    db_company = company.get_company_by_email(db, form_data.username)

    account = db_user or db_company
    if not account or not security.verify_password(form_data.password, account.password):
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    token = jwt.create_access_token({"sub": account.email})
    return {"access_token": token, "token_type": "bearer"}
