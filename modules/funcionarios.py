"""
modules/funcionarios.py
Cadastro de funcionários (sem login individual — usados só para registrar
quem fez cada venda).
"""

from database import conectar


def listar_funcionarios(apenas_ativos=True):
    conn = conectar()
    cursor = conn.cursor()
    if apenas_ativos:
        cursor.execute("SELECT * FROM funcionarios WHERE ativo = 1 ORDER BY nome")
    else:
        cursor.execute("SELECT * FROM funcionarios ORDER BY nome")
    resultado = cursor.fetchall()
    conn.close()
    return resultado


def criar_funcionario(nome, cargo=None, telefone=None, data_admissao=None):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO funcionarios (nome, cargo, telefone, data_admissao)
        VALUES (?, ?, ?, ?)
    """, (nome, cargo, telefone, data_admissao))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def atualizar_funcionario(funcionario_id, nome, cargo, telefone, data_admissao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE funcionarios
        SET nome = ?, cargo = ?, telefone = ?, data_admissao = ?
        WHERE id = ?
    """, (nome, cargo, telefone, data_admissao, funcionario_id))
    conn.commit()
    conn.close()


def desativar_funcionario(funcionario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE funcionarios SET ativo = 0 WHERE id = ?", (funcionario_id,))
    conn.commit()
    conn.close()
