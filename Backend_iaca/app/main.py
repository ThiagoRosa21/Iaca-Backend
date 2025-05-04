from fastapi import FastAPI
from app.routers import auth, user, company
from app.database import Base, engine
from app.routers import acai
from fastapi.middleware.cors import CORSMiddleware
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Projeto Açaí Sustentável")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(company.router)
app.include_router(acai.router)