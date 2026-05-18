import json
import hashlib
import requests
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

def print_aviso(msg):
    print(Fore.MAGENTA + "⚠ " + msg)


# ============================================================
# PEDIR VALOR — aceita vírgula e rejeita letras
# ============================================================

def pedir_valor(mensagem):
    texto = input(mensagem)
    texto = texto.replace(",", ".")

    try:
        valor = float(texto)
        return valor
    except:
        print_erro("Valor inválido! Digite só números. Exemplo: 50 ou 50,30")
        return None


# ============================================================
# API 1 — HAVEIBEENPWNED
# Verifica se a senha digitada já apareceu em vazamentos
#
# Como funciona (conceito chamado k-anonymity):
#   1. Gera o hash SHA1 da senha (ex: "1234" → "7110eda4...")
#   2. Manda só os 5 primeiros caracteres pra API
#      (a senha real NUNCA é enviada — isso é segurança de verdade)
#   3. A API devolve uma lista de hashes que começam com esses 5 chars
#   4. Verifica se o hash completo está nessa lista
#   5. Se estiver, a senha foi vazada
# ============================================================

def verificar_senha_vazada(senha):
    try:
        # Gera hash SHA1 da senha e separa em prefixo + sufixo
        sha1 = hashlib.sha1(senha.encode()).hexdigest().upper()
        prefixo = sha1[:5]    # primeiros 5 caracteres
        sufixo  = sha1[5:]    # o resto

        # Manda só o prefixo pra API — a senha nunca é exposta
        url      = f"https://api.pwnedpasswords.com/range/{prefixo}"
        resposta = requests.get(url, timeout=5)

        # A API devolve uma lista assim:
        # SUFIXO1:quantidade
        # SUFIXO2:quantidade
        # Verifica se o sufixo da nossa senha está nessa lista
        for linha in resposta.text.splitlines():
            hash_retornado, quantidade = linha.split(":")
            if hash_retornado == sufixo:
                return int(quantidade)  # retorna quantas vezes foi vazada

        return 0  # não encontrou — senha segura

    except:
        # Se a API estiver fora do ar, não bloqueia o cadastro
        print_aviso("Não foi possível verificar vazamentos agora. Continuando...")
        return 0


# ============================================================
# API 2 — AWESOMEAPI
# Busca a cotação atual do dólar em tempo real
# API brasileira, gratuita, sem precisar de cadastro
# ============================================================

def buscar_cotacao_dolar():
    try:
        url      = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
        resposta = requests.get(url, timeout=5)
        dados    = resposta.json()

        # A resposta vem assim:
        # { "USDBRL": { "bid": "5.72", "ask": "5.73", ... } }
        cotacao = float(dados["USDBRL"]["bid"])
        return cotacao

    except:
        return None  # se falhar, retorna None e trata depois


# ============================================================
# CADASTRO com verificação de senha vazada
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

    # Verifica se a senha já foi vazada em algum ataque
    print_info("Verificando segurança da senha...")
    vazamentos = verificar_senha_vazada(senha)

    if vazamentos > 0:
        print_erro(f"Essa senha apareceu em {vazamentos:,} vazamentos de dados!")
        print_aviso("Escolha uma senha diferente para proteger sua conta.")
        registrar_log(f"Cadastro bloqueado: senha vazada para usuário {nome}")
        return

    print_sucesso("Senha segura! Nenhum vazamento encontrado.")

    usuarios[nome] = {
        "senha": hash_senha(senha),
        "saldo": 1000.0,
        "historico": [],
        "bloqueado": False
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

    if nome.strip() == "":
        print_erro("Digite um nome de usuário.")
        return None

    if nome not in usuarios:
        print_erro("Usuário não encontrado.")
        registrar_log(f"Tentativa de login com usuário inexistente: {nome}")
        return None

    if usuarios[nome].get("bloqueado", False):
        print_erro("Essa conta está bloqueada. Fale com o administrador.")
        registrar_log(f"Tentativa de acesso em conta bloqueada: {nome}")
        return None

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
    saldo    = usuarios[usuario]["saldo"]
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

    usuarios[usuario]["saldo"] -= valor
    usuarios[destino]["saldo"] += valor

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
        # Busca cotação toda vez que abre o menu
        cotacao = buscar_cotacao_dolar()

        print_titulo(f"OLÁ, {usuario.upper()}")

        # Mostra cotação se conseguiu buscar
        if cotacao:
            print(Fore.MAGENTA + f"  💵 Dólar hoje: R$ {cotacao:.2f}")

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