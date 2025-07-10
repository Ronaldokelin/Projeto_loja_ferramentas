# Script para adicionar campo de estoque na tabela produtos
import sqlite3

con = sqlite3.connect('produtos.db')
cur = con.cursor()
cur.execute('''
ALTER TABLE produtos ADD COLUMN estoque INTEGER DEFAULT 0
''')
con.commit()
con.close()
print('Campo estoque adicionado à tabela produtos!')
