import json
import hashlib

# ============================================================
# ARQUIVO onde os dados ficam salvos
# json é como um "caderno" que o Python sabe ler e escrever
# ============================================================
ARQUIVO = "usuarios.json"


# ------------------------------------------------------------
# Essas 2 funções são "ajudantes" para ler e salvar o arquivo
# Você vai chamar elas sempre que precisar acessar os dados
# ------------------------------------------------------------

def carregar_usuarios():
    # Abre o arquivo e transforma em um dicionário Python
    with open(ARQUIVO, "r") as f:
        return json.load(f)

def salvar_usuarios(usuarios):
    # Pega o dicionário e salva de volta no arquivo
    with open(ARQUIVO, "w") as f:
        json.dump(usuarios, f, indent=4)


# ------------------------------------------------------------
# Hash de senha: transforma "1234" em um código embaralhado
# Isso é segurança básica — nunca salvar senha pura em arquivo
# Exemplo: "1234" vira "03ac674216f3e..."
# ------------------------------------------------------------

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


# ------------------------------------------------------------
# CADASTRO: cria uma conta nova
# Recebe nome e senha, salva no arquivo
# ------------------------------------------------------------

def cadastrar():
    usuarios = carregar_usuarios()

    nome = input("Escolha um nome de usuário: ")

    # Verifica se esse nome já existe no "caderno"
    if nome in usuarios:
        print("Esse usuário já existe!")
        return

    senha = input("Escolha uma senha: ")

    # Cria a conta como um dicionário com 3 informações
    usuarios[nome] = {
        "senha": hash_senha(senha),   # senha embaralhada
        "saldo": 1000.0,              # saldo inicial de presente
        "historico": []               # lista vazia de movimentações
    }

    salvar_usuarios(usuarios)
    print("Conta criada! Saldo inicial: R$ 1000,00")


# ------------------------------------------------------------
# LOGIN: verifica se usuário e senha estão corretos
# Retorna o nome do usuário se der certo, ou None se errar
# ------------------------------------------------------------

def login():
    usuarios = carregar_usuarios()

    nome = input("Usuário: ")
    senha = input("Senha: ")

    # Verifica se o nome existe E se a senha bate
    if nome in usuarios and usuarios[nome]["senha"] == hash_senha(senha):
        print(f"Bem-vindo, {nome}!")
        return nome  # login OK, devolve o nome

    print("Usuário ou senha incorretos.")
    return None  # login falhou


# ------------------------------------------------------------
# VER SALDO: mostra quanto tem na conta
# ------------------------------------------------------------

def ver_saldo(usuario):
    usuarios = carregar_usuarios()
    saldo = usuarios[usuario]["saldo"]
    print(f"Seu saldo: R$ {saldo:.2f}")
    # :.2f significa "mostrar com 2 casas decimais"


# ------------------------------------------------------------
# DEPOSITAR: adiciona dinheiro na conta
# ------------------------------------------------------------

def depositar(usuario):
    usuarios = carregar_usuarios()

    valor = float(input("Quanto quer depositar? R$ "))

    if valor <= 0:
        print("Valor tem que ser maior que zero.")
        return

    usuarios[usuario]["saldo"] += valor
    usuarios[usuario]["historico"].append(f"Depósito: +R$ {valor:.2f}")

    salvar_usuarios(usuarios)
    print(f"Depósito de R$ {valor:.2f} realizado!")


# ------------------------------------------------------------
# SACAR: remove dinheiro da conta
# ------------------------------------------------------------

def sacar(usuario):
    usuarios = carregar_usuarios()

    valor = float(input("Quanto quer sacar? R$ "))

    if valor <= 0:
        print("Valor tem que ser maior que zero.")
        return

    if valor > usuarios[usuario]["saldo"]:
        print("Saldo insuficiente.")
        return

    usuarios[usuario]["saldo"] -= valor
    usuarios[usuario]["historico"].append(f"Saque: -R$ {valor:.2f}")

    salvar_usuarios(usuarios)
    print(f"Saque de R$ {valor:.2f} realizado!")


# ------------------------------------------------------------
# TRANSFERIR: manda dinheiro pra outra conta
# ------------------------------------------------------------

def transferir(usuario):
    usuarios = carregar_usuarios()

    destino = input("Nome do usuário que vai receber: ")

    if destino not in usuarios:
        print("Usuário não encontrado.")
        return

    valor = float(input("Quanto quer transferir? R$ "))

    if valor <= 0:
        print("Valor tem que ser maior que zero.")
        return

    if valor > usuarios[usuario]["saldo"]:
        print("Saldo insuficiente.")
        return

    # Tira de quem envia, coloca em quem recebe
    usuarios[usuario]["saldo"] -= valor
    usuarios[destino]["saldo"] += valor

    # Registra no histórico dos dois
    usuarios[usuario]["historico"].append(f"Transferência para {destino}: -R$ {valor:.2f}")
    usuarios[destino]["historico"].append(f"Transferência de {usuario}: +R$ {valor:.2f}")

    salvar_usuarios(usuarios)
    print(f"Transferência de R$ {valor:.2f} para {destino} realizada!")


# ------------------------------------------------------------
# HISTÓRICO: lista todas as movimentações da conta
# ------------------------------------------------------------

def ver_historico(usuario):
    usuarios = carregar_usuarios()
    historico = usuarios[usuario]["historico"]

    if len(historico) == 0:
        print("Nenhuma movimentação ainda.")
        return

    print("--- Seu histórico ---")
    for item in historico:
        print(" -", item)


# ============================================================
# MENUS — são loops while que ficam rodando até o usuário sair
# ============================================================

def menu_banco(usuario):
    # Esse loop fica rodando enquanto o usuário estiver logado
    while True:
        print("\n===== BANCO DIGITAL =====")
        print("1 - Ver saldo")
        print("2 - Depositar")
        print("3 - Sacar")
        print("4 - Transferir")
        print("5 - Histórico")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            ver_saldo(usuario)
        elif opcao == "2":
            depositar(usuario)
        elif opcao == "3":
            sacar(usuario)
        elif opcao == "4":
            transferir(usuario)
        elif opcao == "5":
            ver_historico(usuario)
        elif opcao == "0":
            print("Saindo... até logo!")
            break  # break sai do while
        else:
            print("Opção inválida.")


def menu_inicial():
    # Cria o arquivo vazio se ainda não existir
    try:
        carregar_usuarios()
    except:
        salvar_usuarios({})  # cria arquivo com dicionário vazio

    while True:
        print("\n===== BEM-VINDO =====")
        print("1 - Login")
        print("2 - Cadastrar")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            usuario = login()
            if usuario:              # se login deu certo
                menu_banco(usuario)  # entra no menu do banco
        elif opcao == "2":
            cadastrar()
        elif opcao == "0":
            break


# ============================================================
# Ponto de entrada do programa
# Isso garante que o menu só roda quando você executa
# o main.py diretamente (não quando importa em outro arquivo)
# ============================================================
menu_inicial()