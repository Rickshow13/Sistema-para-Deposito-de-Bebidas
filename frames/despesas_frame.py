import customtkinter as ctk
from tkinter import messagebox
from modules import despesas
from frames.estilo_tabela import criar_treeview


class DespesasFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self, text="Despesas", font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        painel_tabela = ctk.CTkFrame(self)
        painel_tabela.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        painel_tabela.grid_rowconfigure(0, weight=1)
        painel_tabela.grid_columnconfigure(0, weight=1)

        colunas = ("ID", "Data", "Descrição", "Categoria", "Valor", "Pagamento")
        self.tabela = criar_treeview(painel_tabela, colunas, (40, 100, 180, 110, 90, 100))
        self.tabela.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        painel_form = ctk.CTkFrame(self)
        painel_form.grid(row=1, column=1, sticky="nsew")

        ctk.CTkLabel(painel_form, text="Registrar despesa", font=ctk.CTkFont(weight="bold")).pack(
            padx=15, pady=(15, 10), anchor="w"
        )

        self.campo_descricao = self._campo(painel_form, "Descrição")
        self.campo_categoria = self._campo(painel_form, "Categoria (ex: aluguel, luz)")
        self.campo_valor = self._campo(painel_form, "Valor (R$)")
        self.campo_pagamento = self._campo(painel_form, "Forma de pagamento")

        botoes = ctk.CTkFrame(painel_form, fg_color="transparent")
        botoes.pack(fill="x", padx=15, pady=15)
        ctk.CTkButton(botoes, text="Registrar", command=self._registrar).pack(fill="x", pady=3)
        ctk.CTkButton(
            botoes, text="Excluir selecionada", fg_color="#8b2020", hover_color="#6b1818",
            command=self._excluir
        ).pack(fill="x", pady=3)

        self.atualizar()

    def _campo(self, parent, rotulo):
        ctk.CTkLabel(parent, text=rotulo, font=ctk.CTkFont(size=11)).pack(padx=15, pady=(6, 0), anchor="w")
        entrada = ctk.CTkEntry(parent)
        entrada.pack(fill="x", padx=15, pady=(2, 0))
        return entrada

    def atualizar(self):
        for linha in self.tabela.get_children():
            self.tabela.delete(linha)
        for d in despesas.listar_despesas():
            self.tabela.insert("", "end", iid=d["id"], values=(
                d["id"], d["data"], d["descricao"], d["categoria"] or "-",
                f"R$ {d['valor']:.2f}", d["forma_pagamento"] or "-",
            ))

    def _registrar(self):
        try:
            descricao = self.campo_descricao.get().strip()
            if not descricao:
                raise ValueError("Informe a descrição da despesa")
            categoria = self.campo_categoria.get().strip()
            valor = float(self.campo_valor.get().replace(",", "."))
            pagamento = self.campo_pagamento.get().strip()

            despesas.criar_despesa(descricao, categoria, valor, pagamento)
            messagebox.showinfo("Sucesso", "Despesa registrada!")

            for campo in (self.campo_descricao, self.campo_categoria,
                          self.campo_valor, self.campo_pagamento):
                campo.delete(0, "end")
            self.atualizar()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def _excluir(self):
        selecao = self.tabela.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione uma despesa na tabela")
            return
        despesa_id = int(selecao[0])
        if messagebox.askyesno("Confirmar", "Excluir esta despesa?"):
            despesas.excluir_despesa(despesa_id)
            self.atualizar()
