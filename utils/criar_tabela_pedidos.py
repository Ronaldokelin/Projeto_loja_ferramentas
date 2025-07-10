# Script para criar tabela de pedidos no banco SQLite
import sqlite3

con = sqlite3.connect('produtos.db')
cur = con.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_nome TEXT NOT NULL,
    cliente_email TEXT,
    data TEXT NOT NULL,
    total REAL NOT NULL,
    pdf_path TEXT,
    itens TEXT NOT NULL
)
''')
con.commit()
con.close()
print('Tabela pedidos criada com sucesso!')
