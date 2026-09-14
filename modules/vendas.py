"""
modules/vendas.py
Registro de vendas. Cada venda tem 1+ itens, baixa o estoque automaticamente
e o total é calculado a partir dos itens. Tudo roda numa única transação
para garantir que a venda e a baixa de estoque nunca fiquem inconsistentes.
"""

from database import conectar


def criar_venda(itens, funcionario_id=None, forma_pagamento="dinheiro"):
    """
    itens: lista de dicts [{produto_id, quantidade}, ...]
    Retorna (venda_id, total).
    Lança ValueError se algum produto não existir ou não tiver estoque suficiente.
    """
    if not itens:
        raise ValueError("A venda precisa ter ao menos um item")

    conn = conectar()
    cursor = conn.cursor()
    try:
        total = 0.0
        itens_processados = []

        # Valida estoque e calcula subtotais antes de gravar qualquer coisa
        for item in itens:
            cursor.execute(
                "SELECT nome, preco_venda, estoque_atual FROM produtos WHERE id = ? AND ativo = 1",
                (item["produto_id"],)
            )
            produto = cursor.fetchone()
            if produto is None:
                raise ValueError(f"Produto id={item['produto_id']} não encontrado ou inativo")
            if produto["estoque_atual"] < item["quantidade"]:
                raise ValueError(
                    f"Estoque insuficiente para '{produto['nome']}' "
                    f"(disponível: {produto['estoque_atual']}, pedido: {item['quantidade']})"
                )
            preco_unitario = produto["preco_venda"]
            subtotal = preco_unitario * item["quantidade"]
            total += subtotal
            itens_processados.append({
                "produto_id": item["produto_id"],
                "nome": produto["nome"],
                "quantidade": item["quantidade"],
                "preco_unitario": preco_unitario,
                "subtotal": subtotal,
            })

        # Cria o cabeçalho da venda
        cursor.execute("""
            INSERT INTO vendas (funcionario_id, total, forma_pagamento, status)
            VALUES (?, ?, ?, 'concluida')
        """, (funcionario_id, total, forma_pagamento))
        venda_id = cursor.lastrowid

        # Cria os itens, baixa estoque e registra a movimentação
        for item in itens_processados:
            cursor.execute("""
                INSERT INTO vendas_itens (venda_id, produto_id, quantidade, preco_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (venda_id, item["produto_id"], item["quantidade"],
                  item["preco_unitario"], item["subtotal"]))

            cursor.execute(
                "UPDATE produtos SET estoque_atual = estoque_atual - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"])
            )

            cursor.execute("""
                INSERT INTO estoque_movimentacoes (produto_id, tipo, quantidade, motivo, observacao)
                VALUES (?, 'saida', ?, 'venda', ?)
            """, (item["produto_id"], item["quantidade"], f"Venda #{venda_id}"))

        conn.commit()
        return venda_id, total

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def cancelar_venda(venda_id):
    """Marca a venda como cancelada e devolve os itens ao estoque."""
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT status FROM vendas WHERE id = ?", (venda_id,))
        venda = cursor.fetchone()
        if venda is None:
            raise ValueError("Venda não encontrada")
        if venda["status"] == "cancelada":
            raise ValueError("Venda já está cancelada")

        cursor.execute("SELECT produto_id, quantidade FROM vendas_itens WHERE venda_id = ?", (venda_id,))
        itens = cursor.fetchall()

        for item in itens:
            cursor.execute(
                "UPDATE produtos SET estoque_atual = estoque_atual + ? WHERE id = ?",
                (item["quantidade"], item["produto_id"])
            )
            cursor.execute("""
                INSERT INTO estoque_movimentacoes (produto_id, tipo, quantidade, motivo, observacao)
                VALUES (?, 'entrada', ?, 'cancelamento', ?)
            """, (item["produto_id"], item["quantidade"], f"Cancelamento venda #{venda_id}"))

        cursor.execute("UPDATE vendas SET status = 'cancelada' WHERE id = ?", (venda_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def buscar_venda(venda_id):
    """Retorna a venda (cabeçalho) e seus itens, já com o nome do produto."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.*, f.nome AS funcionario_nome
        FROM vendas v
        LEFT JOIN funcionarios f ON f.id = v.funcionario_id
        WHERE v.id = ?
    """, (venda_id,))
    venda = cursor.fetchone()

    cursor.execute("""
        SELECT vi.*, p.nome AS produto_nome, p.unidade
        FROM vendas_itens vi
        JOIN produtos p ON p.id = vi.produto_id
        WHERE vi.venda_id = ?
    """, (venda_id,))
    itens = cursor.fetchall()

    conn.close()
    return venda, itens


def listar_vendas(data_inicio=None, data_fim=None):
    conn = conectar()
    cursor = conn.cursor()
    query = """
        SELECT v.*, f.nome AS funcionario_nome
        FROM vendas v
        LEFT JOIN funcionarios f ON f.id = v.funcionario_id
        WHERE 1=1
    """
    params = []
    if data_inicio:
        query += " AND date(v.data) >= date(?)"
        params.append(data_inicio)
    if data_fim:
        query += " AND date(v.data) <= date(?)"
        params.append(data_fim)
    query += " ORDER BY v.data DESC"
    cursor.execute(query, params)
    resultado = cursor.fetchall()
    conn.close()
    return resultado
