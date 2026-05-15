import json
import hashlib

ARQUIVO = "data/usuarios.json"

def carregar_usuarios():
    with open(ARQUIVO, "r") as f:
        return json.load(f)

def salvar_usuarios(usuarios):
    with open(ARQUIVO, "w") as f:
        json.dump(usuarios, f, indent=4)

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def cadastrar():
    usuarios = carregar_usuarios()
    nome = input("Nome de usuário: ")
    if nome in usuarios:
        print("Usuário já existe!")
        return None
    senha = input("Senha: ")
    usuarios[nome] = {
        "senha": hash_senha(senha),
        "saldo": 1000.0,  # saldo inicial
        "historico": []
    }
    salvar_usuarios(usuarios)
    print(f"Conta criada com sucesso! Saldo inicial: R$ 1000,00")
    return nome

def login():
    usuarios = carregar_usuarios()
    nome = input("Usuário: ")
    senha = input("Senha: ")
    if nome in usuarios and usuarios[nome]["senha"] == hash_senha(senha):
        print(f"Bem-vindo, {nome}!")
        return nome
    print("Usuário ou senha incorretos.")
    return None