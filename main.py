"""
main.py
Ponto de entrada do sistema. Monta a janela principal com um menu lateral
que troca entre as telas de cada módulo (Produtos, Estoque, Vendas,
Funcionários, Despesas, Perdas, Relatórios).
"""

import customtkinter as ctk
import database

from frames.produtos_frame import ProdutosFrame
from frames.estoque_frame import EstoqueFrame
from frames.vendas_frame import VendasFrame
from frames.funcionarios_frame import FuncionariosFrame
from frames.despesas_frame import DespesasFrame
from frames.perdas_frame import PerdasFrame
from frames.relatorios_frame import RelatoriosFrame

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Depósito de Bebidas")
        self.geometry("1150x680")
        self.minsize(1000, 600)

        # Layout: sidebar fixa + área de conteúdo que troca de tela
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._montar_sidebar()

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Instancia todas as telas de uma vez e troca a visível com .tkraise()
        self.frames = {}
        for Tela in (ProdutosFrame, EstoqueFrame, VendasFrame,
                     FuncionariosFrame, DespesasFrame, PerdasFrame,
                     RelatoriosFrame):
            frame = Tela(self.container, self)
            self.frames[Tela.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.mostrar_tela("VendasFrame")

    def _montar_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=210, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar, text="🍺 Depósito", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(padx=20, pady=(25, 30), anchor="w")

        botoes = [
            ("Vendas", "VendasFrame"),
            ("Produtos", "ProdutosFrame"),
            ("Estoque", "EstoqueFrame"),
            ("Funcionários", "FuncionariosFrame"),
            ("Despesas", "DespesasFrame"),
            ("Perdas", "PerdasFrame"),
            ("Relatórios / Lucro", "RelatoriosFrame"),
        ]

        for texto, nome_tela in botoes:
            btn = ctk.CTkButton(
                sidebar, text=texto, anchor="w", corner_radius=6,
                fg_color="transparent", hover_color=("gray75", "gray25"),
                command=lambda n=nome_tela: self.mostrar_tela(n)
            )
            btn.pack(fill="x", padx=12, pady=4)

    def mostrar_tela(self, nome_tela):
        frame = self.frames[nome_tela]
        frame.tkraise()
        if hasattr(frame, "atualizar"):
            frame.atualizar()


if __name__ == "__main__":
    database.criar_tabelas()
    app = App()
    app.mainloop()
