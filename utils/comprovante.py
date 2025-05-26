from fpdf import FPDF
import os
from datetime import datetime
import qrcode

class PDF(FPDF):
    def header(self):
        # Logo
        logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 33)
        self.set_font("Arial", "B", 18)
        self.cell(0, 10, "Comprovante de pagamento", ln=True, align="C")
        self.set_font("Arial", "", 12)
        self.set_text_color(100)
        data_atual = datetime.now().strftime("%d %b %Y").upper()
        self.cell(0, 10, data_atual, ln=True, align="C")
        self.ln(10)

def gerar_comprovante_pdf(nome_empresa, valor_centavos, pagamento_id):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(0)

    valor_formatado = f"R$ {valor_centavos / 100:.2f}"

    # Informações principais
    pdf.cell(40, 10, "Valor:")
    pdf.cell(100, 10, valor_formatado, ln=True)

    pdf.cell(40, 10, "Documento:")
    pdf.cell(100, 10, "Fatura do cartão", ln=True)

    pdf.cell(40, 10, "Pagador:")
    pdf.cell(100, 10, nome_empresa, ln=True)

    pdf.cell(40, 10, "Agência:")
    pdf.cell(100, 10, "0001", ln=True)

    pdf.cell(40, 10, "Conta:")
    pdf.cell(100, 10, "*********", ln=True)

    pdf.cell(40, 10, "Código Stripe:")
    pdf.cell(100, 10, f"YA-{pagamento_id:06d}", ln=True)

    pdf.ln(10)

    # Rodapé com código
    pdf.set_fill_color(245, 245, 245)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, "Código de autenticação:", ln=True, fill=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, f"{pagamento_id:06d}", ln=True, fill=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, "Estamos aqui para ajudar se você tiver alguma dúvida.")

    # QR Code com link fictício
    qr_data = f"https://yaça.com/comprovante/{pagamento_id}"
    qr_img = qrcode.make(qr_data)
    qr_path = os.path.join("comprovantes", f"qr_{pagamento_id}.png")

    os.makedirs("comprovantes", exist_ok=True)  # ✅ Garante que a pasta existe
    qr_img.save(qr_path)

    pdf.image(qr_path, x=160, y=pdf.get_y() + 10, w=30)

    # Salvando o PDF
    nome_arquivo = f"comprovante_{pagamento_id}.pdf"
    caminho = os.path.join("comprovantes", nome_arquivo)
    pdf.output(caminho)

    # Remover QR temporário
    if os.path.exists(qr_path):
        os.remove(qr_path)

    return caminho
