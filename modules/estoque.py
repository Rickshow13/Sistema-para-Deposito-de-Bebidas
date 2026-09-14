"""
modules/estoque.py
Controle de entradas e saídas de estoque. Toda movimentação passa por aqui
para manter o campo produtos.estoque_atual sempre consistente.
"""

from database import conectar


def registrar_movimentacao(produto_id, tipo, quantidade, motivo="ajuste", observacao=None):
    """
    tipo: 'entrada' ou 'saida'
    Atualiza o estoque_atual do produto e grava o histórico da movimentação.
    """
    if tipo not in ("entrada", "saida"):
        raise ValueError("tipo deve ser 'entrada' ou 'saida'")
    if quantidade <= 0:
        raise ValueError("quantidade deve ser maior que zero")

    conn = conectar()
    cursor = conn.cursor()

    if tipo == "saida":
        cursor.execute("SELECT estoque_atual FROM produtos WHERE id = ?", (produto_id,))
        row = cursor.fetchone()
        if row is None:
            conn.close()
            raise ValueError("Produto não encontrado")
        if row["estoque_atual"] < quantidade:
            conn.close()
            raise ValueError(
                f"Estoque insuficiente (disponível: {row['estoque_atual']}, "
                f"solicitado: {quantidade})"
            )

    cursor.execute("""
        INSERT INTO estoque_movimentacoes (produto_id, tipo, quantidade, motivo, observacao)
        VALUES (?, ?, ?, ?, ?)
    """, (produto_id, tipo, quantidade, motivo, observacao))

    if tipo == "entrada":
        cursor.execute(
            "UPDATE produtos SET estoque_atual = estoque_atual + ? WHERE id = ?",
            (quantidade, produto_id)
        )
    else:
        cursor.execute(
            "UPDATE produtos SET estoque_atual = estoque_atual - ? WHERE id = ?",
            (quantidade, produto_id)
        )

    conn.commit()
    conn.close()


def historico_produto(produto_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM estoque_movimentacoes
        WHERE produto_id = ?
        ORDER BY data DESC
    """, (produto_id,))
    resultado = cursor.fetchall()
    conn.close()
    return resultado


def historico_geral(data_inicio=None, data_fim=None):
    conn = conectar()
    cursor = conn.cursor()
    query = """
        SELECT em.*, p.nome AS produto_nome
        FROM estoque_movimentacoes em
        JOIN produtos p ON p.id = em.produto_id
        WHERE 1=1
    """
    params = []
    if data_inicio:
        query += " AND date(em.data) >= date(?)"
        params.append(data_inicio)
    if data_fim:
        query += " AND date(em.data) <= date(?)"
        params.append(data_fim)
    query += " ORDER BY em.data DESC"
    cursor.execute(query, params)
    resultado = cursor.fetchall()
    conn.close()
    return resultado
