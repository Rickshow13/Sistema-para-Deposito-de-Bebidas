"""
modules/perdas.py
Registro de perdas de produtos (vencidos, quebrados, extraviados etc).
Toda perda baixa o estoque automaticamente.
"""

from database import conectar


def registrar_perda(produto_id, quantidade, motivo, valor_perda=None):
    """
    Se valor_perda não for informado, calcula automaticamente como
    preco_custo do produto x quantidade perdida.
    """
    if quantidade <= 0:
        raise ValueError("quantidade deve ser maior que zero")

    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT nome, preco_custo, estoque_atual FROM produtos WHERE id = ?",
            (produto_id,)
        )
        produto = cursor.fetchone()
        if produto is None:
            raise ValueError("Produto não encontrado")
        if produto["estoque_atual"] < quantidade:
            raise ValueError(
                f"Estoque insuficiente para registrar a perda "
                f"(disponível: {produto['estoque_atual']}, perda: {quantidade})"
            )

        if valor_perda is None:
            valor_perda = produto["preco_custo"] * quantidade

        cursor.execute("""
            INSERT INTO perdas (produto_id, quantidade, motivo, valor_perda)
            VALUES (?, ?, ?, ?)
        """, (produto_id, quantidade, motivo, valor_perda))
        perda_id = cursor.lastrowid

        cursor.execute(
            "UPDATE produtos SET estoque_atual = estoque_atual - ? WHERE id = ?",
            (quantidade, produto_id)
        )

        cursor.execute("""
            INSERT INTO estoque_movimentacoes (produto_id, tipo, quantidade, motivo, observacao)
            VALUES (?, 'saida', ?, 'perda', ?)
        """, (produto_id, quantidade, f"Perda #{perda_id}: {motivo}"))

        conn.commit()
        return perda_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def listar_perdas(data_inicio=None, data_fim=None):
    conn = conectar()
    cursor = conn.cursor()
    query = """
        SELECT pe.*, p.nome AS produto_nome
        FROM perdas pe
        JOIN produtos p ON p.id = pe.produto_id
        WHERE 1=1
    """
    params = []
    if data_inicio:
        query += " AND date(pe.data) >= date(?)"
        params.append(data_inicio)
    if data_fim:
        query += " AND date(pe.data) <= date(?)"
        params.append(data_fim)
    query += " ORDER BY pe.data DESC"
    cursor.execute(query, params)
    resultado = cursor.fetchall()
    conn.close()
    return resultado


def total_perdas(data_inicio=None, data_fim=None):
    conn = conectar()
    cursor = conn.cursor()
    query = "SELECT COALESCE(SUM(valor_perda), 0) AS total FROM perdas WHERE 1=1"
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
