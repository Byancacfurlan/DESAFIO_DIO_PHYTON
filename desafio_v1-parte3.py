from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime
import textwrap

class cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def acidionar_conta(self, conta):
        self.contas.append(conta)
    
class pessoa_fisica(cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf
        
class conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = historico()

    @classmethod    
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico  
    
    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor>saldo

        if excedeu_saldo:
            print("__Operação falhou! Você não tem saldo suficiente!__")

        elif valor >0:
            self._saldo-= valor
            print("\n ++SALDO REALIZADO COM SUCESSO!++")
            return True
        
        else:
            print("__Operação falhou. Você informou um valor inválido!")
        return False
        
    def depositar(self, valor):
        if valor >0:
            self._saldo += valor
            print("\n ++DEPÓSITO REALIZADO COM SUCESSO!++")
        else:
            print("\n __Operação falhou! Valor informado inválido!__")
            return False
        return True
    
class conta_corrente(conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques
    
    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"]==saque.__name__]
        )
        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques>= self.limite_saques

        if excedeu_limite:
            print("\n __Operação falhou! Você excedeu o limite do valordo dia!__")
        elif excedeu_saques:
            print("\n __Operação falhou! Você excedeu o limite de saque do dia!__")
        else:
            return super().sacar(valor)
        return False
    
    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """

class historico:
    def __init__(self):
        self._transacoes = []
    
    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime
                ("%d-%m-%Y %H:%M:%s"),
            }
        )

class transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def regitrar(self,conta):
        pass

class saque(transacao):
    def __init__(self,valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
            
class deposito(transacao):
    def __init__(self,valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
            
def menu():  
    menu = """
    [1] Depositar
    [2] Sacar
    [3] Extrato
    [4] Nova Conta
    [5] Listar contas
    [6] Novo Usuário
    [7] Sair
    """
    return input(textwrap.dedent(menu))

def filtar_cliente(cpf, clientes):
    cliente_filtrados = [cliente for cliente in clientes if cliente.cpf ==cpf]
    return cliente_filtrados[0] if cliente_filtrados else None

def recuperar_conta_cliente(cliente):
     if not cliente.contas:
        print("\n__Cliente não possui conta!__")
        return
    
    # FIXME: nao permite cliente escolher a conta
     return cliente.contas[0]

def depositar(clientes):
    cpf=input("Informe o CPF do cliente: ")
    cliente = filtar_cliente(cpf,cliente)
    if not clientes:
            print("\n__Cliente não encontrado__")
            return  
    valor = float(input("Informe o valor do depósito: "))
    transacao = deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    

def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtar_cliente(cpf, clientes)
    if not cliente:
        print("\n__Cliente não encontrado!__")
        return
    
    valor = float(input("Informe o valor do saque: "))
    transacao = saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)
    
def exibir_extrato(clientes):
   cpf = input("Informe o CPF do cliente: ")
   cliente = filtar_cliente(cpf, clientes)

   if not cliente:
       print("\n Cliente não encontrado!")
       return
   
   conta = recuperar_conta_cliente(cliente)
   if not conta:
       return
   
   print("\n___________EXTRATO___________")
   transacoes = conta.historico.transacoes

   extrato = ""
   if not transacoes:
       extrato = "Não foram relizadas movimentações na conta!"

   else:
       for transacao in transacao:
           extrato += f"\n{transacao['tipo']}:\n\tR${transacao['valor']:.2f}"
   
   print(extrato)
   print(f"\n Saldo: \n\tR$ {conta.saldo:.2f}")
   print("\n_____________________________")

def criar_cliente(clientes):
    cpf = input("Digite O CPF (somente números): ")
    cliente = filtar_cliente(cpf,clientes)

    if cliente:
        print("\n Já existe cadastro com esse CPF!")
        return
    
    nome = input("Digite o nome completo: ")
    data_nascimento = input("Digite a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Digitr o endereço (logradouro, n - bairro- cidade/sigla estado): ")

    cliente= pessoa_fisica(nome=nome, data_nascimento=data_nascimento,cpf=cpf, endereco=endereco)
    clientes.append(cliente)

    print("Usuário cadastrado com sucesso!")
    


def criar_conta(numero_conta, clientes, contas):
    cpf = input ("Digite o CPF do usuário: ")
    cliente = filtar_cliente(cpf,clientes)

    if not cliente:
        print("\n Cliente não encontrado!")
        return
    
    conta = conta_corrente.nova_conta(cliente=cliente, numero=numero_conta)
    cliente.append(conta)
    cliente.contas.append(conta)

    print("\n ++Conta criada com sucesso!++")

def listar_contas(contas):
    for conta in contas:
        print("="*100)
        print(textwrap.dedent(str(conta)))

def main():
    
    clientes= []
    contas = []
    
    while True:
        opcao = menu()
        if opcao == "1":
            depositar(clientes)

        elif opcao == "2":
            sacar(clientes)

        elif opcao == "3":
            exibir_extrato(clientes)

        elif opcao == "4":
           criar_cliente(clientes)
                          
        elif opcao == "5":
            listar_contas(contas)
        
        elif opcao== "6":
            numer_conta= len(contas)+1
            criar_conta(numer_conta, clientes, contas)
        
        elif opcao =="7":
            break

        else:
            print("Operação inválida, por avor selecione novamente a opção desejada")

main()