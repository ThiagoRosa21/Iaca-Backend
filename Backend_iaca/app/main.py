from fastapi import FastAPI
from app.routers import auth, user, company
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Projeto Açaí Sustentável")

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(company.router)
