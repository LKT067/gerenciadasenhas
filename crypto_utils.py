from cryptography.fernet import Fernet
import os

def gerar_chave():
    chave = Fernet.generate_key()
    with open('chave.key', 'wb') as chave_file:
        chave_file.write(chave)
    return chave

def carregar_chave():
    chave = open('chave.key', 'rb').read()
    try:
        Fernet(chave)
        return chave
    except ValueError:
        return gerar_chave()

def criptografar_senha(senha, fernet):
    return fernet.encrypt(senha.encode())

def descriptografar_senha(senha_criptografada, fernet):
    return fernet.decrypt(senha_criptografada).decode()
