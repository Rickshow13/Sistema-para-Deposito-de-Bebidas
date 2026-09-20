import os
import subprocess
import sys
import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
from modules import produtos, vendas, funcionarios
from frames.estilo_tabela import criar_treeview
import comprovante

class VendasFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.carrinho = []
        self._mapa_produtos = {}
        self._mapa_funcionarios = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Nova Venda", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

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
        ctk.CTkButton(linha_add, text="Adicionar", width=90, command=self._adicionar_item).pack(side="left")

        # Ancorar controlos inferiores primeiro para evitar que desapareçam
        painel_inferior = ctk.CTkFrame(painel, fg_color="transparent")
        painel_inferior.pack(side="bottom", fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(painel_inferior, text="Finalizar venda e gerar comprovante", height=40, command=self._finalizar_venda).pack(side="bottom", fill="x", pady=(5, 0))
        self.label_total = ctk.CTkLabel(painel_inferior, text="Total: R$ 0,00", font=ctk.CTkFont(size=18, weight="bold"))
        self.label_total.pack(side="bottom", pady=(10, 5))

        linha_opcoes = ctk.CTkFrame(painel_inferior, fg_color="transparent")
        linha_opcoes.pack(side="bottom", fill="x", pady=5)
        ctk.CTkLabel(linha_opcoes, text="Funcionário:").grid(row=0, column=0, sticky="w")
        self.combo_funcionario = ctk.CTkComboBox(linha_opcoes, values=[], state="readonly")
        self.combo_funcionario.grid(row=0, column=1, sticky="ew", padx=8)
        ctk.CTkLabel(linha_opcoes, text="Pagamento:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.combo_pagamento = ctk.CTkComboBox(linha_opcoes, values=["dinheiro", "cartao", "pix"], state="readonly")
        self.combo_pagamento.grid(row=1, column=1, sticky="ew", padx=8, pady=(8, 0))
        linha_opcoes.grid_columnconfigure(1, weight=1)
        self.combo_pagamento.set("dinheiro")

        ctk.CTkButton(painel_inferior, text="Remover item selecionado", fg_color="gray40", hover_color="gray30", command=self._remover_item).pack(side="bottom", fill="x", pady=(0, 10))

        # Tabela e scrollbar expandem no espaço que sobrar
        container_tabela = ctk.CTkFrame(painel, fg_color="transparent")
        container_tabela.pack(fill="both", expand=True, padx=15, pady=10)
        colunas = ("Produto", "Qtd", "Unit.", "Subtotal")
        self.tabela_carrinho = criar_treeview(container_tabela, colunas, (180, 50, 80, 90))
        scrollbar_carrinho = ttk.Scrollbar(container_tabela, orient="vertical", command=self.tabela_carrinho.yview)
        self.tabela_carrinho.configure(yscrollcommand=scrollbar_carrinho.set)
        self.tabela_carrinho.pack(side="left", fill="both", expand=True)
        scrollbar_carrinho.pack(side="right", fill="y")

    def _montar_historico(self):
        painel = ctk.CTkFrame(self)
        painel.grid(row=1, column=1, sticky="nsew")
        painel.grid_rowconfigure(1, weight=1)
        painel.grid_columnconfigure(0, weight=1)

        linha_topo = ctk.CTkFrame(painel, fg_color="transparent")
        linha_topo.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        ctk.CTkLabel(linha_topo, text="Vendas recentes", font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkButton(linha_topo, text="Exportar p/ Excel", width=120, command=self._exportar_excel).pack(side="right")

        container_tabela = ctk.CTkFrame(painel, fg_color="transparent")
        container_tabela.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)
        colunas = ("ID", "Data", "Funcionário", "Total", "Pagamento", "Status")
        self.tabela_vendas = criar_treeview(container_tabela, colunas, (35, 130, 110, 80, 80, 80))
        scrollbar_vendas = ttk.Scrollbar(container_tabela, orient="vertical", command=self.tabela_vendas.yview)
        self.tabela_vendas.configure(yscrollcommand=scrollbar_vendas.set)
        self.tabela_vendas.pack(side="left", fill="both", expand=True)
        scrollbar_vendas.pack(side="right", fill="y")

        botoes = ctk.CTkFrame(painel, fg_color="transparent")
        botoes.grid(row=2, column=0, sticky="ew", padx=15, pady=(5, 15))
        ctk.CTkButton(botoes, text="Abrir comprovante", command=self._abrir_comprovante).pack(side="left", padx=(0, 8))
        ctk.CTkButton(botoes, text="Cancelar venda", fg_color="#8b2020", hover_color="#6b1818", command=self._cancelar_venda).pack(side="left")

    # Mantenha os métodos atualizar(), _adicionar_item(), _remover_item(), _redesenhar_carrinho(), _finalizar_venda(), _abrir_comprovante() e _cancelar_venda() inalterados do original.
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
        for item in self.carrinho:
            if item["produto_id"] == produto["id"]:
                item["quantidade"] += qtd
                break
        else:
            self.carrinho.append({
                "produto_id": produto["id"], "nome": produto["nome"],
                "quantidade": qtd, "preco_unitario": produto["preco_venda"],
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
        funcionario_id = self._mapa_funcionarios.get(chave_func)
        pagamento = self.combo_pagamento.get()

        try:
            itens = [{"produto_id": i["produto_id"], "quantidade": i["quantidade"]} for i in self.carrinho]
            venda_id, total = vendas.criar_venda(itens, funcionario_id, pagamento)
            venda, itens_venda = vendas.buscar_venda(venda_id)
            caminho_pdf = comprovante.gerar_comprovante_pdf(venda, itens_venda)

            messagebox.showinfo(
                "Venda concluída",
                f"Venda #{venda_id} registrada — total R$ {total:.2f}\nComprovante salvo em:\n{caminho_pdf}"
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
        if messagebox.askyesno("Confirmar", f"Cancelar a venda #{venda_id}?"):
            try:
                vendas.cancelar_venda(venda_id)
                self.atualizar()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

    def _exportar_excel(self):
        try:
            import pandas as pd
        except ImportError:
            messagebox.showerror("Erro", "Instale o pandas (pip install pandas openpyxl)")
            return

        linhas = []
        for child in self.tabela_vendas.get_children():
            linhas.append(self.tabela_vendas.item(child)["values"])
        
        if not linhas:
            return messagebox.showwarning("Aviso", "Não há dados para exportar.")

        df = pd.DataFrame(linhas, columns=["ID", "Data", "Funcionário", "Total", "Pagamento", "Status"])
        caminho = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if caminho:
            df.to_excel(caminho, index=False)
            messagebox.showinfo("Sucesso", "Vendas exportadas com sucesso!")