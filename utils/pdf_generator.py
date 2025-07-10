from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from datetime import datetime

def gerar_pdf(nome_cliente, produtos, total, caminho_pdf):
    c = canvas.Canvas(caminho_pdf, pagesize=A4)
    largura, altura = A4

    # Cabeçalho
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(largura/2, altura - 40, "Orçamento de Ferramentas")
    c.setStrokeColor(colors.grey)
    c.line(40, altura - 50, largura - 40, altura - 50)

    c.setFont("Helvetica", 12)
    c.drawString(50, altura - 80, f"Cliente: {nome_cliente}")
    c.drawString(50, altura - 100, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    y = altura - 140
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Itens:")
    y -= 20

    # Tabela de produtos
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, y, "Produto")
    c.drawString(220, y, "Descrição")
    c.drawString(420, y, "Preço (R$)")
    y -= 10
    c.line(50, y, largura - 50, y)
    y -= 15
    c.setFont("Helvetica", 10)

    item_bg_colors = [colors.whitesmoke, colors.Color(0.8, 0.8, 0.8, alpha=0.3)]  # branco e cinza mais escuro
    item_index = 0

    for nome, descricao, preco in produtos:
        # Quebra de linha para nome e descrição
        nome_lines = simpleSplit(str(nome), "Helvetica", 10, 150)
        desc_lines = simpleSplit(str(descricao), "Helvetica", 10, 180)
        max_lines = max(len(nome_lines), len(desc_lines))
        item_height = 14 * max_lines
        # Desenha o fundo alternado
        c.setFillColor(item_bg_colors[item_index % 2])
        c.rect(50, y - item_height + 4, largura - 100, item_height, fill=1, stroke=0)
        c.setFillColor(colors.black)
        for i in range(max_lines):
            n = nome_lines[i] if i < len(nome_lines) else ""
            d = desc_lines[i] if i < len(desc_lines) else ""
            if i == 0:
                c.drawString(60, y, n)
                c.drawString(220, y, d)
                c.drawRightString(490, y, f"{preco:.2f}")
            else:
                c.drawString(60, y, n)
                c.drawString(220, y, d)
            y -= 14
            if y < 100:
                c.showPage()
                y = altura - 100
                c.setFont("Helvetica", 10)
        item_index += 1

    y -= 10
    c.setStrokeColor(colors.grey)
    c.line(50, y, largura - 50, y)
    y -= 25
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.darkblue)
    c.drawString(50, y, f"Total: R$ {total:.2f}")
    c.setFillColor(colors.black)

    c.save()