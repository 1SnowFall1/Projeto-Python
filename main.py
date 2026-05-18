import json
import hashlib
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

# ============================================================
# ARQUIVOS do sistema
# ============================================================
ARQUIVO_USUARIOS = "usuarios.json"
ARQUIVO_LOGS     = "logs.txt"


# ============================================================
# LOGS
# ============================================================

def registrar_log(mensagem):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open(ARQUIVO_LOGS, "a") as f:
        f.write(f"[{agora}] {mensagem}\n")


# ============================================================
# CARREGAR e SALVAR
# ============================================================

def carregar_usuarios():
    with open(ARQUIVO_USUARIOS, "r") as f:
        return json.load(f)

def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, "w") as f:
        json.dump(usuarios, f, indent=4)


# ============================================================
# HASH de senha
# ============================================================

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


# ============================================================
# PRINTS COLORIDOS
# ============================================================

def print_sucesso(msg):
    print(Fore.GREEN + "✔ " + msg)

def print_erro(msg):
    print(Fore.RED + "✘ " + msg)

def print_info(msg):
    print(Fore.CYAN + "→ " + msg)

def print_titulo(msg):
    print(Style.BRIGHT + Fore.YELLOW + "\n" + "=" * 35)
    print(Style.BRIGHT + Fore.YELLOW + f"  {msg}")
    print(Style.BRIGHT + Fore.YELLOW + "=" * 35)


# ============================================================
# PEDIR VALOR — aceita vírgula e rejeita letras
# Usada em depositar, sacar e transferir
# ============================================================

def pedir_valor(mensagem):
    texto = input(mensagem)
    texto = texto.replace(",", ".")  # transforma 50,30 em 50.30

    try:
        valor = float(texto)
        return valor
    except:
        print_erro("Valor inválido! Digite só números.")
        return None


# ============================================================
# CADASTRO
# ============================================================

def cadastrar():
    print_titulo("CADASTRO")
    usuarios = carregar_usuarios()

    nome = input("Escolha um nome de usuário: ")

    if nome.strip() == "":
        print_erro("Nome de usuário não pode ser vazio.")
        return

    if nome in usuarios:
        print_erro("Esse usuário já existe!")
        registrar_log(f"Tentativa de cadastro com usuário já existente: {nome}")
        return

    senha = input("Escolha uma senha: ")

    if senha.strip() == "":
        print_erro("A senha não pode ser vazia.")
        return

    usuarios[nome] = {
        "senha": hash_senha(senha),
        "saldo": 1000.0,
        "historico": [],
        "bloqueado": False   # começa desbloqueado
    }

    salvar_usuarios(usuarios)
    registrar_log(f"Nova conta criada: {nome}")
    print_sucesso("Conta criada! Saldo inicial: R$ 1000,00")


# ============================================================
# LOGIN com limite de tentativas e bloqueio persistente
# ============================================================

def login():
    print_titulo("LOGIN")
    usuarios = carregar_usuarios()

    MAX_TENTATIVAS = 3

    nome = input("Usuário: ")

    # Rejeita entrada vazia sem contar tentativa
    if nome.strip() == "":
        print_erro("Digite um nome de usuário.")
        return None

    # Avisa que não existe sem contar tentativa
    if nome not in usuarios:
        print_erro("Usuário não encontrado.")
        registrar_log(f"Tentativa de login com usuário inexistente: {nome}")
        return None

    # Verifica se a conta já está bloqueada
    if usuarios[nome].get("bloqueado", False):
        print_erro("Essa conta está bloqueada. Fale com o administrador.")
        registrar_log(f"Tentativa de acesso em conta bloqueada: {nome}")
        return None

    # Só chega aqui se o usuário existe e não está bloqueado
    for tentativa in range(MAX_TENTATIVAS):
        senha = input("Senha: ")

        if usuarios[nome]["senha"] == hash_senha(senha):
            registrar_log(f"Login bem-sucedido: {nome}")
            print_sucesso(f"Bem-vindo, {nome}!")
            return nome

        restantes = MAX_TENTATIVAS - tentativa - 1
        registrar_log(f"Senha errada para: {nome}")

        if restantes > 0:
            print_erro(f"Senha incorreta. {restantes} tentativa(s) restante(s).")
        else:
            # Bloqueia a conta e salva no arquivo
            usuarios[nome]["bloqueado"] = True
            salvar_usuarios(usuarios)
            print_erro("Muitas tentativas. Conta bloqueada!")
            registrar_log(f"Conta bloqueada: {nome}")

    return None


# ============================================================
# OPERAÇÕES BANCÁRIAS
# ============================================================

def ver_saldo(usuario):
    usuarios = carregar_usuarios()
    saldo = usuarios[usuario]["saldo"]
    print_info(f"Seu saldo: R$ {saldo:.2f}")


def depositar(usuario):
    usuarios = carregar_usuarios()

    valor = pedir_valor("Quanto quer depositar? R$ ")
    if valor is None:
        return

    if valor <= 0:
        print_erro("Valor tem que ser maior que zero.")
        return

    usuarios[usuario]["saldo"] += valor
    usuarios[usuario]["historico"].append(f"Depósito: +R$ {valor:.2f}")

    salvar_usuarios(usuarios)
    registrar_log(f"{usuario} depositou R$ {valor:.2f}")
    print_sucesso(f"Depósito de R$ {valor:.2f} realizado!")


def sacar(usuario):
    usuarios = carregar_usuarios()

    valor = pedir_valor("Quanto quer sacar? R$ ")
    if valor is None:
        return

    if valor <= 0:
        print_erro("Valor tem que ser maior que zero.")
        return

    if valor > usuarios[usuario]["saldo"]:
        registrar_log(f"{usuario} tentou sacar R$ {valor:.2f} sem saldo suficiente")
        print_erro("Saldo insuficiente.")
        return

    usuarios[usuario]["saldo"] -= valor
    usuarios[usuario]["historico"].append(f"Saque: -R$ {valor:.2f}")

    salvar_usuarios(usuarios)
    registrar_log(f"{usuario} sacou R$ {valor:.2f}")
    print_sucesso(f"Saque de R$ {valor:.2f} realizado!")


def transferir(usuario):
    usuarios = carregar_usuarios()

    destino = input("Nome do usuário que vai receber: ")

    # Não pode transferir para si mesmo
    if destino == usuario:
        print_erro("Você não pode transferir para si mesmo.")
        return

    if destino not in usuarios:
        print_erro("Usuário não encontrado.")
        return

    valor = pedir_valor("Quanto quer transferir? R$ ")
    if valor is None:
        return

    if valor <= 0:
        print_erro("Valor tem que ser maior que zero.")
        return

    if valor > usuarios[usuario]["saldo"]:
        print_erro("Saldo insuficiente.")
        return

    usuarios[usuario]["saldo"]  -= valor
    usuarios[destino]["saldo"]  += valor

    usuarios[usuario]["historico"].append(f"Transferência para {destino}: -R$ {valor:.2f}")
    usuarios[destino]["historico"].append(f"Transferência de {usuario}: +R$ {valor:.2f}")

    salvar_usuarios(usuarios)
    registrar_log(f"{usuario} transferiu R$ {valor:.2f} para {destino}")
    print_sucesso(f"Transferência de R$ {valor:.2f} para {destino} realizada!")


def ver_historico(usuario):
    usuarios = carregar_usuarios()
    historico = usuarios[usuario]["historico"]

    print_titulo("HISTÓRICO")

    if len(historico) == 0:
        print_info("Nenhuma movimentação ainda.")
        return

    for item in historico:
        print(Fore.CYAN + f"  - {item}")


# ============================================================
# MENUS
# ============================================================

def menu_banco(usuario):
    while True:
        print_titulo(f"OLÁ, {usuario.upper()}")
        print("  1 - Ver saldo")
        print("  2 - Depositar")
        print("  3 - Sacar")
        print("  4 - Transferir")
        print("  5 - Histórico")
        print("  0 - Sair")

        opcao = input("\nEscolha uma opção: ")

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
            registrar_log(f"{usuario} saiu do sistema")
            print_info("Saindo... até logo!")
            break
        else:
            print_erro("Opção inválida.")


def menu_inicial():
    try:
        carregar_usuarios()
    except:
        salvar_usuarios({})

    while True:
        print_titulo("BANCO DIGITAL")
        print("  1 - Login")
        print("  2 - Cadastrar")
        print("  0 - Sair")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            usuario = login()
            if usuario:
                menu_banco(usuario)
        elif opcao == "2":
            cadastrar()
        elif opcao == "0":
            print_info("Encerrando o sistema.")
            break


menu_inicial()