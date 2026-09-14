import customtkinter as ctk
from tkinter import messagebox
from modules import funcionarios
from frames.estilo_tabela import criar_treeview


class FuncionariosFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.funcionario_selecionado_id = None

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self, text="Funcionários", font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        painel_tabela = ctk.CTkFrame(self)
        painel_tabela.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        painel_tabela.grid_rowconfigure(0, weight=1)
        painel_tabela.grid_columnconfigure(0, weight=1)

        colunas = ("ID", "Nome", "Cargo", "Telefone", "Admissão")
        self.tabela = criar_treeview(painel_tabela, colunas, (40, 180, 140, 120, 100))
        self.tabela.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.tabela.bind("<<TreeviewSelect>>", self._ao_selecionar)

        painel_form = ctk.CTkFrame(self)
        painel_form.grid(row=1, column=1, sticky="nsew")

        ctk.CTkLabel(painel_form, text="Cadastro / Edição", font=ctk.CTkFont(weight="bold")).pack(
            padx=15, pady=(15, 10), anchor="w"
        )

        self.campo_nome = self._campo(painel_form, "Nome")
        self.campo_cargo = self._campo(painel_form, "Cargo")
        self.campo_telefone = self._campo(painel_form, "Telefone")
        self.campo_admissao = self._campo(painel_form, "Data de admissão (AAAA-MM-DD)")

        botoes = ctk.CTkFrame(painel_form, fg_color="transparent")
        botoes.pack(fill="x", padx=15, pady=15)
        ctk.CTkButton(botoes, text="Salvar", command=self._salvar).pack(fill="x", pady=3)
        ctk.CTkButton(
            botoes, text="Limpar", fg_color="gray40", hover_color="gray30",
            command=self._limpar
        ).pack(fill="x", pady=3)
        ctk.CTkButton(
            botoes, text="Desativar", fg_color="#8b2020", hover_color="#6b1818",
            command=self._desativar
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
        for f in funcionarios.listar_funcionarios():
            self.tabela.insert("", "end", iid=f["id"], values=(
                f["id"], f["nome"], f["cargo"] or "-", f["telefone"] or "-",
                f["data_admissao"] or "-",
            ))

    def _ao_selecionar(self, event):
        selecao = self.tabela.selection()
        if not selecao:
            return
        funcionario_id = int(selecao[0])
        lista = funcionarios.listar_funcionarios(apenas_ativos=False)
        f = next((x for x in lista if x["id"] == funcionario_id), None)
        if f is None:
            return
        self.funcionario_selecionado_id = funcionario_id
        self.campo_nome.delete(0, "end"); self.campo_nome.insert(0, f["nome"])
        self.campo_cargo.delete(0, "end"); self.campo_cargo.insert(0, f["cargo"] or "")
        self.campo_telefone.delete(0, "end"); self.campo_telefone.insert(0, f["telefone"] or "")
        self.campo_admissao.delete(0, "end"); self.campo_admissao.insert(0, f["data_admissao"] or "")

    def _limpar(self):
        self.funcionario_selecionado_id = None
        for campo in (self.campo_nome, self.campo_cargo, self.campo_telefone, self.campo_admissao):
            campo.delete(0, "end")
        self.tabela.selection_remove(self.tabela.selection())

    def _salvar(self):
        nome = self.campo_nome.get().strip()
        if not nome:
            messagebox.showerror("Erro", "Informe o nome do funcionário")
            return
        cargo = self.campo_cargo.get().strip()
        telefone = self.campo_telefone.get().strip()
        admissao = self.campo_admissao.get().strip()

        if self.funcionario_selecionado_id is None:
            funcionarios.criar_funcionario(nome, cargo, telefone, admissao)
            messagebox.showinfo("Sucesso", "Funcionário cadastrado!")
        else:
            funcionarios.atualizar_funcionario(
                self.funcionario_selecionado_id, nome, cargo, telefone, admissao
            )
            messagebox.showinfo("Sucesso", "Funcionário atualizado!")

        self._limpar()
        self.atualizar()

    def _desativar(self):
        if self.funcionario_selecionado_id is None:
            messagebox.showwarning("Aviso", "Selecione um funcionário na tabela")
            return
        if messagebox.askyesno("Confirmar", "Desativar este funcionário?"):
            funcionarios.desativar_funcionario(self.funcionario_selecionado_id)
            self._limpar()
            self.atualizar()
