import sqlite3

caminho_banco = "iaca.db"
conn = sqlite3.connect(caminho_banco)
cursor = conn.cursor()

# Verifica se a coluna "comprado" já existe na tabela "descartes"
cursor.execute("PRAGMA table_info(descartes)")
colunas_descartes = [col[1] for col in cursor.fetchall()]

if "comprado" not in colunas_descartes:
    print("Adicionando coluna 'comprado' na tabela 'descartes'...")
    cursor.execute("ALTER TABLE descartes ADD COLUMN comprado BOOLEAN DEFAULT 0")
    conn.commit()
    print("Coluna 'comprado' adicionada com sucesso!")
else:
    print("A coluna 'comprado' já existe na tabela 'descartes'.")

# Verifica se a coluna "ponto_id" já existe na tabela "pagamentos"
cursor.execute("PRAGMA table_info(pagamentos)")
colunas_pagamentos = [col[1] for col in cursor.fetchall()]

if "ponto_id" not in colunas_pagamentos:
    print("Adicionando coluna 'ponto_id' na tabela 'pagamentos'...")
    cursor.execute("ALTER TABLE pagamentos ADD COLUMN ponto_id INTEGER")
    conn.commit()
    print("Coluna 'ponto_id' adicionada com sucesso!")
else:
    print("A coluna 'ponto_id' já existe na tabela 'pagamentos'.")

conn.close()
