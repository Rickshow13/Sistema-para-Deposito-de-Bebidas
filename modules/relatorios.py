"""
modules/relatorios.py
Cálculo de lucro por período. Lucro não é armazenado — é sempre calculado
na hora a partir de vendas, despesas e perdas, pra nunca ficar desatualizado.

Lucro = total de vendas concluídas - despesas do período - valor das perdas
"""

from database import conectar
from modules.despesas import total_despesas
from modules.perdas import total_perdas


def total_vendas(data_inicio=None, data_fim=None):
    conn = conectar()
    cursor = conn.cursor()
    query = """
        SELECT COALESCE(SUM(total), 0) AS total
        FROM vendas
        WHERE status = 'concluida'
    """
    params = []
    if data_inicio:
        query += " AND date(data) >= date(?)"
        params.append(data_inicio)
    if data_fim:
        query += " AND date(data) <= date(?)"
        params.append(data_fim)
    cursor.execute(query, params)
    resultado = cursor.fetchone()["total"]
    conn.close()
    return resultado


def calcular_lucro(data_inicio=None, data_fim=None):
    """Retorna um dict com vendas, despesas, perdas e lucro líquido do período."""
    vendas = total_vendas(data_inicio, data_fim)
    despesas = total_despesas(data_inicio, data_fim)
    perdas = total_perdas(data_inicio, data_fim)
    lucro = vendas - despesas - perdas
    return {
        "vendas": vendas,
        "despesas": despesas,
        "perdas": perdas,
        "lucro": lucro,
    }


def produtos_mais_vendidos(data_inicio=None, data_fim=None, limite=10):
    conn = conectar()
    cursor = conn.cursor()
    query = """
        SELECT p.nome, SUM(vi.quantidade) AS quantidade_total,
               SUM(vi.subtotal) AS valor_total
        FROM vendas_itens vi
        JOIN vendas v ON v.id = vi.venda_id
        JOIN produtos p ON p.id = vi.produto_id
        WHERE v.status = 'concluida'
    """
    params = []
    if data_inicio:
        query += " AND date(v.data) >= date(?)"
        params.append(data_inicio)
    if data_fim:
        query += " AND date(v.data) <= date(?)"
        params.append(data_fim)
    query += " GROUP BY p.id ORDER BY quantidade_total DESC LIMIT ?"
    params.append(limite)
    cursor.execute(query, params)
    resultado = cursor.fetchall()
    conn.close()
    return resultado
