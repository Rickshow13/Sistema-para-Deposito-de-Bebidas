"""
database.py
Responsável por conectar ao banco SQLite e criar todas as tabelas do sistema.
"""

import sqlite3  # biblioteca padrão do Python pra trabalhar com banco SQLite
import sys      # pra detectar se está rodando como .exe (frozen) ou como script normal
import os       # biblioteca padrão pra mexer com caminhos de arquivo/pasta

# Quando o programa roda como .exe (gerado pelo PyInstaller), __file__ aponta
# pra uma pasta temporária que é apagada ao fechar o programa — o que faria
# o banco de dados "sumir" a cada execução. Por isso, quando estiver rodando
# como .exe (sys.frozen), usamos a pasta onde o .exe realmente está
# (sys.executable) em vez de __file__.
if getattr(sys, "frozen", False):          # True só quando rodando como .exe empacotado
    BASE_DIR = os.path.dirname(sys.executable)  # pasta onde o .exe está de verdade
else:                                        # rodando normal, via "python main.py"
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # pasta deste arquivo .py

DB_PATH = os.path.join(BASE_DIR, "deposito.db")  # caminho final do arquivo do banco


def conectar():
    """Retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)           # abre (ou cria) o arquivo do banco
    conn.execute("PRAGMA foreign_keys = ON")   # liga a checagem de chave estrangeira
    conn.row_factory = sqlite3.Row             # faz as linhas virem acessíveis por nome de coluna
    return conn                                # devolve a conexão pronta pra usar


def criar_tabelas():
    """Cria todas as tabelas do sistema, caso ainda não existam."""
    conn = conectar()          # abre uma conexão
    cursor = conn.cursor()     # cria o cursor, que executa os comandos SQL

    # ---------- Produtos (cadastro de itens) ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT,
            unidade TEXT NOT NULL DEFAULT 'unidade',
            preco_custo REAL NOT NULL DEFAULT 0,
            preco_venda REAL NOT NULL DEFAULT 0,
            estoque_minimo INTEGER NOT NULL DEFAULT 0,
            estoque_atual INTEGER NOT NULL DEFAULT 0,
            data_cadastro TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            ativo INTEGER NOT NULL DEFAULT 1
        )
    """)

    # ---------- Funcionários (cadastro, sem login individual) ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cargo TEXT,
            telefone TEXT,
            data_admissao TEXT,
            ativo INTEGER NOT NULL DEFAULT 1
        )
    """)

    # ---------- Movimentações de estoque (entradas e saídas) ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque_movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL CHECK (tipo IN ('entrada', 'saida')),
            quantidade INTEGER NOT NULL,
            motivo TEXT NOT NULL DEFAULT 'ajuste',
            observacao TEXT,
            data TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    """)

    # ---------- Vendas (cabeçalho) ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            funcionario_id INTEGER,
            total REAL NOT NULL DEFAULT 0,
            forma_pagamento TEXT NOT NULL DEFAULT 'dinheiro',
            status TEXT NOT NULL DEFAULT 'concluida' CHECK (status IN ('concluida', 'cancelada')),
            FOREIGN KEY (funcionario_id) REFERENCES funcionarios (id)
        )
    """)

    # ---------- Itens de cada venda ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venda_id) REFERENCES vendas (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    """)

    # ---------- Despesas ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS despesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            categoria TEXT,
            valor REAL NOT NULL,
            forma_pagamento TEXT,
            data TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # ---------- Perdas (produtos vencidos, quebrados, extraviados) ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS perdas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            motivo TEXT NOT NULL,
            valor_perda REAL NOT NULL DEFAULT 0,
            data TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    """)

    conn.commit()   # grava todas as tabelas criadas acima de vez no arquivo do banco
    conn.close()    # fecha a conexão


if __name__ == "__main__":                                 # só roda se este arquivo for executado direto
    criar_tabelas()                                          # cria as tabelas
    print(f"Banco de dados criado com sucesso em: {DB_PATH}")  # mensagem de confirmação
