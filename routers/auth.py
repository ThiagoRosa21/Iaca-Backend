from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from database import SessionLocal
from schemas.all_schemas import Token
from models import all_models
from utils.security import verify_password, create_access_token, hash_password
from fastapi.security import OAuth2PasswordRequestForm
from utils.email import enviar_email
import random
from datetime import datetime, timedelta

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def gerar_codigo_verificacao():
    return ''.join(random.choices("0123456789", k=6))


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(all_models.Empresa).filter(all_models.Empresa.email == form_data.username).first()
    role = "empresa"

    if not user:
        user = db.query(all_models.Vendedor).filter(all_models.Vendedor.email == form_data.username).first()
        role = "vendedor"

    if not user or not verify_password(form_data.password, user.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

    if not user.email_verificado:
        raise HTTPException(status_code=403, detail="Verifique seu e-mail antes de fazer login.")

    access_token = create_access_token(data={"id": user.id, "role": role})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register")
def registro_usuario(
    tipo: str = Body(...),
    dados: dict = Body(...),
    db: Session = Depends(get_db)
):
    codigo = gerar_codigo_verificacao()
    expira_em = datetime.utcnow() + timedelta(minutes=10)

    if tipo == "empresa":
        if db.query(all_models.Empresa).filter(all_models.Empresa.email == dados["email"]).first():
            raise HTTPException(status_code=400, detail="Email já cadastrado")

        empresa = all_models.Empresa(
            nome=dados["nome"],
            cnpj=dados["cnpj"],
            email=dados["email"],
            senha_hash=hash_password(dados["senha"]),
            telefone=dados.get("telefone", ""),
            whatsapp=dados.get("whatsapp", False),
            endereco=dados.get("endereco", ""),
            receber_info=dados.get("receber_info", False),
            email_verificado=False,
            codigo_verificacao=codigo,
            codigo_verificacao_expira_em=expira_em
        )

        db.add(empresa)
        db.commit()
        db.refresh(empresa)

        enviar_email(
            destinatario=empresa.email,
            assunto="Verificação de E-mail - Iacá",
            corpo=f"Olá {empresa.nome},\n\nSeu código de verificação é: {codigo}\n\nDigite esse código no app para ativar sua conta. Ele expira em 10 minutos."
        )

        return {"tipo": "empresa", "id": empresa.id}

    elif tipo == "vendedor":
        if db.query(all_models.Vendedor).filter(all_models.Vendedor.email == dados["email"]).first():
            raise HTTPException(status_code=400, detail="Email já cadastrado")

        vendedor = all_models.Vendedor(
            nome=dados["nome"],
            email=dados["email"],
            senha_hash=hash_password(dados["senha"]),
            local_feira=dados.get("local_feira", ""),
            telefone=dados.get("telefone", ""),
            whatsapp=dados.get("whatsapp", False),
            receber_info=dados.get("receber_info", False),
            email_verificado=False,
            codigo_verificacao=codigo,
            codigo_verificacao_expira_em=expira_em
        )

        db.add(vendedor)
        db.commit()
        db.refresh(vendedor)

        enviar_email(
            destinatario=vendedor.email,
            assunto="Verificação de E-mail - Iacá",
            corpo=f"Olá {vendedor.nome},\n\nSeu código de verificação é: {codigo}\n\nDigite esse código no app para ativar sua conta. Ele expira em 10 minutos."
        )

        return {"tipo": "vendedor", "id": vendedor.id}

    else:
        raise HTTPException(status_code=400, detail="Tipo inválido: use 'empresa' ou 'vendedor'")


@router.post("/verificar-email")
def verificar_email(email: str = Body(...), codigo: str = Body(...), db: Session = Depends(get_db)):
    user = db.query(all_models.Empresa).filter_by(email=email).first() or \
           db.query(all_models.Vendedor).filter_by(email=email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if user.email_verificado:
        return {"message": "E-mail já verificado"}

    if user.codigo_verificacao != codigo:
        raise HTTPException(status_code=400, detail="Código incorreto")

    if user.codigo_verificacao_expira_em and user.codigo_verificacao_expira_em < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Código expirado. Solicite um novo.")

    user.email_verificado = True
    user.codigo_verificacao = None
    user.codigo_verificacao_expira_em = None
    db.commit()

    return {"message": "E-mail verificado com sucesso"}


@router.post("/reenviar-codigo")
def reenviar_codigo(email: str = Body(...), db: Session = Depends(get_db)):
    user = db.query(all_models.Empresa).filter_by(email=email).first() or \
           db.query(all_models.Vendedor).filter_by(email=email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if user.email_verificado:
        return {"message": "E-mail já verificado"}

    novo_codigo = gerar_codigo_verificacao()
    nova_expiracao = datetime.utcnow() + timedelta(minutes=10)

    user.codigo_verificacao = novo_codigo
    user.codigo_verificacao_expira_em = nova_expiracao
    db.commit()

    enviar_email(
        destinatario=user.email,
        assunto="Novo Código de Verificação - Iacá",
        corpo=f"Seu novo código é: {novo_codigo}. Ele expira em 10 minutos."
    )

    return {"message": "Código reenviado com sucesso"}
