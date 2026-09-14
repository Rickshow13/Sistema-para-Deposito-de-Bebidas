# Sistema de Depósito de Bebidas

Sistema desktop completo para gestão de um depósito de bebidas: controle de
estoque, vendas com emissão de comprovante em PDF, funcionários, despesas,
perdas e relatório de lucro por período.

## Requisitos

- Python 3.10 ou superior instalado no computador
- No Linux, o pacote `python3-tk` (no Windows e macOS o Tkinter já vem
  junto com o Python, não precisa instalar nada extra)

## Instalação

1. Extraia esta pasta em qualquer lugar do seu computador.
2. Abra um terminal (ou Prompt de Comando) dentro da pasta `deposito_bebidas`.
3. Instale as dependências:

   ```
   pip install -r requirements.txt
   ```

   Se aparecer erro parecido com "No module named tkinter" no Linux, rode
   antes: `sudo apt-get install python3-tk`

## Como usar

Para abrir o sistema, rode:

```
python main.py
```

Na primeira vez que você rodar, o sistema cria automaticamente o arquivo
`deposito.db` (o banco de dados) na mesma pasta — não precisa configurar
nada.

### Fluxo recomendado na primeira utilização

1. Vá em **Produtos** e cadastre os itens do seu depósito (nome, categoria,
   preço de custo, preço de venda, estoque mínimo e estoque inicial).
2. Vá em **Funcionários** e cadastre quem trabalha no depósito (não tem
   login/senha — é só um cadastro de referência, usado pra saber quem
   registrou cada venda).
3. Use a tela **Vendas** para registrar vendas: escolha os produtos,
   quantidades, forma de pagamento e finalize. O comprovante em PDF é
   gerado automaticamente e salvo na pasta `comprovantes/`.
4. Use **Estoque** para registrar entradas (reposição de mercadoria) e
   ajustes manuais.
5. Use **Despesas** para lançar custos do depósito (aluguel, água, luz,
   fornecedores etc).
6. Use **Perdas** para registrar produtos vencidos, quebrados ou
   extraviados — o valor da perda é calculado automaticamente pelo preço
   de custo, mas você pode informar um valor manual se quiser.
7. Use **Relatórios / Lucro** para ver o lucro líquido do período
   (vendas − despesas − perdas) e o ranking de produtos mais vendidos.
   Deixe as datas em branco para ver o total geral, ou preencha
   "De" / "Até" no formato AAAA-MM-DD para filtrar um período.

## Estrutura do projeto

```
deposito_bebidas/
├── main.py                  # Ponto de entrada — abre a janela do sistema
├── database.py               # Conexão e criação das tabelas do banco
├── comprovante.py             # Geração do comprovante de venda em PDF
├── requirements.txt
├── modules/                   # Regras de negócio (nada de interface aqui)
│   ├── produtos.py
│   ├── estoque.py
│   ├── vendas.py
│   ├── funcionarios.py
│   ├── despesas.py
│   ├── perdas.py
│   └── relatorios.py
└── frames/                    # Telas da interface gráfica (CustomTkinter)
    ├── vendas_frame.py
    ├── produtos_frame.py
    ├── estoque_frame.py
    ├── funcionarios_frame.py
    ├── despesas_frame.py
    ├── perdas_frame.py
    ├── relatorios_frame.py
    └── estilo_tabela.py
```

## Observações técnicas

- **Banco de dados:** SQLite (arquivo único `deposito.db`, sem precisar
  instalar servidor nenhum). Se quiser migrar para MySQL no futuro (por
  exemplo, pra acessar de mais de um computador na rede), a lógica em
  `modules/` está isolada da interface — é uma troca localizada em
  `database.py`.
- **Lucro:** não é armazenado em tabela — é sempre calculado na hora,
  cruzando vendas concluídas, despesas e perdas do período escolhido.
  Isso evita que o número fique desatualizado.
- **Estoque:** toda operação que mexe no estoque (venda, perda, entrada
  manual) atualiza o campo `estoque_atual` do produto e grava um
  registro no histórico de movimentações, então dá pra auditar tudo
  depois.
- **Backup:** como é tudo um arquivo SQLite só, pra fazer backup basta
  copiar o arquivo `deposito.db` pra outro lugar de vez em quando.
