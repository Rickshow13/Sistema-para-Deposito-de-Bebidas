"""
modules/produtos.py
CRUD do cadastro de produtos (itens do depósito).
"""

from database import conectar


def listar_produtos(apenas_ativos=True):
    conn = conectar()
    cursor = conn.cursor()
    if apenas_ativos:
        cursor.execute("SELECT * FROM produtos WHERE ativo = 1 ORDER BY nome")
    else:
        cursor.execute("SELECT * FROM produtos ORDER BY nome")
    resultado = cursor.fetchall()
    conn.close()
    return resultado


def buscar_produto(produto_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado


def criar_produto(nome, categoria, unidade, preco_custo, preco_venda,
                   estoque_minimo=0, estoque_inicial=0):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO produtos (nome, categoria, unidade, preco_custo, preco_venda,
                               estoque_minimo, estoque_atual)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nome, categoria, unidade, preco_custo, preco_venda,
          estoque_minimo, estoque_inicial))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def atualizar_produto(produto_id, nome, categoria, unidade, preco_custo,
                       preco_venda, estoque_minimo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE produtos
        SET nome = ?, categoria = ?, unidade = ?, preco_custo = ?,
            preco_venda = ?, estoque_minimo = ?
        WHERE id = ?
    """, (nome, categoria, unidade, preco_custo, preco_venda,
          estoque_minimo, produto_id))
    conn.commit()
    conn.close()


def desativar_produto(produto_id):
    """Não apaga o produto (preserva histórico de vendas/estoque) — só marca como inativo."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE produtos SET ativo = 0 WHERE id = ?", (produto_id,))
    conn.commit()
    conn.close()


def produtos_estoque_baixo():
    """Retorna produtos cujo estoque atual está no ou abaixo do mínimo definido."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM produtos
        WHERE ativo = 1 AND estoque_atual <= estoque_minimo
        ORDER BY nome
    """)
    resultado = cursor.fetchall()
    conn.close()
    return resultado
