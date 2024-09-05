class Paciente: #Usar classe super() para atributos repetidos
    def __init__(self, nome, sobrenome, telefone, cpf,cep, numero, complemento, data_nascimento, email):
        self.__nome = nome
        self.__sobrenome = sobrenome
        self.__telefone = telefone
        self.__cpf = cpf
        self.__cep = cep
        self.__numero = numero
        self.__complemento = complemento
        self.__data_nascimento = data_nascimento
        self.__email = email

    @property
    def nome(self):
        return self.__nome

    @property
    def sobrenome(self):
        return self.__sobrenome

    @property
    def cpf(self):
        return self.__cpf

    @property
    def cep(self):
        return self.__cep

    @property
    def numero(self):
        return self.__numero

    @property
    def complemento(self):
        return self.__complemento

    @property
    def data_nascimento(self):
        return self.__data_nascimento

    @property
    def email(self):
        return self.__email

    @property
    def telefone(self):
        return self.__telefone