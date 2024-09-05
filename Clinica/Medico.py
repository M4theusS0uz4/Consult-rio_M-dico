class Medico:
    def __init__(self, crm, especialidade, nome, sobrenome, dataNasc, email, telefone, cep, numero, complemento):
        self.crm = crm
        self.especialidade = especialidade
        self.nome = nome
        self.sobrenome = sobrenome
        self.dataNasc = dataNasc
        self.email = email
        self.telefone = telefone
        self.cep = cep
        self.numero = numero
        self.complemento = complemento

    @property
    def get_crm(self):
        return self.crm

    @property
    def get_especialidade(self):
        return self.especialidade

    @property
    def get_nome(self):
        return self.nome

    @property
    def get_sobrenome(self):
        return self.sobrenome

    @property
    def get_dataNasc(self):
        return self.dataNasc

    @property
    def get_email(self):
        return self.email

    @property
    def get_telefone(self):
        return self.telefone

    @property
    def get_cep(self):
        return self.cep

    @property
    def get_numero(self):
        return self.numero

    @property
    def get_complemento(self):
        return self.complemento