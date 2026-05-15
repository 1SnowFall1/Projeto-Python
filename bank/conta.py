import json

ARQUIVO = "data/usuarios.json"

def carregar_usuarios():
    with open(ARQUIVO, "r") as f:
        return json.load(f)

def salvar_usuarios(usuarios):
    with open(ARQUIVO, "w") as f:
        json.dump(usuarios, f, indent=4)

def ver_saldo(usuario):
    usuarios = carregar_usuarios()
    saldo = usuarios[usuario]["saldo"]
    print(f"\nSaldo atual: R$ {saldo:.2f}")

def depositar(usuario):
    usuarios = carregar_usuarios()
    valor = float(input("Valor do depósito: R$ "))
    if valor <= 0:
        print("Valor inválido.")
        return
    usuarios[usuario]["saldo"] += valor
    usuarios[usuario]["historico"].append(f"Depósito: +R$ {valor:.2f}")
    salvar_usuarios(usuarios)
    print(f"Depósito de R$ {valor:.2f} realizado!")

def sacar(usuario):
    usuarios = carregar_usuarios()
    valor = float(input("Valor do saque: R$ "))
    if valor <= 0:
        print("Valor inválido.")
        return
    if valor > usuarios[usuario]["saldo"]:
        print("Saldo insuficiente.")
        return
    usuarios[usuario]["saldo"] -= valor
    usuarios[usuario]["historico"].append(f"Saque: -R$ {valor:.2f}")
    salvar_usuarios(usuarios)
    print(f"Saque de R$ {valor:.2f} realizado!")

def transferir(usuario):
    usuarios = carregar_usuarios()
    destino = input("Transferir para (usuário): ")
    if destino not in usuarios:
        print("Usuário destino não encontrado.")
        return
    valor = float(input("Valor: R$ "))
    if valor <= 0 or valor > usuarios[usuario]["saldo"]:
        print("Valor inválido ou saldo insuficiente.")
        return
    usuarios[usuario]["saldo"] -= valor
    usuarios[destino]["saldo"] += valor
    usuarios[usuario]["historico"].append(f"Transferência para {destino}: -R$ {valor:.2f}")
    usuarios[destino]["historico"].append(f"Transferência de {usuario}: +R$ {valor:.2f}")
    salvar_usuarios(usuarios)
    print(f"Transferência de R$ {valor:.2f} para {destino} realizada!")

def ver_historico(usuario):
    usuarios = carregar_usuarios()
    historico = usuarios[usuario]["historico"]
    if not historico:
        print("Nenhuma movimentação ainda.")
        return
    print("\n--- Histórico ---")
    for item in historico:
        print(f"  {item}")