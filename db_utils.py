import sqlite3
from datetime import datetime

def criar_tabela():
    conn = sqlite3.connect('dados_senhas.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS senhas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        servico TEXT NOT NULL,
        usuario TEXT NOT NULL,
        senha BLOB NOT NULL,
        data_criacao TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

def salvar_senha(servico, usuario, senha_criptografada):
    data_criacao = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect('dados_senhas.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO senhas(servico, usuario, senha, data_criacao) VALUES (?, ?, ?, ?)
    ''', (servico, usuario, senha_criptografada, data_criacao))
    conn.commit()
    conn.close()

def listar_senhas():
    conn = sqlite3.connect('dados_senhas.db')
    cursor = conn.cursor()
    cursor.execute('SELECT servico, usuario, senha FROM senhas')
    senhas = cursor.fetchall()
    conn.close()
    return senhas

def excluir_senha(servico, usuario):
    conn = sqlite3.connect('dados_senhas.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM senhas WHERE servico = ? AND usuario = ?", (servico, usuario))
    conn.commit()
    conn.close()
