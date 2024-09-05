class Consulta:
    def __init__(self,id, data, hora, Paciente, Medico, sala):
        self.id = id
        self.hora = hora
        self.data = data
        self.Paciente = Paciente()
        self.Medico = Medico()
        self.sala = sala

    def getId(self):
        return self.id

    def getHora(self):
        return self.hora

    def getData(self):
        return self.data

    def getSala(self):
        return self.sala
class Historico:
    def __init__(self):
        self.historico = []


    def imprimirHistorico(self, cpf):
        pass