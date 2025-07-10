import sqlite3

def atualizar_tabela_clientes():
    con = sqlite3.connect('produtos.db')
    cur = con.cursor()
    # Adiciona as colunas se não existirem
    try:
        cur.execute("ALTER TABLE clientes ADD COLUMN sobrenome TEXT;")
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute("ALTER TABLE clientes ADD COLUMN endereco TEXT;")
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute("ALTER TABLE clientes ADD COLUMN celular TEXT;")
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute("ALTER TABLE clientes ADD COLUMN empresa TEXT;")
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute("ALTER TABLE clientes ADD COLUMN contato TEXT;")
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute("ALTER TABLE clientes ADD COLUMN observacao TEXT;")
    except sqlite3.OperationalError:
        pass

    con.commit()
    con.close()
    print("Tabela clientes atualizada com sucesso!")

if __name__ == '__main__':
    atualizar_tabela_clientes()