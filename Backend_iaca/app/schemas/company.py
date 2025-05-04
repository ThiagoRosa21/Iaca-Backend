from pydantic import BaseModel, EmailStr

class CompanyCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class CompanyOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True