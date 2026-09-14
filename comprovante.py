"""
comprovante.py
Gera o comprovante de venda em PDF a partir dos dados de uma venda.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

PASTA_COMPROVANTES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "comprovantes")


def gerar_comprovante_pdf(venda, itens, nome_deposito="Depósito de Bebidas"):
    """
    venda: linha (sqlite3.Row) retornada por modules.vendas.buscar_venda
    itens: lista de linhas (sqlite3.Row) de itens da venda
    Retorna o caminho do arquivo PDF gerado.
    """
    os.makedirs(PASTA_COMPROVANTES, exist_ok=True)
    caminho = os.path.join(PASTA_COMPROVANTES, f"venda_{venda['id']}.pdf")

    c = canvas.Canvas(caminho, pagesize=A5)
    largura, altura = A5
    margem = 1.5 * cm
    y = altura - margem

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(largura / 2, y, nome_deposito)
    y -= 0.8 * cm

    c.setFont("Helvetica", 9)
    c.drawCentredString(largura / 2, y, "Comprovante de Venda")
    y -= 1 * cm

    c.setFont("Helvetica", 9)
    c.drawString(margem, y, f"Venda nº: {venda['id']}")
    c.drawRightString(largura - margem, y, f"Data: {venda['data']}")
    y -= 0.5 * cm

    if venda["funcionario_nome"]:
        c.drawString(margem, y, f"Atendido por: {venda['funcionario_nome']}")
        y -= 0.5 * cm

    c.drawString(margem, y, f"Forma de pagamento: {venda['forma_pagamento']}")
    y -= 0.7 * cm

    c.line(margem, y, largura - margem, y)
    y -= 0.5 * cm

    c.setFont("Helvetica-Bold", 9)
    c.drawString(margem, y, "Item")
    c.drawString(margem + 6.5 * cm, y, "Qtd")
    c.drawString(margem + 8 * cm, y, "Unit.")
    c.drawRightString(largura - margem, y, "Subtotal")
    y -= 0.4 * cm
    c.line(margem, y, largura - margem, y)
    y -= 0.5 * cm

    c.setFont("Helvetica", 9)
    for item in itens:
        nome = item["produto_nome"]
        if len(nome) > 30:
            nome = nome[:27] + "..."
        c.drawString(margem, y, nome)
        c.drawString(margem + 6.5 * cm, y, str(item["quantidade"]))
        c.drawString(margem + 8 * cm, y, f"R$ {item['preco_unitario']:.2f}")
        c.drawRightString(largura - margem, y, f"R$ {item['subtotal']:.2f}")
        y -= 0.5 * cm
        if y < 3 * cm:
            c.showPage()
            y = altura - margem

    y -= 0.3 * cm
    c.line(margem, y, largura - margem, y)
    y -= 0.7 * cm

    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(largura - margem, y, f"TOTAL: R$ {venda['total']:.2f}")
    y -= 1 * cm

    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(
        largura / 2, y,
        f"Emitido em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )

    c.save()
    return caminho
