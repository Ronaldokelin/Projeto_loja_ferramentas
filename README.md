# 🛠️ Loja de Ferramentas — Aplicativo Web com Flask

Um projeto de site simples para vendas de ferramentas, com funcionalidades de catálogo, carrinho de compras, cadastro de clientes e geração de orçamento em PDF com redirecionamento para o WhatsApp.

---

## ✅ Funcionalidades incluídas
🧰 Funcionalidades Incluídas
| Funcionalidade | Descrição | 
| 🏠 Página Inicial | Interface com cabeçalho, navegação e rodapé estilizados | 
| 🔐 Login e Logout de Admin | Autenticação para painel administrativo com sessão | 
| 🧍 Cadastro de Cliente | Formulário de nome, e-mail e senha para novos usuários | 
| 📞 Formulário de Contato | Coleta nome, e-mail e mensagem — com feedback visual | 
| 📦 Cadastro de Produtos | Adição de produtos com nome, descrição, preço e até 5 imagens | 
| 🖼️ Preview de Imagens | Visualização em tempo real das imagens antes de salvar | 
| 🔁 Rotação de Imagens (visual) | Botão para girar cada imagem no navegador antes do upload | 
| 📤 Upload com Pillow | Redimensionamento para 800×600 e conversão para .jpg | 
| 🛒 Catálogo com Galeria | Carrossel com todas as imagens por produto + miniaturas + contador | 
| 🛍️ Carrinho com Quantidade | Adição, aumento, diminuição e remoção de produtos com subtotal | 
| 📄 Geração de PDF do Pedido | Orçamento final com todos os produtos e valor total | 
| 📱 Envio via WhatsApp | Redirecionamento com link direto para abrir PDF no WhatsApp | 
| 🛠️ Painel Admin | Listagem dos produtos cadastrados com imagem, preço e botões de ação | 
| ✏️ Edição de Produto | Formulário para atualizar nome, descrição e preço | 
| 🗑️ Exclusão de Produto | Confirmação e remoção completa de produto do sistema | 

para evoluir mais, sugerir:
- 🔎 Busca por nome ou categoria
- 📆 Registro de data de cadastro
- 🧮 Estoque e controle de quantidade disponível
- 🌐 Deploy online no Render ou Railway


## 📁 Estrutura do Projeto

loja_ferramentas│
├── app.py                            # Arquivo principal da aplicação Flask
├── produtos.db                       # Banco de dados SQLite (gerado automaticamente)
├── requirements.txt                  # Lista de dependências (opcional para deploy)
│
├── static/                           # Arquivos estáticos (imagens, PDFs, CSS, JS)
│   ├── imagens/                      # Imagens dos produtos
│   └── orcamento_*.pdf               # PDFs gerados com orçamento
│
├── templates/                        # Arquivos HTML
│   ├── base.html                     # Template base com Bootstrap e estrutura comum
│   ├── index.html                    # Página inicial
│   ├── login.html                    # Tela de login do administrador
│   ├── cadastro.html                 # Formulário de cadastro do cliente
│   ├── contato.html                  # Página de contato
│   ├── produtos.html                 # Catálogo com galeria de imagens
│   ├── carrinho.html                 # Visualização e controle do carrinho
│   ├── painel_admin.html             # Painel administrativo com cadastro e listagem
│   └── editar_produto.html          # Formulário para editar produto existente
│
├── utils/                            # Funções auxiliares
│   └── pdf_generator.py              # Função gerar_pdf(cliente, produtos, total, caminho)
│
└── README.md  

## ⚙️ Instalação e Configuração

### 1. Clonar o repositório e criar ambiente virtual

```bash
python -m venv venv_loja
venv_loja\Scripts\activate     # Windows
source venv_loja/bin/activate   # Linux/Mac
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Criar o banco de dados
Crie um arquivo de inicialização que crie as tabelas:
- produtos
- clientes
Ou use um script separado para criar produtos.db.

### 4. Geração de PDF de orçamento
Após o cliente confirmar o pedido, o sistema:
- Gera um arquivo PDF com a lista de itens selecionados, valor total e dados do cliente.
- Salva o PDF na pasta static/
- Redireciona para o número de WhatsApp (5512345678) com a mensagem pronta.

### 5. Como rodar o app
```bash
python app.py
```
Acesse no navegador: http://localhost:5000

### 6. Rodar em modo desenvolvimento (opcional)
```bash
set FLASK_ENV=development  # Windows
export FLASK_ENV=development  # Linux/Mac
python app.py
```

### 7. Variáveis de ambiente
Se desejar, crie um arquivo `.env` para definir variáveis como `SECRET_KEY` e limite de upload.

### 8. Exemplo de uso
1. Cadastre um cliente.
2. Adicione produtos ao carrinho.
3. Finalize o pedido e gere o PDF.
4. O PDF será salvo em `static/` e o WhatsApp será aberto com a mensagem pronta.

---

## 📸 Screenshots
Adicione aqui imagens das principais telas do sistema para ilustrar o funcionamento.

---

## 🤝 Como contribuir
1. Faça um fork do projeto
2. Crie uma branch: `git checkout -b minha-feature`
3. Commit suas alterações: `git commit -m 'Minha nova feature'`
4. Push para o fork: `git push origin minha-feature`
5. Abra um Pull Request

---

## 📄 Licença
Este projeto está licenciado sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

## 📬 Contato
Dúvidas ou sugestões? Envie um e-mail para seuemail@exemplo.com ou abra uma issue no repositório.

📌 Próximas funcionalidades sugeridas
- Área administrativa completa com login
- Edição e exclusão de produtos via navegador
- Histórico de pedidos por cliente
- Adicionar controle de quantidade no carrinho
- Layout responsivo com CSS estilizado
- Integração com armazenamento em nuvem para PDFs (opcional)

💡 Desenvolvido com
- Python 3
- Flask
- SQLite
- ReportLab