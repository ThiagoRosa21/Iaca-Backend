from sqlalchemy.orm import Session
from app import models, schemas
from app.auth.security import hash_password


def create_company(db: Session, company: schemas.CompanyCreate):
    db_company = models.Company(
        name=company.name,
        email=company.email,
        password=hash_password(company.password)
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def get_company_by_email(db: Session, email: str):
    return db.query(models.Company).filter(models.Company.email == email).first()
