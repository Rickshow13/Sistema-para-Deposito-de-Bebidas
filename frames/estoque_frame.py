import customtkinter as ctk
from tkinter import messagebox
from modules import produtos, estoque
from frames.estilo_tabela import criar_treeview


class EstoqueFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self, text="Controle de Estoque", font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        self._montar_tabela()
        self._montar_formulario()
        self.atualizar()

    def _montar_tabela(self):
        painel = ctk.CTkFrame(self)
        painel.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        painel.grid_rowconfigure(0, weight=1)
        painel.grid_columnconfigure(0, weight=1)

        colunas = ("Data", "Produto", "Tipo", "Qtd", "Motivo", "Observação")
        larguras = (140, 200, 70, 50, 90, 200)
        self.tabela = criar_treeview(painel, colunas, larguras)
        self.tabela.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

    def _montar_formulario(self):
        painel = ctk.CTkFrame(self)
        painel.grid(row=1, column=1, sticky="nsew")

        ctk.CTkLabel(
            painel, text="Movimentação manual", font=ctk.CTkFont(weight="bold")
        ).pack(padx=15, pady=(15, 10), anchor="w")

        ctk.CTkLabel(painel, text="Produto", font=ctk.CTkFont(size=11)).pack(
            padx=15, anchor="w"
        )
        self.combo_produto = ctk.CTkComboBox(painel, values=[], state="readonly")
        self.combo_produto.pack(fill="x", padx=15, pady=(2, 0))

        ctk.CTkLabel(painel, text="Tipo", font=ctk.CTkFont(size=11)).pack(
            padx=15, pady=(8, 0), anchor="w"
        )
        self.combo_tipo = ctk.CTkComboBox(painel, values=["entrada", "saida"], state="readonly")
        self.combo_tipo.pack(fill="x", padx=15, pady=(2, 0))

        ctk.CTkLabel(painel, text="Quantidade", font=ctk.CTkFont(size=11)).pack(
            padx=15, pady=(8, 0), anchor="w"
        )
        self.campo_quantidade = ctk.CTkEntry(painel)
        self.campo_quantidade.pack(fill="x", padx=15, pady=(2, 0))

        ctk.CTkLabel(painel, text="Motivo (ex: compra, ajuste)", font=ctk.CTkFont(size=11)).pack(
            padx=15, pady=(8, 0), anchor="w"
        )
        self.campo_motivo = ctk.CTkEntry(painel)
        self.campo_motivo.pack(fill="x", padx=15, pady=(2, 0))

        ctk.CTkLabel(painel, text="Observação (opcional)", font=ctk.CTkFont(size=11)).pack(
            padx=15, pady=(8, 0), anchor="w"
        )
        self.campo_obs = ctk.CTkEntry(painel)
        self.campo_obs.pack(fill="x", padx=15, pady=(2, 0))

        ctk.CTkButton(painel, text="Registrar movimentação", command=self._registrar).pack(
            fill="x", padx=15, pady=20
        )

        self._mapa_produtos = {}

    def atualizar(self):
        # Atualiza combo de produtos
        lista = produtos.listar_produtos()
        self._mapa_produtos = {f"{p['nome']} (estoque: {p['estoque_atual']})": p["id"] for p in lista}
        self.combo_produto.configure(values=list(self._mapa_produtos.keys()))

        # Atualiza tabela de histórico
        for linha in self.tabela.get_children():
            self.tabela.delete(linha)
        for m in estoque.historico_geral():
            self.tabela.insert("", "end", values=(
                m["data"], m["produto_nome"], m["tipo"], m["quantidade"],
                m["motivo"], m["observacao"] or "-",
            ))

    def _registrar(self):
        try:
            chave_produto = self.combo_produto.get()
            if chave_produto not in self._mapa_produtos:
                raise ValueError("Selecione um produto válido")
            produto_id = self._mapa_produtos[chave_produto]

            tipo = self.combo_tipo.get()
            if tipo not in ("entrada", "saida"):
                raise ValueError("Selecione o tipo de movimentação")

            quantidade = int(self.campo_quantidade.get())
            motivo = self.campo_motivo.get().strip() or "ajuste"
            obs = self.campo_obs.get().strip() or None

            estoque.registrar_movimentacao(produto_id, tipo, quantidade, motivo, obs)
            messagebox.showinfo("Sucesso", "Movimentação registrada!")

            self.campo_quantidade.delete(0, "end")
            self.campo_motivo.delete(0, "end")
            self.campo_obs.delete(0, "end")
            self.atualizar()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
