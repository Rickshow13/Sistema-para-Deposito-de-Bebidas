import customtkinter as ctk
from tkinter import messagebox
from modules import produtos, perdas
from frames.estilo_tabela import criar_treeview


class PerdasFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._mapa_produtos = {}

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self, text="Perdas", font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        painel_tabela = ctk.CTkFrame(self)
        painel_tabela.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        painel_tabela.grid_rowconfigure(0, weight=1)
        painel_tabela.grid_columnconfigure(0, weight=1)

        colunas = ("ID", "Data", "Produto", "Qtd", "Motivo", "Valor perdido")
        self.tabela = criar_treeview(painel_tabela, colunas, (40, 100, 180, 50, 130, 100))
        self.tabela.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        painel_form = ctk.CTkFrame(self)
        painel_form.grid(row=1, column=1, sticky="nsew")

        ctk.CTkLabel(painel_form, text="Registrar perda", font=ctk.CTkFont(weight="bold")).pack(
            padx=15, pady=(15, 10), anchor="w"
        )

        ctk.CTkLabel(painel_form, text="Produto", font=ctk.CTkFont(size=11)).pack(
            padx=15, anchor="w"
        )
        self.combo_produto = ctk.CTkComboBox(painel_form, values=[], state="readonly")
        self.combo_produto.pack(fill="x", padx=15, pady=(2, 0))

        self.campo_quantidade = self._campo(painel_form, "Quantidade perdida")
        self.campo_motivo = self._campo(painel_form, "Motivo (ex: vencido, quebrado)")
        self.campo_valor = self._campo(
            painel_form, "Valor da perda (R$) — opcional, calcula automático"
        )

        ctk.CTkButton(painel_form, text="Registrar perda", command=self._registrar).pack(
            fill="x", padx=15, pady=20
        )

        self.atualizar()

    def _campo(self, parent, rotulo):
        ctk.CTkLabel(parent, text=rotulo, font=ctk.CTkFont(size=11)).pack(padx=15, pady=(8, 0), anchor="w")
        entrada = ctk.CTkEntry(parent)
        entrada.pack(fill="x", padx=15, pady=(2, 0))
        return entrada

    def atualizar(self):
        lista = produtos.listar_produtos()
        self._mapa_produtos = {f"{p['nome']} (estoque: {p['estoque_atual']})": p["id"] for p in lista}
        self.combo_produto.configure(values=list(self._mapa_produtos.keys()))

        for linha in self.tabela.get_children():
            self.tabela.delete(linha)
        for p in perdas.listar_perdas():
            self.tabela.insert("", "end", values=(
                p["id"], p["data"], p["produto_nome"], p["quantidade"],
                p["motivo"], f"R$ {p['valor_perda']:.2f}",
            ))

    def _registrar(self):
        try:
            chave = self.combo_produto.get()
            if chave not in self._mapa_produtos:
                raise ValueError("Selecione um produto válido")
            produto_id = self._mapa_produtos[chave]

            quantidade = int(self.campo_quantidade.get())
            motivo = self.campo_motivo.get().strip()
            if not motivo:
                raise ValueError("Informe o motivo da perda")

            texto_valor = self.campo_valor.get().strip()
            valor_perda = float(texto_valor.replace(",", ".")) if texto_valor else None

            perdas.registrar_perda(produto_id, quantidade, motivo, valor_perda)
            messagebox.showinfo("Sucesso", "Perda registrada e estoque atualizado!")

            self.campo_quantidade.delete(0, "end")
            self.campo_motivo.delete(0, "end")
            self.campo_valor.delete(0, "end")
            self.atualizar()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
