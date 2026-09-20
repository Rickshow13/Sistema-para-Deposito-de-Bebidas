"""
comprovante.py
Gera o comprovante de venda em PDF a partir dos dados de uma venda.
"""

import sys                                          # pra detectar se está rodando como .exe (frozen)
import os                                            # pra montar caminhos de arquivo/pasta
from datetime import datetime                        # pra pegar a data/hora atual no rodapé
from reportlab.lib.pagesizes import A5                # tamanho de página A5 (meia folha A4)
from reportlab.lib.units import cm                    # unidade "centímetro" já convertida pra pontos
from reportlab.pdfgen import canvas                    # o "desenhador" de PDF de verdade

# Mesma lógica de database.py: rodando como .exe, usa a pasta do .exe
# (sys.executable); rodando como script Python normal, usa a pasta deste
# arquivo (__file__). Isso evita salvar os PDFs numa pasta temporária que
# some quando o programa fecha.
if getattr(sys, "frozen", False):                       # True só quando rodando como .exe empacotado
    BASE_DIR = os.path.dirname(sys.executable)             # pasta onde o .exe está de verdade
else:                                                     # rodando normal, via "python main.py"
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))    # pasta deste arquivo .py

PASTA_COMPROVANTES = os.path.join(BASE_DIR, "comprovantes")  # pasta onde os PDFs são salvos


def gerar_comprovante_pdf(venda, itens, nome_deposito="Depósito de Bebidas"):
    """
    venda: linha (sqlite3.Row) retornada por modules.vendas.buscar_venda
    itens: lista de linhas (sqlite3.Row) de itens da venda
    Retorna o caminho do arquivo PDF gerado.
    """
    os.makedirs(PASTA_COMPROVANTES, exist_ok=True)   # cria a pasta comprovantes/ se ainda não existir
    caminho = os.path.join(PASTA_COMPROVANTES, f"venda_{venda['id']}.pdf")  # nome do arquivo final

    c = canvas.Canvas(caminho, pagesize=A5)          # cria o "papel" do PDF, tamanho A5
    largura, altura = A5                              # desempacota largura e altura da página
    margem = 1.5 * cm                                 # distância das bordas
    y = altura - margem                               # começa a escrever 1,5cm abaixo do topo

    c.setFont("Helvetica-Bold", 14)                   # fonte negrito, tamanho 14
    c.drawCentredString(largura / 2, y, nome_deposito) # escreve o nome do depósito, centralizado
    y -= 0.8 * cm                                      # desce o cursor pra próxima linha

    c.setFont("Helvetica", 9)                          # fonte normal, tamanho 9
    c.drawCentredString(largura / 2, y, "Comprovante de Venda")  # subtítulo centralizado
    y -= 1 * cm                                         # desce mais

    c.setFont("Helvetica", 9)                           # garante a fonte normal
    c.drawString(margem, y, f"Venda nº: {venda['id']}")  # número da venda, alinhado à esquerda
    c.drawRightString(largura - margem, y, f"Data: {venda['data']}")  # data, alinhada à direita
    y -= 0.5 * cm                                         # desce

    if venda["funcionario_nome"]:                          # só escreve se tiver funcionário associado
        c.drawString(margem, y, f"Atendido por: {venda['funcionario_nome']}")  # nome de quem atendeu
        y -= 0.5 * cm                                        # desce só se a linha foi escrita

    c.drawString(margem, y, f"Forma de pagamento: {venda['forma_pagamento']}")  # forma de pagamento
    y -= 0.7 * cm                                            # desce mais, antes da linha separadora

    c.line(margem, y, largura - margem, y)                   # desenha uma linha horizontal separadora
    y -= 0.5 * cm                                             # desce

    c.setFont("Helvetica-Bold", 9)                            # negrito pro cabeçalho da tabela de itens
    c.drawString(margem, y, "Item")                            # cabeçalho da coluna "Item"
    c.drawString(margem + 6.5 * cm, y, "Qtd")                   # cabeçalho da coluna "Qtd"
    c.drawString(margem + 8 * cm, y, "Unit.")                    # cabeçalho da coluna "Unit."
    c.drawRightString(largura - margem, y, "Subtotal")           # cabeçalho da coluna "Subtotal"
    y -= 0.4 * cm                                                 # desce um pouco
    c.line(margem, y, largura - margem, y)                       # outra linha separadora
    y -= 0.5 * cm                                                 # desce mais

    c.setFont("Helvetica", 9)                                     # volta pra fonte normal pros itens
    for item in itens:                                            # percorre cada item da venda
        nome = item["produto_nome"]                                # pega o nome do produto
        if len(nome) > 30:                                          # se o nome for muito comprido
            nome = nome[:27] + "..."                                 # corta em 27 caracteres + reticências

        c.drawString(margem, y, nome)                                # escreve o nome do produto
        c.drawString(margem + 6.5 * cm, y, str(item["quantidade"]))  # escreve a quantidade
        c.drawString(margem + 8 * cm, y, f"R$ {item['preco_unitario']:.2f}")  # escreve o preço unitário
        c.drawRightString(largura - margem, y, f"R$ {item['subtotal']:.2f}")  # escreve o subtotal
        y -= 0.5 * cm                                                 # desce pro próximo item

        if y < 3 * cm:                                                # se estiver perto do fim da página
            c.showPage()                                               # fecha a página atual, abre uma nova
            y = altura - margem                                        # reseta o y pro topo da nova página

    y -= 0.3 * cm                                                      # desce um pouco depois do loop
    c.line(margem, y, largura - margem, y)                             # linha separadora antes do total
    y -= 0.7 * cm                                                      # desce mais

    c.setFont("Helvetica-Bold", 11)                                    # negrito, maior, pro total
    c.drawRightString(largura - margem, y, f"TOTAL: R$ {venda['total']:.2f}")  # escreve o total
    y -= 1 * cm                                                        # desce, preparando o rodapé

    c.setFont("Helvetica-Oblique", 8)                                  # fonte itálica, pequena, pro rodapé
    c.drawCentredString(                                               # escreve a data/hora de emissão
        largura / 2, y,
        f"Emitido em {datetime.now().strftime('%d/%m/%Y %H:%M')}"       # formata a data/hora no padrão BR
    )

    c.save()                                                            # grava o PDF de verdade no disco
    return caminho                                                      # devolve o caminho do arquivo gerado
