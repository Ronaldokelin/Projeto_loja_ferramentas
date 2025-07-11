from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
import sqlite3, os, urllib.parse
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
from utils.pdf_generator import gerar_pdf
import re
from werkzeug.security import generate_password_hash, check_password_hash
import glob

# =========================
# Configuração do Flask e utilitários
# =========================

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sua_chave_secreta_aqui')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Limite de 2MB para upload

def conectar_banco():
    return sqlite3.connect('produtos.db')

# =========================
# Rotas Públicas
# =========================

@app.route('/')
def index():
    """Página inicial com produtos em destaque"""
    destaques = []
    try:
        with conectar_banco() as con:
            cur = con.cursor()
            # Seleciona até 4 produtos com maior estoque ou mais recentes
            cur.execute('SELECT id, nome, descricao, preco, imagem FROM produtos ORDER BY estoque DESC, id DESC LIMIT 4')
            destaques = cur.fetchall()
    except Exception:
        destaques = []
    return render_template('index.html', current_year=datetime.now().year, destaques=destaques)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login de admin e cliente"""
    if request.method == 'POST':
        usuario = request.form['usuario'].strip()
        senha = request.form['senha'].strip()
        if not usuario or not senha:
            flash('Preencha todos os campos.', 'warning')
            return redirect(url_for('login'))
        if usuario == 'admin' and senha == 'senha123':
            session['admin_logado'] = True
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin'))
        else:
            try:
                with conectar_banco() as con:
                    cur = con.cursor()
                    cur.execute('SELECT senha, nome, sobrenome, email FROM clientes WHERE email = ?', (usuario,))
                    row = cur.fetchone()
                if row and check_password_hash(row[0], senha):
                    session['cliente_logado'] = True
                    session['usuario_email'] = row[3]
                    session['usuario_nome'] = f"{row[1]} {row[2]}"
                    flash('Login de cliente realizado com sucesso!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Credenciais inválidas.', 'danger')
                    return redirect(url_for('login'))
            except Exception as e:
                flash('Erro ao acessar o banco de dados.', 'danger')
                return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout de admin e cliente"""
    session.pop('admin_logado', None)
    session.pop('cliente_logado', None)
    session.pop('usuario_email', None)
    session.pop('usuario_nome', None)
    flash('Logout efetuado!', 'info')
    return redirect(url_for('index'))

# =========================
# Rotas de Cadastro
# =========================

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Cadastro de novo cliente"""
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        sobrenome = request.form['sobrenome'].strip()
        email = request.form['email'].strip()
        senha = request.form['senha'].strip()
        confirmar_senha = request.form['confirmar_senha'].strip()
        endereco = request.form.get('endereco', '').strip()
        celular = request.form['celular'].strip()
        empresa = request.form.get('empresa', '').strip()
        contato = request.form.get('contato', '').strip()
        observacao = request.form.get('observacao', '').strip()
        if not nome or not sobrenome or not email or not senha or not celular:
            flash('Preencha todos os campos obrigatórios.', 'warning')
            return redirect(url_for('cadastro'))
        if senha != confirmar_senha:
            flash('As senhas não coincidem.', 'danger')
            return redirect(url_for('cadastro'))
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('E-mail inválido.', 'danger')
            return redirect(url_for('cadastro'))
        senha_hash = generate_password_hash(senha)
        try:
            with conectar_banco() as con:
                cur = con.cursor()
                cur.execute('INSERT INTO clientes (nome, sobrenome, email, senha, endereco, celular, empresa, contato, observacao) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (nome, sobrenome, email, senha_hash, endereco, celular, empresa, contato, observacao))
                con.commit()
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect('/')
        except Exception as e:
            flash('Erro ao cadastrar usuário.', 'danger')
            return redirect(url_for('cadastro'))
    return render_template('cadastro.html')

@app.route('/contato', methods=['GET', 'POST'])
def contato():
    """Formulário de contato"""
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        mensagem = request.form['mensagem']
        print(f"[CONTATO] {nome} | {email} | {mensagem}")
        flash('Mensagem enviada com sucesso!', 'success')
        return redirect('/')
    return render_template('contato.html')

@app.route('/produtos', methods=['GET', 'POST'])
def produtos():
    """
    Listagem e busca de produtos
    - Exibe todos os produtos cadastrados
    - Permite busca por nome ou descrição
    - Monta galeria de imagens para cada produto
    """
    termo = ''  # Termo de busca
    produtos = []  # Lista final de produtos para exibir
    if request.method == 'POST':
        termo = request.form.get('busca', '').strip()  # Recebe termo de busca do formulário
    try:
        with conectar_banco() as con:
            cur = con.cursor()
            if termo:
                # Busca produtos pelo termo
                cur.execute('SELECT id, nome, descricao, preco, imagem, estoque FROM produtos WHERE nome LIKE ? OR descricao LIKE ?', (f'%{termo}%', f'%{termo}%'))
            else:
                # Busca todos os produtos
                cur.execute('SELECT id, nome, descricao, preco, imagem, estoque FROM produtos')
            lista = cur.fetchall()
    except Exception as e:
        flash('Erro ao acessar produtos.', 'danger')
        lista = []
    # Monta lista de produtos com galeria de imagens
    for p in lista:
        produto_id = p[0]
        imagens = []
        # Procura até 5 imagens para cada produto
        for i in range(1, 6):
            nome_img = f"produto_{produto_id}_{i}.jpg"
            caminho = os.path.join('static', 'imagens', nome_img)
            if os.path.exists(caminho):
                imagens.append(nome_img)
        produtos.append({
            'id': produto_id,
            'nome': p[1],
            'descricao': p[2],
            'preco': p[3],
            'imagem': p[4],
            'estoque': p[5],
            'galeria': imagens  # Lista de imagens do produto
        })
    # Renderiza página de produtos
    return render_template('produtos.html', produtos=produtos, termo=termo)

@app.route('/adicionar_carrinho/<int:produto_id>', methods=['POST', 'GET'])
def adicionar_carrinho(produto_id):
    """
    Adiciona um produto ao carrinho do usuário
    - Se já existe, incrementa a quantidade
    - Suporta requisições AJAX e padrão
    """
    carrinho = session.get('carrinho', {})  # Recupera carrinho da sessão
    pid = str(produto_id)
    carrinho[pid] = carrinho.get(pid, 0) + 1  # Adiciona ou incrementa produto
    session['carrinho'] = carrinho  # Atualiza carrinho na sessão
    # Resposta para AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Produto adicionado ao carrinho!'})
    # Resposta padrão
    flash('Produto adicionado ao carrinho!', 'success')
    return redirect(url_for('produtos'))


# =========================
# Rotas de Carrinho
# =========================

@app.route('/carrinho')
def carrinho():
    """
    Exibe o carrinho de compras do usuário
    - Lista produtos, quantidades e subtotal
    - Calcula o valor total
    """
    carrinho = session.get('carrinho', {})  # Recupera carrinho da sessão
    produtos = []  # Lista de produtos no carrinho
    total = 0  # Valor total do carrinho
    if carrinho:
        con = conectar_banco()
        cur = con.cursor()
        for pid_str, qtd in carrinho.items():
            pid = int(pid_str)
            # Busca dados do produto
            cur.execute('SELECT nome, descricao, preco, imagem FROM produtos WHERE id = ?', (pid,))
            p = cur.fetchone()
            if p:
                subtotal = p[2] * qtd  # Calcula subtotal
                produtos.append({
                    'id': pid,
                    'nome': p[0],
                    'descricao': p[1],
                    'preco': p[2],
                    'imagem': p[3],
                    'quantidade': qtd,
                    'subtotal': subtotal
                })
                total += subtotal
        con.close()
    # Renderiza página do carrinho
    return render_template('carrinho.html', produtos=produtos, total=total)

@app.route('/carrinho/aumentar/<int:produto_id>')
def aumentar_quantidade(produto_id):
    """Aumenta a quantidade de um item no carrinho"""
    carrinho = session.get('carrinho', {})
    pid = str(produto_id)
    if pid in carrinho:
        carrinho[pid] += 1
    session['carrinho'] = carrinho
    return redirect(url_for('carrinho'))

@app.route('/carrinho/diminuir/<int:produto_id>')
def diminuir_quantidade(produto_id):
    """Diminui a quantidade de um item no carrinho"""
    carrinho = session.get('carrinho', {})
    pid = str(produto_id)
    if pid in carrinho and carrinho[pid] > 1:
        carrinho[pid] -= 1
    elif pid in carrinho:
        del carrinho[pid]
    session['carrinho'] = carrinho
    return redirect(url_for('carrinho'))

@app.route('/carrinho/remover/<int:produto_id>')
def remover_item(produto_id):
    """Remove um item do carrinho"""
    carrinho = session.get('carrinho', {})
    pid = str(produto_id)
    if pid in carrinho:
        del carrinho[pid]
    session['carrinho'] = carrinho
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Item removido do carrinho.'})
    flash('Item removido do carrinho.', 'info')
    return redirect(url_for('carrinho'))

# =========================
# Rotas de Pedido
# =========================

@app.route('/finalizar_pedido', methods=['GET', 'POST'])
def finalizar_pedido():
    """Finaliza o pedido, gera PDF e salva no banco de dados."""
    carrinho = session.get('carrinho', {})
    if not carrinho:
        flash('Carrinho vazio.', 'warning')
        return redirect(url_for('produtos'))

    cliente_email = None
    # Se não estiver logado, pede dados rápidos
    if not session.get('admin_logado') and not session.get('cliente_logado'):
        if request.method == 'POST':
            nome = request.form['nome'].strip()
            sobrenome = request.form['sobrenome'].strip()
            celular = request.form['celular'].strip()
            if not nome or not sobrenome or not celular:
                flash('Preencha todos os campos.', 'warning')
                return render_template('finalizar_rapido.html')
            cliente_nome = f"{nome} {sobrenome} ({celular})"
        else:
            return render_template('finalizar_rapido.html')
    else:
        # Se for admin, nome genérico. Se for cliente, pega nome e email do banco
        if session.get('admin_logado'):
            cliente_nome = "Administrador"
        else:
            try:
                with conectar_banco() as con:
                    cur = con.cursor()
                    cur.execute('SELECT nome, sobrenome, email FROM clientes WHERE email = ?', (session.get('usuario_email'),))
                    row = cur.fetchone()
                if row:
                    cliente_nome = f"{row[0]} {row[1]}"
                    cliente_email = row[2]
                else:
                    cliente_nome = "Cliente"
            except Exception:
                cliente_nome = "Cliente"

    con = conectar_banco()
    cur = con.cursor()
    produtos = []
    total = 0
    itens_str = []
    for pid_str, qtd in carrinho.items():
        pid = int(pid_str)
        cur.execute('SELECT nome, descricao, preco FROM produtos WHERE id = ?', (pid,))
        item = cur.fetchone()
        if item:
            for _ in range(qtd):
                produtos.append(item)
                total += item[2]
            itens_str.append(f"{item[0]} (x{qtd})")
    con.close()

    nome_pdf = f"orcamento_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    caminho_pdf = os.path.join('static', nome_pdf)
    gerar_pdf(cliente_nome, produtos, total, caminho_pdf)

    # Salva pedido no banco
    try:
        with conectar_banco() as con:
            cur = con.cursor()
            cur.execute('INSERT INTO pedidos (cliente_nome, cliente_email, data, total, pdf_path, itens) VALUES (?, ?, ?, ?, ?, ?)',
                (cliente_nome, cliente_email, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), total, caminho_pdf, ', '.join(itens_str)))
            con.commit()
    except Exception as e:
        flash('Erro ao salvar pedido no banco.', 'danger')

    numero = '5512345678'
    texto = urllib.parse.quote(f"Olá! Pedido realizado. Orçamento: {request.host_url}static/{nome_pdf}")
    return redirect(f"https://wa.me/{numero}?text={texto}")

# =========================
# Rotas Administrativas
# =========================

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Painel administrativo para gerenciar produtos e importar via Excel"""
    if not session.get('admin_logado'):
        flash('Acesso restrito.', 'danger')
        return redirect(url_for('login'))
    # Importação via Excel
    if request.method == 'POST' and 'excel_produtos' in request.files:
        excel_file = request.files['excel_produtos']
        if excel_file.filename:
            caminho_excel = os.path.join('doc', 'upload_temp.xlsx')
            excel_file.save(caminho_excel)
            import pandas as pd
            try:
                df = pd.read_excel(caminho_excel)
                colunas_esperadas = {'nome', 'descricao', 'preco', 'estoque'}
                if not colunas_esperadas.issubset(df.columns):
                    flash('Colunas esperadas não encontradas no Excel.', 'danger')
                else:
                    with conectar_banco() as con:
                        cur = con.cursor()
                        for _, row in df.iterrows():
                            cur.execute('INSERT INTO produtos (nome, descricao, preco, imagem, estoque) VALUES (?, ?, ?, ?, ?)',
                                        (row['nome'], row['descricao'], float(row['preco']), '', int(row['estoque'])))
                        con.commit()
                    flash('Produtos importados com sucesso!', 'success')
            except Exception as e:
                flash(f'Erro ao importar Excel: {str(e)}', 'danger')
            finally:
                if os.path.exists(caminho_excel):
                    os.remove(caminho_excel)
        else:
            flash('Selecione um arquivo Excel.', 'warning')
    try:
        with conectar_banco() as con:
            cur = con.cursor()
            cur.execute('SELECT id, nome, descricao, preco, imagem, estoque FROM produtos')
            produtos = cur.fetchall()
    except Exception as e:
        flash('Erro ao acessar produtos.', 'danger')
        produtos = []
    return render_template('painel_admin.html', produtos=produtos)

@app.route('/admin/adicionar', methods=['POST'])
def admin_adicionar():
    """Cadastro de produto pelo admin"""
    if not session.get('admin_logado'):
        flash('Acesso negado.', 'danger')
        return redirect(url_for('login'))
    nome = request.form['nome'].strip()
    descricao = request.form['descricao'].strip()
    preco = request.form['preco'].strip()
    estoque = request.form.get('estoque', '').strip()
    arquivos = request.files.getlist('imagens')
    # Validação backend
    if not nome or not descricao or not preco or not estoque:
        flash('Preencha todos os campos obrigatórios.', 'warning')
        return redirect(url_for('admin'))
    try:
        preco_float = float(preco)
        if preco_float <= 0:
            flash('O preço deve ser maior que zero.', 'warning')
            return redirect(url_for('admin'))
        estoque_int = int(estoque)
        if estoque_int < 0:
            flash('O estoque não pode ser negativo.', 'warning')
            return redirect(url_for('admin'))
    except ValueError:
        flash('Preço ou estoque inválido.', 'warning')
        return redirect(url_for('admin'))
    imagens_validas = [arq for arq in arquivos[:5] if arq and arq.filename and arq.mimetype.startswith('image/')]
    if not imagens_validas:
        flash('Envie pelo menos uma imagem válida do produto.', 'warning')
        return redirect(url_for('admin'))
    if len(arquivos) > 5:
        flash('Máximo de 5 imagens por produto.', 'warning')
        return redirect(url_for('admin'))
    try:
        with conectar_banco() as con:
            cur = con.cursor()
            cur.execute('INSERT INTO produtos (nome, descricao, preco, imagem, estoque) VALUES (?, ?, ?, ?, ?)', (nome, descricao, preco, '', estoque_int))
            produto_id = cur.lastrowid
            pasta = os.path.join('static', 'imagens')
            os.makedirs(pasta, exist_ok=True)
            imagens_salvas = []
            for i, arquivo in enumerate(imagens_validas):
                nome_img = f"produto_{produto_id}_{i+1}.jpg"
                caminho = os.path.join(pasta, secure_filename(nome_img))
                imagem = Image.open(arquivo)
                imagem = imagem.convert('RGB')
                imagem = imagem.resize((400, 300))
                imagem.save(caminho, format='JPEG', quality=85)
                imagens_salvas.append(nome_img)
            if imagens_salvas:
                cur.execute('UPDATE produtos SET imagem = ? WHERE id = ?', (imagens_salvas[0], produto_id))
            con.commit()
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('admin'))
    except Exception as e:
        flash('Erro ao cadastrar produto.', 'danger')
        return redirect(url_for('admin'))

@app.route('/admin/editar/<int:produto_id>', methods=['GET', 'POST'])
def editar_produto(produto_id):
    """Edição de produto pelo admin"""
    if not session.get('admin_logado'):
        flash('Acesso negado.', 'danger')
        return redirect(url_for('login'))

    con = conectar_banco()
    cur = con.cursor()

    # Deletar imagem
    if request.method == 'POST' and 'deletar_imagem' in request.form:
        img_nome = request.form['deletar_imagem']
        img_path = os.path.join('static', 'imagens', img_nome)
        if os.path.exists(img_path):
            os.remove(img_path)
            flash('Imagem removida com sucesso!', 'info')
        return redirect(url_for('editar_produto', produto_id=produto_id))

    # Edição completa do produto (campos + imagem)
    if request.method == 'POST' and not (
        'deletar_imagem' in request.form or
        ('adicionar_nova_imagem' in request.form and 'nova_imagem_galeria' in request.files and request.files['nova_imagem_galeria'].filename)
    ):
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['preco']
        estoque = request.form['estoque']
        # Se houver nova imagem, salva
        nova_img = request.files.get('nova_imagem', None)
        if nova_img and nova_img.filename and nova_img.mimetype.startswith('image/'):
            nome_img = request.form.get('img_nome', None)
            if nome_img:
                try:
                    img_path = os.path.join('static', 'imagens', nome_img)
                    imagem = Image.open(nova_img)
                    imagem = imagem.convert('RGB')
                    imagem = imagem.resize((400, 300))
                    imagem.save(img_path, format='JPEG', quality=85)
                    flash('Imagem substituída com sucesso!', 'success')
                except Exception as e:
                    flash(f'Erro ao processar imagem: {str(e)}', 'danger')
        # Atualiza dados do produto
        cur.execute('UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ? WHERE id = ?',
                    (nome, descricao, preco, estoque, produto_id))
        con.commit()
        con.close()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('admin'))

    # Adicionar nova imagem
    if request.method == 'POST' and 'adicionar_nova_imagem' in request.form and 'nova_imagem_galeria' in request.files:
        nova_img = request.files['nova_imagem_galeria']
        if nova_img and nova_img.filename and nova_img.mimetype.startswith('image/'):
            # Descobrir próximo slot livre
            for i in range(1, 6):
                nome_img = f"produto_{produto_id}_{i}.jpg"
                img_path = os.path.join('static', 'imagens', nome_img)
                if not os.path.exists(img_path):
                    imagem = Image.open(nova_img)
                    imagem = imagem.convert('RGB')
                    imagem = imagem.resize((400, 300))
                    imagem.save(img_path, format='JPEG', quality=85)
                    flash('Nova imagem adicionada com sucesso!', 'success')
                    break
        return redirect(url_for('editar_produto', produto_id=produto_id))

    # Só executa update do produto se não for ação de imagem
    if request.method == 'POST' and not (
        'deletar_imagem' in request.form or
        ('nova_imagem' in request.files and request.files['nova_imagem'].filename) or
        ('adicionar_nova_imagem' in request.form and 'nova_imagem_galeria' in request.files and request.files['nova_imagem_galeria'].filename)
    ):
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['preco']
        estoque = request.form['estoque']
        cur.execute('UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ? WHERE id = ?',
                    (nome, descricao, preco, estoque, produto_id))
        con.commit()
        con.close()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('admin'))

    cur.execute('SELECT id, nome, descricao, preco, imagem, estoque FROM produtos WHERE id = ?', (produto_id,))
    produto = cur.fetchone()
    # Buscar galeria de imagens
    galeria = []
    for i in range(1, 6):
        nome_img = f"produto_{produto_id}_{i}.jpg"
        caminho = os.path.join('static', 'imagens', nome_img)
        if os.path.exists(caminho):
            galeria.append(nome_img)
    con.close()

    if produto:
        return render_template('editar_produto.html', produto=produto, galeria=galeria)
    else:
        flash('Produto não encontrado.', 'warning')
        return redirect(url_for('admin'))

@app.route('/admin/excluir/<int:produto_id>')
def excluir_produto(produto_id):
    """Exclusão de produto pelo admin"""
    if not session.get('admin_logado'):
        flash('Acesso negado.', 'danger')
        return redirect(url_for('login'))

    con = conectar_banco()
    cur = con.cursor()
    cur.execute('DELETE FROM produtos WHERE id = ?', (produto_id,))
    con.commit()
    con.close()
    flash('Produto excluído com sucesso!', 'info')
    return redirect(url_for('admin'))

@app.route('/meus_pedidos')
def meus_pedidos():
    """Exibe o histórico de pedidos do cliente logado."""
    if not session.get('cliente_logado'):
        flash('Faça login para ver seus pedidos.', 'warning')
        return redirect(url_for('login'))
    pedidos = []
    try:
        with conectar_banco() as con:
            cur = con.cursor()
            cur.execute('SELECT data, total, pdf_path, itens FROM pedidos WHERE cliente_email = ? ORDER BY data DESC', (session.get('usuario_email'),))
            pedidos = cur.fetchall()
    except Exception as e:
        flash('Erro ao acessar pedidos.', 'danger')
    return render_template('meus_pedidos.html', pedidos=pedidos)

# =========================
# Observações e dicas
# =========================

# DICA: Para projetos maiores, utilize Blueprints e Flask-WTF para CSRF.

# 🚀 Rodar app
if __name__ == '__main__':
    app.run(debug=True)