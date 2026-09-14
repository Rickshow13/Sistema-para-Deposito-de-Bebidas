"""
frames/estilo_tabela.py
CustomTkinter não tem um widget de tabela nativo, então usamos o
ttk.Treeview do próprio tkinter para listar dados — mas ajustamos o
estilo dele pra combinar com o tema escuro do resto do app.
"""

from tkinter import ttk


def aplicar_estilo_treeview():
    estilo = ttk.Style()
    estilo.theme_use("default")

    estilo.configure(
        "Custom.Treeview",
        background="#2b2b2b",
        foreground="white",
        fieldbackground="#2b2b2b",
        rowheight=28,
        borderwidth=0,
        font=("Segoe UI", 11),
    )
    estilo.configure(
        "Custom.Treeview.Heading",
        background="#1f6aa5",
        foreground="white",
        font=("Segoe UI", 11, "bold"),
        borderwidth=0,
    )
    estilo.map(
        "Custom.Treeview",
        background=[("selected", "#144870")],
        foreground=[("selected", "white")],
    )
    return estilo


def criar_treeview(parent, colunas, larguras=None):
    """Cria e retorna um ttk.Treeview já estilizado, com as colunas informadas."""
    aplicar_estilo_treeview()
    tree = ttk.Treeview(
        parent, columns=colunas, show="headings", style="Custom.Treeview"
    )
    for i, coluna in enumerate(colunas):
        tree.heading(coluna, text=coluna)
        largura = larguras[i] if larguras else 120
        tree.column(coluna, width=largura, anchor="w")
    return tree
