import sqlite3
import pandas as pd
import os

def conectar_banco():
    return sqlite3.connect('produtos.db')

# Caminho do arquivo Excel
CAMINHO_EXCEL = os.path.join('doc', 'Lista de Ferramentas Will.xlsx')

def importar_produtos_excel():
    if not os.path.exists(CAMINHO_EXCEL):
        print('Arquivo Excel não encontrado:', CAMINHO_EXCEL)
        return
    df = pd.read_excel(CAMINHO_EXCEL)
    # Espera colunas: nome, descricao, preco, estoque
    colunas_esperadas = {'nome', 'descricao', 'preco', 'estoque'}
    if not colunas_esperadas.issubset(df.columns):
        print('Colunas esperadas não encontradas no Excel:', colunas_esperadas)
        return
    with conectar_banco() as con:
        cur = con.cursor()
        for _, row in df.iterrows():
            cur.execute('INSERT INTO produtos (nome, descricao, preco, imagem, estoque) VALUES (?, ?, ?, ?, ?)',
                        (row['nome'], row['descricao'], float(row['preco']), '', int(row['estoque'])))
        con.commit()
    print('Produtos importados com sucesso!')

def gerar_modelo_excel():
    import pandas as pd
    df = pd.DataFrame({
        'nome': ['Exemplo Produto'],
        'descricao': ['Descrição do produto'],
        'preco': [99.90],
        'estoque': [10]
    })
    caminho_modelo = os.path.join('..', 'static', 'doc', 'modelo_cadastro_produtos.xlsx')
    df.to_excel(caminho_modelo, index=False)
    print('Modelo gerado em:', caminho_modelo)

if __name__ == '__main__':
    # Para gerar o modelo, descomente a linha abaixo:
    # gerar_modelo_excel()
    importar_produtos_excel()
