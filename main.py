from auth.login import cadastrar, login
from bank.conta import ver_saldo, depositar, sacar, transferir, ver_historico

def menu_banco(usuario):
    opcoes = {
        "1": ("Ver saldo", ver_saldo),
        "2": ("Depositar", depositar),
        "3": ("Sacar", sacar),
        "4": ("Transferir", transferir),
        "5": ("Histórico", ver_historico),
    }
    while True:
        print("\n========== BANCO DIGITAL ==========")
        for k, (desc, _) in opcoes.items():
            print(f"  {k}. {desc}")
        print("  0. Sair")
        escolha = input("Opção: ")
        if escolha == "0":
            print("Até logo!")
            break
        elif escolha in opcoes:
            opcoes[escolha][1](usuario)
        else:
            print("Opção inválida.")

def menu_inicial():
    while True:
        print("\n====== BEM-VINDO AO BANCO DIGITAL ======")
        print("  1. Login")
        print("  2. Cadastrar")
        print("  0. Sair")
        escolha = input("Opção: ")
        if escolha == "1":
            usuario = login()
            if usuario:
                menu_banco(usuario)
        elif escolha == "2":
            cadastrar()
        elif escolha == "0":
            break

if __name__ == "__main__":
    menu_inicial()