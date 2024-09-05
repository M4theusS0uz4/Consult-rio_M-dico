from Database import Database
class Historico:
    def __init__(self):
        self.historico = []

    def imprimirHistorico(self, cpf):
        """
        Recupera e imprime o histórico médico de um paciente dado o CPF.

        Conecta-se ao banco de dados, recupera o histórico médico do paciente correspondente ao CPF
        fornecido e imprime as informações formatadas na tela.

        Args:
            cpf (str): O CPF do paciente para o qual o histórico médico será recuperado.

        Returns:
            None

        Raises:
            ValueError: Se o CPF não for uma string válida.
        """
        try:
            # Conecta-se ao banco de dados
            db = Database(host="localhost", user="root", password="", database="sistema_consultorio")

            historico_medico = db.historicoMedico(cpf)

            if historico_medico:
                self.historico = historico_medico

                # Imprime as consultas do histórico médico
                for consulta in self.historico:
                    print("=" * 50)
                    print(f"Data: {consulta[0]}")
                    print(f"Horário: {consulta[1]}")
                    print(f"Status: {consulta[2]}")
                    print(f"Doutor(a): {consulta[3]}")
                    print("=" * 50)
            else:
                print("Não há histórico médico para o CPF informado.")

        except ValueError as ve:
            print(f"Erro: {ve}")

        except Exception as e:
            print(f"Erro desconhecido: {e}")