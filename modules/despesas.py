"""
modules/despesas.py
Registro de despesas do depósito (aluguel, água, luz, fornecedores etc).
"""

from database import conectar


def listar_despesas(data_inicio=None, data_fim=None):
    conn = conectar()
    cursor = conn.cursor()
    query = "SELECT * FROM despesas WHERE 1=1"
    params = []
    if data_inicio:
        query += " AND date(data) >= date(?)"
        params.append(data_inicio)
    if data_fim:
        query += " AND date(data) <= date(?)"
        params.append(data_fim)
    query += " ORDER BY data DESC"
    cursor.execute(query, params)
    resultado = cursor.fetchall()
    conn.close()
    return resultado


def criar_despesa(descricao, categoria, valor, forma_pagamento=None):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO despesas (descricao, categoria, valor, forma_pagamento)
        VALUES (?, ?, ?, ?)
    """, (descricao, categoria, valor, forma_pagamento))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def excluir_despesa(despesa_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM despesas WHERE id = ?", (despesa_id,))
    conn.commit()
    conn.close()


def total_despesas(data_inicio=None, data_fim=None):
    conn = conectar()
    cursor = conn.cursor()
    query = "SELECT COALESCE(SUM(valor), 0) AS total FROM despesas WHERE 1=1"
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
