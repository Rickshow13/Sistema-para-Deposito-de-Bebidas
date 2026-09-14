import customtkinter as ctk
from tkinter import messagebox
from modules import produtos
from frames.estilo_tabela import criar_treeview


class ProdutosFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.produto_selecionado_id = None

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self, text="Produtos", font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        self._montar_tabela()
        self._montar_formulario()
        self.atualizar()

    def _montar_tabela(self):
        painel = ctk.CTkFrame(self)
        painel.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        painel.grid_rowconfigure(0, weight=1)
        painel.grid_columnconfigure(0, weight=1)

        colunas = ("ID", "Nome", "Categoria", "Unid.", "Custo", "Venda", "Estoque", "Mínimo")
        larguras = (40, 200, 110, 60, 70, 70, 70, 70)
        self.tabela = criar_treeview(painel, colunas, larguras)
        self.tabela.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.tabela.bind("<<TreeviewSelect>>", self._ao_selecionar)

    def _montar_formulario(self):
        painel = ctk.CTkFrame(self)
        painel.grid(row=1, column=1, sticky="nsew")

        ctk.CTkLabel(painel, text="Cadastro / Edição", font=ctk.CTkFont(weight="bold")).pack(
            padx=15, pady=(15, 10), anchor="w"
        )

        self.campo_nome = self._campo(painel, "Nome do produto")
        self.campo_categoria = self._campo(painel, "Categoria (ex: Cerveja)")
        self.campo_unidade = self._campo(painel, "Unidade (ex: unidade, caixa)")
        self.campo_custo = self._campo(painel, "Preço de custo (R$)")
        self.campo_venda = self._campo(painel, "Preço de venda (R$)")
        self.campo_minimo = self._campo(painel, "Estoque mínimo")
        self.campo_inicial = self._campo(painel, "Estoque inicial (só na criação)")

        botoes = ctk.CTkFrame(painel, fg_color="transparent")
        botoes.pack(fill="x", padx=15, pady=15)

        ctk.CTkButton(botoes, text="Salvar", command=self._salvar).pack(fill="x", pady=3)
        ctk.CTkButton(
            botoes, text="Limpar", fg_color="gray40", hover_color="gray30",
            command=self._limpar_formulario
        ).pack(fill="x", pady=3)
        ctk.CTkButton(
            botoes, text="Desativar produto", fg_color="#8b2020", hover_color="#6b1818",
            command=self._desativar
        ).pack(fill="x", pady=3)

    def _campo(self, parent, rotulo):
        ctk.CTkLabel(parent, text=rotulo, font=ctk.CTkFont(size=11)).pack(
            padx=15, pady=(6, 0), anchor="w"
        )
        entrada = ctk.CTkEntry(parent)
        entrada.pack(fill="x", padx=15, pady=(2, 0))
        return entrada

    def atualizar(self):
        for linha in self.tabela.get_children():
            self.tabela.delete(linha)
        for p in produtos.listar_produtos():
            self.tabela.insert("", "end", iid=p["id"], values=(
                p["id"], p["nome"], p["categoria"] or "-", p["unidade"],
                f"R$ {p['preco_custo']:.2f}", f"R$ {p['preco_venda']:.2f}",
                p["estoque_atual"], p["estoque_minimo"],
            ))

    def _ao_selecionar(self, event):
        selecao = self.tabela.selection()
        if not selecao:
            return
        produto_id = int(selecao[0])
        p = produtos.buscar_produto(produto_id)
        if p is None:
            return
        self.produto_selecionado_id = produto_id
        self.campo_nome.delete(0, "end"); self.campo_nome.insert(0, p["nome"])
        self.campo_categoria.delete(0, "end"); self.campo_categoria.insert(0, p["categoria"] or "")
        self.campo_unidade.delete(0, "end"); self.campo_unidade.insert(0, p["unidade"])
        self.campo_custo.delete(0, "end"); self.campo_custo.insert(0, str(p["preco_custo"]))
        self.campo_venda.delete(0, "end"); self.campo_venda.insert(0, str(p["preco_venda"]))
        self.campo_minimo.delete(0, "end"); self.campo_minimo.insert(0, str(p["estoque_minimo"]))
        self.campo_inicial.configure(state="disabled")

    def _limpar_formulario(self):
        self.produto_selecionado_id = None
        for campo in (self.campo_nome, self.campo_categoria, self.campo_unidade,
                      self.campo_custo, self.campo_venda, self.campo_minimo):
            campo.delete(0, "end")
        self.campo_inicial.configure(state="normal")
        self.campo_inicial.delete(0, "end")
        self.tabela.selection_remove(self.tabela.selection())

    def _salvar(self):
        try:
            nome = self.campo_nome.get().strip()
            if not nome:
                raise ValueError("Informe o nome do produto")
            categoria = self.campo_categoria.get().strip()
            unidade = self.campo_unidade.get().strip() or "unidade"
            custo = float(self.campo_custo.get().replace(",", ".") or 0)
            venda = float(self.campo_venda.get().replace(",", ".") or 0)
            minimo = int(self.campo_minimo.get() or 0)

            if self.produto_selecionado_id is None:
                inicial = int(self.campo_inicial.get() or 0)
                produtos.criar_produto(nome, categoria, unidade, custo, venda, minimo, inicial)
                messagebox.showinfo("Sucesso", "Produto cadastrado!")
            else:
                produtos.atualizar_produto(
                    self.produto_selecionado_id, nome, categoria, unidade, custo, venda, minimo
                )
                messagebox.showinfo("Sucesso", "Produto atualizado!")

            self._limpar_formulario()
            self.atualizar()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def _desativar(self):
        if self.produto_selecionado_id is None:
            messagebox.showwarning("Aviso", "Selecione um produto na tabela primeiro")
            return
        if messagebox.askyesno("Confirmar", "Desativar este produto? O histórico é mantido."):
            produtos.desativar_produto(self.produto_selecionado_id)
            self._limpar_formulario()
            self.atualizar()
