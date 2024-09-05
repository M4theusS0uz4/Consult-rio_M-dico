from Database import Database
class Relatorio:
    def imprimirRelatorio(self):
        """
        Método para imprimir relatórios de consultas realizadas, agendadas ou canceladas.

        O método apresenta um menu para escolha do tipo de relatório:
        1 - Consultas Realizadas
        2 - Consultas Agendadas
        3 - Consultas Canceladas
        4 - Voltar ao menu principal

        Ao selecionar uma opção válida, o método executa consultas SQL no banco de dados para
        recuperar os dados correspondentes e os exibe formatados no console.

        """
        while True:
            db = Database(host="localhost", user="root", password="", database="sistema_consultorio")
            print("=" * 50)
            print("Selecione Relatório Desejado")
            print("=" * 50)
            print("1 - Consultas Indisponíveis\n2 - Consultas Agendadas\n3 - Voltar\n")
            opcao = input("Opção Desejada: ")

            try:
                cursor = db.connection.cursor()
                opcaoNum = int(opcao)
                if opcaoNum in (1, 2, 3, 4):
                    if opcaoNum == 1:
                        try:
                            sql = """select * from consulta where consulta.status = 'I'"""
                            cursor.execute(sql)
                            resultadoConsultasIndisponiveis = cursor.fetchall()
                            if resultadoConsultasIndisponiveis:
                                print("=" * 50)
                                print("Consultas Indisponíveis:")
                                for consulta in resultadoConsultasIndisponiveis:
                                    print("=" * 50)
                                    print(f"ID: {consulta[0]}")
                                    print(f"Horário: {consulta[1]}")
                                    print(f"Data: {consulta[2]}")
                                    print(f"Status: Indisponível")
                                    print(f"Crm: {consulta[4]}")
                                    print(f"ID_Paciente: {consulta[5]}")
                                    print("=" * 50)
                            else:
                                print("Consultas Indisponíveis não encontradas.")
                        except Exception as e:
                            print(f"Erro ao consultar consultas realizadas: {e}")

                    elif opcaoNum == 2:
                        try:
                            sql = """select * from consulta where consulta.status = 'A'"""
                            cursor.execute(sql)
                            resultadoConsultasAgendadas = cursor.fetchall()
                            if resultadoConsultasAgendadas:
                                print("=" * 50)
                                print("Consultas Agendadas:")
                                for consulta in resultadoConsultasAgendadas:
                                    print("=" * 50)
                                    print(f"ID: {consulta[0]}")
                                    print(f"Horário: {consulta[1]}")
                                    print(f"Data: {consulta[2]}")
                                    print(f"Status: Agendada")
                                    print(f"Crm: {consulta[4]}")
                                    print(f"ID_Paciente: {consulta[5]}")
                                print("=" * 50)
                            else:
                                print("Consultas Agendadas não encontradas.")
                        except Exception as e:
                            print(f"Erro ao consultar consultas agendadas: {e}")
                    elif opcaoNum == 3:
                        print("Voltando ao Menu")
                        break
                else:
                    print("Opção não existente no Menu. Tente novamente.")
            except ValueError:
                print("Opção Inválida. Tente Novamente.")
            finally:
                cursor = db.connection.cursor()
                if db.connection.is_connected():
                    cursor.close()
                    db.connection.close()