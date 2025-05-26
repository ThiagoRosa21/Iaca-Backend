
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, empresa, vendedor, descarte
from database import create_db
from routers import pagamento

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_db()

app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(empresa.router, prefix="/api/empresa", tags=["Empresa"])
app.include_router(vendedor.router, prefix="/api/vendedor", tags=["Vendedor"])
app.include_router(descarte.router, prefix="/api/descarte", tags=["Descarte"])
app.include_router(pagamento.router, prefix="/api/pagamento", tags=["Pagamento"])

@app.get("/")
def root():
    return {"message": "API iaca-app em funcionamento!"}
