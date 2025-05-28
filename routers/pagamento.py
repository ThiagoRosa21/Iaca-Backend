from fastapi import APIRouter, HTTPException, Depends, Request, Response
from sqlalchemy.orm import Session
from database import SessionLocal
from models.all_models import Pagamento, Empresa
from schemas.all_schemas import PagamentoCreate, PagamentoResponse
import stripe
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import List
from utils.comprovante import gerar_comprovante_pdf
from utils.email import enviar_email
from fastapi.responses import FileResponse
from fpdf import FPDF
import qrcode
import hashlib


load_dotenv()
router = APIRouter()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/pagar", summary="Cria uma sessão de pagamento e retorna a URL")
def pagar_empresa(dados: PagamentoCreate, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.id == dados.empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "brl",
                    "product_data": {"name": f"Pagamento por {empresa.nome}"},
                    "unit_amount": dados.valor_centavos,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="http://localhost:5173/sucesso",
            cancel_url="http://localhost:5173/erro",
        )

        pagamento = Pagamento(
            empresa_id=dados.empresa_id,
            valor_centavos=dados.valor_centavos,
            stripe_session_id=session.id,
            status="pendente",
            metodo_pagamento="card",
            data_pagamento=datetime.utcnow(),
            ponto_id=dados.ponto_id
        )

        db.add(pagamento)
        db.commit()
        db.refresh(pagamento)

        return {"checkout_url": session.url}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook", summary="Recebe eventos de pagamento do Stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    from models.all_models import Descarte  # Importar se necessário

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session["id"]

        pagamento = db.query(Pagamento).filter(Pagamento.stripe_session_id == session_id).first()
        if pagamento and pagamento.status != "pago":
            pagamento.status = "pago"
            db.commit()

            # ✅ Zera os descartes do ponto que foram comprados
            if pagamento.ponto_id:
                descartes = db.query(Descarte).filter(
                    Descarte.ponto_id == pagamento.ponto_id,
                    Descarte.comprado == False
                ).all()

                for d in descartes:
                    d.comprado = True

                db.commit()

            # Envia comprovante por e-mail
            empresa = db.query(Empresa).filter(Empresa.id == pagamento.empresa_id).first()
            if empresa:
                caminho_pdf = gerar_comprovante_pdf(
                    empresa.nome,
                    pagamento.valor_centavos,
                    pagamento.id
                )

                enviar_email(
                    destinatario=empresa.email,
                    assunto="Pagamento confirmado",
                    corpo=f"Olá {empresa.nome}, seu pagamento de R$ {pagamento.valor_centavos / 100:.2f} foi confirmado com sucesso.",
                    anexo_pdf=caminho_pdf
                )

    return {"status": "success"}




@router.get("/empresa/{empresa_id}", response_model=List[PagamentoResponse])
def listar_pagamentos_empresa(empresa_id: int, db: Session = Depends(get_db)):
    pagamentos = db.query(Pagamento).filter(Pagamento.empresa_id == empresa_id).all()
    return pagamentos


@router.get("/comprovante/{pagamento_id}", summary="Download do comprovante PDF")
def baixar_comprovante(pagamento_id: int):
    nome_arquivo = f"comprovante_{pagamento_id}.pdf"
    caminho = os.path.join("comprovantes", nome_arquivo)
    if not os.path.exists(caminho):
        raise HTTPException(status_code=404, detail="Comprovante não encontrado")
    return FileResponse(caminho, media_type='application/pdf', filename=nome_arquivo)


@router.get("/historico/{empresa_id}", summary="Histórico de pagamentos com link do comprovante")
def historico_pagamentos(empresa_id: int, db: Session = Depends(get_db)):
    pagamentos = db.query(Pagamento).filter(Pagamento.empresa_id == empresa_id).all()
    resultado = []
    for pagamento in pagamentos:
        comprovante_url = f"/api/pagamento/comprovante/{pagamento.id}" if pagamento.status == "pago" else None
        resultado.append({
            "id": pagamento.id,
            "valor_centavos": pagamento.valor_centavos,
            "status": pagamento.status,
            "data_pagamento": pagamento.data_pagamento,
            "comprovante_url": comprovante_url
        })
    return resultado


@router.get("/nota-fiscal/{pagamento_id}", summary="Gerar nota fiscal estilo DANFE")
def gerar_nota_fiscal(pagamento_id: int, db: Session = Depends(get_db)):
    pagamento = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if not pagamento or pagamento.status != "pago":
        raise HTTPException(status_code=404, detail="Pagamento não encontrado ou não confirmado")

    empresa = db.query(Empresa).filter(Empresa.id == pagamento.empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    pdf = FPDF()
    pdf.add_page()

    logo_path = os.path.join("assets", "logo.png")
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=30)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"NF-e Nº {pagamento.id:06d} - Série 1", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Documento Auxiliar da Nota Fiscal Eletrônica", ln=True, align="C")
    pdf.cell(0, 10, f"Data de Emissão: {pagamento.data_pagamento.strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, f"Emitente: {empresa.nome} - CNPJ: {empresa.cnpj}", ln=True)
    pdf.cell(0, 10, f"Endereço: {empresa.endereco}", ln=True)
    pdf.cell(0, 10, f"E-mail: {empresa.email}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Itens da Nota Fiscal", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, f"1x Serviço de coleta reciclável - R$ {pagamento.valor_centavos / 100:.2f}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Valor Total: R$ {pagamento.valor_centavos / 100:.2f}", ln=True)

    hash_base = f"{pagamento.id}{empresa.email}{pagamento.valor_centavos}{pagamento.data_pagamento}".encode()
    hash_nf = hashlib.sha256(hash_base).hexdigest()[:10].upper()

    qr_data = f"https://yaça.com/nota/{pagamento_id}?auth={hash_nf}"
    qr_img = qrcode.make(qr_data)
    qr_path = os.path.join("notas_fiscais", f"qr_nf_{pagamento_id}.png")
    os.makedirs("notas_fiscais", exist_ok=True)
    qr_img.save(qr_path)
    pdf.image(qr_path, x=160, y=pdf.get_y() + 5, w=30)

    pdf.set_font("Arial", "I", 10)
    pdf.ln(20)
    pdf.cell(0, 10, f"Documento sem valor fiscal - Código de Autenticação: {hash_nf}", ln=True)

    os.makedirs("notas_fiscais", exist_ok=True)
    caminho = os.path.join("notas_fiscais", f"nota_{pagamento_id}.pdf")
    pdf.output(caminho)

    if os.path.exists(qr_path):
        os.remove(qr_path)

    pagamento.nota_fiscal_hash = hash_nf
    db.commit()

    enviar_email(
        destinatario=empresa.email,
        assunto="Nota Fiscal da sua compra",
        corpo=f"Olá {empresa.nome}, em anexo está a nota fiscal referente ao seu pagamento de R$ {pagamento.valor_centavos / 100:.2f}. Código de autenticação: {hash_nf}.",
        anexo_pdf=caminho
    )

    return FileResponse(caminho, media_type='application/pdf', filename=f"nota_{pagamento_id}.pdf")


