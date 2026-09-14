import customtkinter as ctk
from tkinter import messagebox
from modules import relatorios
from frames.estilo_tabela import criar_treeview


class RelatoriosFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            self, text="Relatórios / Lucro", font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 15))

        painel_filtro = ctk.CTkFrame(self)
        painel_filtro.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        ctk.CTkLabel(painel_filtro, text="De (AAAA-MM-DD):").pack(side="left", padx=(15, 5), pady=15)
        self.campo_data_inicio = ctk.CTkEntry(painel_filtro, width=120, placeholder_text="opcional")
        self.campo_data_inicio.pack(side="left", padx=5)

        ctk.CTkLabel(painel_filtro, text="Até (AAAA-MM-DD):").pack(side="left", padx=(15, 5))
        self.campo_data_fim = ctk.CTkEntry(painel_filtro, width=120, placeholder_text="opcional")
        self.campo_data_fim.pack(side="left", padx=5)

        ctk.CTkButton(painel_filtro, text="Calcular", command=self.atualizar).pack(
            side="left", padx=15
        )

        painel_cards = ctk.CTkFrame(self, fg_color="transparent")
        painel_cards.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        for i in range(4):
            painel_cards.grid_columnconfigure(i, weight=1)

        self.card_vendas = self._card(painel_cards, 0, "Vendas", "#1f6aa5")
        self.card_despesas = self._card(painel_cards, 1, "Despesas", "#8b4513")
        self.card_perdas = self._card(painel_cards, 2, "Perdas", "#8b2020")
        self.card_lucro = self._card(painel_cards, 3, "Lucro líquido", "#2d6a2d")

        painel_ranking = ctk.CTkFrame(self)
        painel_ranking.grid(row=3, column=0, sticky="nsew")
        painel_ranking.grid_rowconfigure(1, weight=1)
        painel_ranking.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            painel_ranking, text="Produtos mais vendidos no período",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))

        colunas = ("Produto", "Quantidade vendida", "Valor total")
        self.tabela_ranking = criar_treeview(painel_ranking, colunas, (250, 160, 140))
        self.tabela_ranking.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

        self.atualizar()

    def _card(self, parent, coluna, titulo, cor):
        frame = ctk.CTkFrame(parent, fg_color=cor, corner_radius=10)
        frame.grid(row=0, column=coluna, sticky="ew", padx=6)
        ctk.CTkLabel(frame, text=titulo, font=ctk.CTkFont(size=12)).pack(padx=15, pady=(12, 2))
        valor = ctk.CTkLabel(frame, text="R$ 0,00", font=ctk.CTkFont(size=18, weight="bold"))
        valor.pack(padx=15, pady=(0, 12))
        return valor

    def atualizar(self):
        data_inicio = self.campo_data_inicio.get().strip() or None
        data_fim = self.campo_data_fim.get().strip() or None

        try:
            resultado = relatorios.calcular_lucro(data_inicio, data_fim)
        except Exception as e:
            messagebox.showerror("Erro", f"Data inválida: {e}")
            return

        self.card_vendas.configure(text=f"R$ {resultado['vendas']:.2f}")
        self.card_despesas.configure(text=f"R$ {resultado['despesas']:.2f}")
        self.card_perdas.configure(text=f"R$ {resultado['perdas']:.2f}")
        self.card_lucro.configure(text=f"R$ {resultado['lucro']:.2f}")

        for linha in self.tabela_ranking.get_children():
            self.tabela_ranking.delete(linha)
        for item in relatorios.produtos_mais_vendidos(data_inicio, data_fim):
            self.tabela_ranking.insert("", "end", values=(
                item["nome"], item["quantidade_total"], f"R$ {item['valor_total']:.2f}",
            ))
