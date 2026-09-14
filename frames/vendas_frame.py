import os
import subprocess
import sys
import customtkinter as ctk
from tkinter import messagebox
from modules import produtos, vendas, funcionarios
from frames.estilo_tabela import criar_treeview
import comprovante


class VendasFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.carrinho = []  # lista de dicts {produto_id, nome, quantidade, preco_unitario}
        self._mapa_produtos = {}
        self._mapa_funcionarios = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self, text="Nova Venda", font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        self._montar_carrinho()
        self._montar_historico()
        self.atualizar()

    def _montar_carrinho(self):
        painel = ctk.CTkFrame(self)
        painel.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        linha_add = ctk.CTkFrame(painel, fg_color="transparent")
        linha_add.pack(fill="x", padx=15, pady=(15, 5))

        self.combo_produto = ctk.CTkComboBox(linha_add, values=[], state="readonly", width=220)
        self.combo_produto.pack(side="left", padx=(0, 8))

        self.campo_qtd = ctk.CTkEntry(linha_add, placeholder_text="Qtd", width=60)
        self.campo_qtd.pack(side="left", padx=(0, 8))

        ctk.CTkButton(linha_add, text="Adicionar", width=90, command=self._adicionar_item).pack(
            side="left"
        )

        colunas = ("Produto", "Qtd", "Unit.", "Subtotal")
        self.tabela_carrinho = criar_treeview(painel, colunas, (180, 50, 80, 90))
        self.tabela_carrinho.pack(fill="both", expand=True, padx=15, pady=10)

        ctk.CTkButton(
            painel, text="Remover item selecionado", fg_color="gray40", hover_color="gray30",
            command=self._remover_item
        ).pack(fill="x", padx=15, pady=(0, 10))

        linha_opcoes = ctk.CTkFrame(painel, fg_color="transparent")
        linha_opcoes.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(linha_opcoes, text="Funcionário:").grid(row=0, column=0, sticky="w")
        self.combo_funcionario = ctk.CTkComboBox(linha_opcoes, values=[], state="readonly")
        self.combo_funcionario.grid(row=0, column=1, sticky="ew", padx=8)

        ctk.CTkLabel(linha_opcoes, text="Pagamento:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.combo_pagamento = ctk.CTkComboBox(
            linha_opcoes, values=["dinheiro", "cartao", "pix"], state="readonly"
        )
        self.combo_pagamento.grid(row=1, column=1, sticky="ew", padx=8, pady=(8, 0))
        self.combo_pagamento.set("dinheiro")
        linha_opcoes.grid_columnconfigure(1, weight=1)

        self.label_total = ctk.CTkLabel(
            painel, text="Total: R$ 0,00", font=ctk.CTkFont(size=18, weight="bold")
        )
        self.label_total.pack(pady=(10, 5))

        ctk.CTkButton(
            painel, text="Finalizar venda e gerar comprovante", height=40,
            command=self._finalizar_venda
        ).pack(fill="x", padx=15, pady=(5, 15))

    def _montar_historico(self):
        painel = ctk.CTkFrame(self)
        painel.grid(row=1, column=1, sticky="nsew")
        painel.grid_rowconfigure(1, weight=1)
        painel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(painel, text="Vendas recentes", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=15, pady=(15, 5)
        )

        colunas = ("ID", "Data", "Funcionário", "Total", "Pagamento", "Status")
        self.tabela_vendas = criar_treeview(painel, colunas, (35, 130, 110, 80, 80, 80))
        self.tabela_vendas.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)

        botoes = ctk.CTkFrame(painel, fg_color="transparent")
        botoes.grid(row=2, column=0, sticky="ew", padx=15, pady=(5, 15))
        ctk.CTkButton(botoes, text="Abrir comprovante", command=self._abrir_comprovante).pack(
            side="left", padx=(0, 8)
        )
        ctk.CTkButton(
            botoes, text="Cancelar venda", fg_color="#8b2020", hover_color="#6b1818",
            command=self._cancelar_venda
        ).pack(side="left")

    def atualizar(self):
        lista_produtos = produtos.listar_produtos()
        self._mapa_produtos = {
            f"{p['nome']} (R$ {p['preco_venda']:.2f} | estq: {p['estoque_atual']})": p
            for p in lista_produtos
        }
        self.combo_produto.configure(values=list(self._mapa_produtos.keys()))

        lista_func = funcionarios.listar_funcionarios()
        self._mapa_funcionarios = {f["nome"]: f["id"] for f in lista_func}
        opcoes_func = ["(sem funcionário)"] + list(self._mapa_funcionarios.keys())
        self.combo_funcionario.configure(values=opcoes_func)
        if not self.combo_funcionario.get():
            self.combo_funcionario.set("(sem funcionário)")

        for linha in self.tabela_vendas.get_children():
            self.tabela_vendas.delete(linha)
        for v in vendas.listar_vendas():
            self.tabela_vendas.insert("", "end", iid=v["id"], values=(
                v["id"], v["data"], v["funcionario_nome"] or "-",
                f"R$ {v['total']:.2f}", v["forma_pagamento"], v["status"],
            ))

    def _adicionar_item(self):
        chave = self.combo_produto.get()
        if chave not in self._mapa_produtos:
            messagebox.showerror("Erro", "Selecione um produto válido")
            return
        try:
            qtd = int(self.campo_qtd.get())
            if qtd <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Informe uma quantidade válida")
            return

        produto = self._mapa_produtos[chave]

        # Soma se o produto já estiver no carrinho
        for item in self.carrinho:
            if item["produto_id"] == produto["id"]:
                item["quantidade"] += qtd
                break
        else:
            self.carrinho.append({
                "produto_id": produto["id"],
                "nome": produto["nome"],
                "quantidade": qtd,
                "preco_unitario": produto["preco_venda"],
            })

        self.campo_qtd.delete(0, "end")
        self._redesenhar_carrinho()

    def _remover_item(self):
        selecao = self.tabela_carrinho.selection()
        if not selecao:
            return
        indice = self.tabela_carrinho.index(selecao[0])
        del self.carrinho[indice]
        self._redesenhar_carrinho()

    def _redesenhar_carrinho(self):
        for linha in self.tabela_carrinho.get_children():
            self.tabela_carrinho.delete(linha)
        total = 0.0
        for item in self.carrinho:
            subtotal = item["quantidade"] * item["preco_unitario"]
            total += subtotal
            self.tabela_carrinho.insert("", "end", values=(
                item["nome"], item["quantidade"],
                f"R$ {item['preco_unitario']:.2f}", f"R$ {subtotal:.2f}",
            ))
        self.label_total.configure(text=f"Total: R$ {total:.2f}")

    def _finalizar_venda(self):
        if not self.carrinho:
            messagebox.showwarning("Aviso", "Adicione ao menos um item à venda")
            return

        chave_func = self.combo_funcionario.get()
        funcionario_id = self._mapa_funcionarios.get(chave_func)  # None se "(sem funcionário)"
        pagamento = self.combo_pagamento.get()

        try:
            itens = [{"produto_id": i["produto_id"], "quantidade": i["quantidade"]} for i in self.carrinho]
            venda_id, total = vendas.criar_venda(itens, funcionario_id, pagamento)

            venda, itens_venda = vendas.buscar_venda(venda_id)
            caminho_pdf = comprovante.gerar_comprovante_pdf(venda, itens_venda)

            messagebox.showinfo(
                "Venda concluída",
                f"Venda #{venda_id} registrada — total R$ {total:.2f}\n"
                f"Comprovante salvo em:\n{caminho_pdf}"
            )

            self.carrinho = []
            self._redesenhar_carrinho()
            self.atualizar()
        except ValueError as e:
            messagebox.showerror("Erro ao finalizar venda", str(e))

    def _abrir_comprovante(self):
        selecao = self.tabela_vendas.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione uma venda na tabela")
            return
        venda_id = int(selecao[0])
        caminho = os.path.join(comprovante.PASTA_COMPROVANTES, f"venda_{venda_id}.pdf")
        if not os.path.exists(caminho):
            venda, itens = vendas.buscar_venda(venda_id)
            caminho = comprovante.gerar_comprovante_pdf(venda, itens)

        try:
            if sys.platform == "win32":
                os.startfile(caminho)
            elif sys.platform == "darwin":
                subprocess.run(["open", caminho])
            else:
                subprocess.run(["xdg-open", caminho])
        except Exception:
            messagebox.showinfo("Comprovante", f"Arquivo salvo em:\n{caminho}")

    def _cancelar_venda(self):
        selecao = self.tabela_vendas.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione uma venda na tabela")
            return
        venda_id = int(selecao[0])
        if messagebox.askyesno("Confirmar", f"Cancelar a venda #{venda_id}? Os itens voltam ao estoque."):
            try:
                vendas.cancelar_venda(venda_id)
                self.atualizar()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))
