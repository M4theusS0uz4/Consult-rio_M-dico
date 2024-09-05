import bcrypt
import mysql.connector
from datetime import datetime, timedelta
from Clinica.Paciente import Paciente
from Medico import Medico

class Database:
    """
    Classe que gerencia a conexão e operações com o banco de dados do sistema de consultório médico.
    """

    def __init__(self, host="localhost", user="root", password="", database="sistema_consultorio"):
        """
        Inicializa a conexão com o banco de dados MySQL.

        Args:
            host (str): Endereço do servidor MySQL.
            user (str): Nome de usuário para autenticação no MySQL.
            password (str): Senha para autenticação no MySQL.
            database (str): Nome do banco de dados MySQL a ser utilizado.
        """
        try:
            self.connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        except mysql.connector.Error as erro:
            print(f"Erro enquanto conecta no MySQL: {erro}")

    def cadastrarPaciente(self, paciente):
        """
        Cadastra um novo paciente no banco de dados.

        Args:
            paciente (Paciente): Objeto Paciente contendo as informações do paciente a ser cadastrado.
        """
        cursor = self.connection.cursor()
        try:
            # Iniciar transação se não estiver em andamento
            if not self.connection.in_transaction:
                self.connection.start_transaction()

            # Inserir dados de endereço
            sql_endereco = "INSERT INTO endereco (cep, numero, complemento) VALUES (%s, %s, %s)"
            val_endereco = (paciente.cep, paciente.numero, paciente.complemento)
            cursor.execute(sql_endereco, val_endereco)

            if cursor.rowcount == 1:
                id_endereco = cursor.lastrowid
                # Inserir dados do paciente
                sql_paciente = "INSERT INTO paciente (nome, cpf, data_nasc, email, telefone, id_endereco) VALUES (%s, %s, %s, %s, %s, %s)"
                nome_completo = f"{paciente.nome} {paciente.sobrenome}"
                val_paciente = (nome_completo, paciente.cpf, paciente.data_nascimento, paciente.email, paciente.telefone, id_endereco)
                cursor.execute(sql_paciente, val_paciente)
                self.connection.commit()

                if cursor.rowcount == 1:
                    print("Paciente cadastrado com sucesso.")
                else:
                    print("Erro ao cadastrar paciente, tente novamente.")
            else:
                print("Erro ao cadastrar endereço, tente novamente.")
        except mysql.connector.Error as e:
            print(f"Erro: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def descobrirIdPaciente(self, cpf):
        """
        Obtém o ID de um paciente a partir do CPF.

        Args:
            cpf (str): CPF do paciente a ser pesquisado.

        Returns:
            int: ID do paciente encontrado, ou None se não encontrado.
        """
        cursor = self.connection.cursor()
        try:
            sql = "SELECT id_paciente FROM paciente WHERE cpf = %s"
            cursor.execute(sql, (cpf,))
            resultado = cursor.fetchone()
            if resultado:
                return resultado[0]  # Retorna o ID do paciente encontrado
            else:
                print("Paciente não encontrado.")
                return None
        except mysql.connector.Error as e:
            print(f"Erro ao buscar ID do paciente: {e}")
            return None
        finally:
            cursor.close()

    def cadastrarMedico(self, medico):
        """
        Cadastra um novo médico no banco de dados.

        Args:
            medico (Medico): Objeto Medico contendo as informações do médico a ser cadastrado.
        """
        cursor = self.connection.cursor()
        try:
            # Verifica se uma transação já está em andamento
            if not self.connection.in_transaction:
                self.connection.start_transaction()

            # Verifica se a especialidade já existe no banco de dados
            sql_especialidade = "SELECT especialidade_id FROM especialidade WHERE especialidade = %s"
            val_especialidade = medico.get_especialidade
            cursor.execute(sql_especialidade, (val_especialidade,))
            resultado_especialidade = cursor.fetchone()

            if resultado_especialidade:
                especialidade_id = resultado_especialidade[0]
            else:
                # Se a especialidade não existe, insere-a e obtém o id
                sql_inserir_especialidade = "INSERT INTO especialidade (especialidade) VALUES (%s)"
                cursor.execute(sql_inserir_especialidade, (val_especialidade,))
                self.connection.commit()
                especialidade_id = cursor.lastrowid

            # Insere o endereço do médico
            sql_endereco = "INSERT INTO endereco (cep, numero, complemento) VALUES (%s, %s, %s)"
            val_endereco = medico.get_cep, medico.get_numero, medico.get_complemento
            cursor.execute(sql_endereco, val_endereco)
            self.connection.commit()
            id_endereco = cursor.lastrowid

            # Insere os dados do médico
            sql_medico = "INSERT INTO medico (crm, nome, data_nasc, email, telefone, id_endereco) VALUES (%s, %s, %s, %s, %s, %s)"
            nome_completo = medico.get_nome + " " + medico.get_sobrenome
            val_medico = medico.get_crm, nome_completo, medico.get_dataNasc, medico.get_email, medico.get_telefone, id_endereco
            cursor.execute(sql_medico, val_medico)

            # Relaciona o médico com a especialidade na tabela especialidade_medico_aux
            sql_especialidade_medico = "INSERT INTO especialidade_medico (especialidade_id, crm) VALUES (%s, %s)"
            val_especialidade_medico = especialidade_id, medico.get_crm
            cursor.execute(sql_especialidade_medico, val_especialidade_medico)

            # Commita a transação
            self.connection.commit()
            print("Médico adicionado com sucesso.")
        except Exception as e:
            # Em caso de erro, faz rollback da transação
            self.connection.rollback()
            print(f"Erro ao cadastrar médico: {e}")
        finally:
            # Fecha o cursor
            cursor.close()

    def padronizadoConsultas(self):
        cursor = self.connection.cursor()
        dias_ano = []
        data = datetime.today()
        ano_atual = data.year

        while data.year == ano_atual:
            dias_ano.append(data.strftime('%Y-%m-%d'))
            data += timedelta(days=1)

        try:
            sql = "SELECT crm FROM medico"
            cursor.execute(sql)
            medicos = cursor.fetchall()

            horas = ["07:00:00", "08:00:00", "09:00:00", "10:00:00",
                     "13:00:00", "14:00:00", "15:00:00", "16:00:00", "17:00:00"]

            for medico in medicos:
                crm = medico[0]
                for dia in dias_ano:
                    if datetime.strptime(dia, '%Y-%m-%d').weekday() not in (6, 0):
                        for hora in horas:
                            sql_check = "SELECT COUNT(*) FROM consulta WHERE crm = %s AND data = %s AND horario = %s"
                            cursor.execute(sql_check, (crm, dia, hora))
                            result = cursor.fetchone()

                            if result[0] == 0:
                                sql_insert = "INSERT INTO consulta (horario, data, status, crm) VALUES (%s, %s, 'D', %s)"
                                cursor.execute(sql_insert, (hora, dia, crm))
                    else:
                        for hora in horas:
                            sql_check = "SELECT COUNT(*) FROM consulta WHERE crm = %s AND data = %s AND horario = %s"
                            cursor.execute(sql_check, (crm, dia, hora))
                            result = cursor.fetchone()

                            if result[0] == 0:
                                sql_insert = "INSERT INTO consulta (horario, data, status, crm) VALUES (%s, %s, 'I', %s)"
                                cursor.execute(sql_insert, (hora, dia, crm))

            self.connection.commit()
        except mysql.connector.Error as e:
            print(f"Erro: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def descobrirNome(self, crm):
        """
        Obtém o nome de um médico a partir do CRM.

        Args:
            crm (str): CRM do médico a ser pesquisado.

        Returns:
            str: Nome do médico encontrado, ou None se não encontrado.
        """
        cursor = self.connection.cursor()
        try:
            sql_checknome = "SELECT nome FROM medico WHERE crm = %s"
            cursor.execute(sql_checknome, (crm,))
            nome = cursor.fetchone()
            return nome[0] if nome else None
        except mysql.connector.Error as e:
            print(f"Erro: {e}")
        finally:
            cursor.close()

    def descobrirCrm(self, nome_dr):
        """
        Descobre o CRM de um médico dado seu nome.

        Args:
            nome_dr (str): Nome do médico.

        Returns:
            str: CRM do médico se encontrado, None caso contrário.
        """
        cursor = self.connection.cursor()
        try:
            sql_checkcrm = "SELECT crm FROM medico WHERE nome = %s"
            cursor.execute(sql_checkcrm, (nome_dr,))
            crm = cursor.fetchone()
            return crm[0] if crm else None
        except mysql.connector.Error as e:
            print(f"Erro: {e}")
        finally:
            cursor.close()

    def indisponibilizarHorario(self, nome_dr, data, horario):
        """
        Indisponibiliza um horário de consulta para um médico específico em uma data específica.

        Args:
            nome_dr (str): Nome do médico.
            data (str): Data da consulta no formato 'YYYY-MM-DD'.
            horario (str): Horário da consulta no formato 'HH:MM:SS'.
        """
        crm = self.descobrirCrm(nome_dr)
        cursor = self.connection.cursor()
        try:
            sql_check = "SELECT status FROM consulta WHERE crm = %s AND data = %s AND horario = %s"
            cursor.execute(sql_check, (crm, data, horario))
            status = cursor.fetchone()

            sql_indisp = "UPDATE consulta SET status = 'I' WHERE crm = %s AND data = %s AND horario = %s"
            cursor.execute(sql_indisp, (crm, data, horario))
            self.connection.commit()

            if status and status[0] == 'A':
                print('Consulta desmarcada.')
            else:
                print('Horário indisponibilizado.')
        except mysql.connector.Error as e:
            print(f"Erro: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def disponibilizarHorario(self, nome_dr, data, horario):
        """
        Disponibiliza um horário de consulta para um médico específico em uma data específica.

        Args:
            nome_dr (str): Nome do médico.
            data (str): Data da consulta no formato 'YYYY-MM-DD'.
            horario (str): Horário da consulta no formato 'HH:MM:SS'.
        """
        crm = self.descobrirCrm(nome_dr)
        cursor = self.connection.cursor()
        try:
            sql_check = "SELECT status FROM consulta WHERE crm = %s AND data = %s AND horario = %s"
            cursor.execute(sql_check, (crm, data, horario))
            status = cursor.fetchone()

            sql_disp = "UPDATE consulta SET status = 'D' WHERE crm = %s AND data = %s AND horario = %s"
            cursor.execute(sql_disp, (crm, data, horario))
            self.connection.commit()

            if status and status[0] == 'A':
                print('Consulta desmarcada.')
            else:
                print('Horário disponibilizado.')
        except mysql.connector.Error as e:
            print(f"Erro: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def listarEspecialidades(self):
        """
        Lista todas as especialidades cadastradas no sistema.

        Returns:
            list: Lista de tuplas contendo as especialidades cadastradas.
                  Cada tupla contém um único valor de especialidade.
        """
        cursor = self.connection.cursor()
        try:
            sql = "SELECT especialidade FROM especialidade"
            cursor.execute(sql)
            especialidades = cursor.fetchall()
            return especialidades
        except mysql.connector.Error as e:
            print(f"Erro ao listar especialidades: {e}")
            return None
        finally:
            cursor.close()

    def mostrarMedicosPorEspecialidade(self, especialidade):
        """
        Lista todos os médicos associados a uma especialidade específica.

        Args:
            especialidade (str): Especialidade do médico.

        Returns:
            list: Lista de tuplas contendo os CRM e nomes dos médicos associados à especialidade.
        """
        cursor = self.connection.cursor()
        try:
            # Primeiro, obtemos o ID da especialidade
            sql_especialidade_id = "SELECT especialidade_id FROM especialidade WHERE especialidade = %s"
            cursor.execute(sql_especialidade_id, (especialidade,))
            especialidade_id = cursor.fetchone()

            if especialidade_id:
                especialidade_id = especialidade_id[0]

                # Agora buscamos os médicos associados a essa especialidade pelo ID na tabela especialidade_medico
                sql = """
                    SELECT medico.crm, medico.nome
                    FROM medico
                    INNER JOIN especialidade_medico ON medico.crm = especialidade_medico.crm
                    WHERE especialidade_medico.especialidade_id = %s
                """
                cursor.execute(sql, (especialidade_id,))
                medicos = cursor.fetchall()
                return medicos
            else:
                print(f"Especialidade '{especialidade}' não encontrada.")
                return None
        except Exception as e:
            print(f"Erro ao buscar médicos por especialidade: {e}")
            return None
        finally:
            cursor.close()

    def mostrarConsultasDisponiveis(self, crm, dia):
        """
        Lista todas as consultas disponíveis para um médico em um determinado dia.

        Args:
            crm (str): CRM do médico.
            dia (str): Data da consulta no formato 'YYYY-MM-DD'.

        Returns:
            list: Lista de tuplas contendo data, horário, status e nome do médico das consultas disponíveis.
        """
        cursor = self.connection.cursor()
        try:
            sql = """
                SELECT consulta.data, consulta.horario, consulta.status, medico.nome
                FROM consulta
                INNER JOIN medico ON consulta.crm = medico.crm
                WHERE consulta.crm = %s AND consulta.data = %s AND consulta.status = 'D'
                """
            cursor.execute(sql, (crm, dia))
            consultas = cursor.fetchall()
            return consultas
        except Exception as e:
            print(f"Erro: {e}")
        finally:
            cursor.close()

    def marcarConsulta(self, nome_dr, data, hora, cpf):
        """
        Marca uma consulta para um paciente com um médico específico.

        Args:
            nome_dr (str): Nome do médico.
            data (str): Data da consulta no formato 'YYYY-MM-DD'.
            hora (str): Horário da consulta no formato 'HH:MM:SS'.
            cpf (str): CPF do paciente.
        """
        crm = self.descobrirCrm(nome_dr)
        id_paciente = self.descobrirIdPaciente(cpf)
        cursor = self.connection.cursor()
        try:
            sql = "UPDATE consulta SET id_paciente = %s, status = 'A' WHERE crm = %s AND data = %s AND horario = %s"
            cursor.execute(sql, (id_paciente, crm, data, hora))
            self.connection.commit()
            if cursor.rowcount == 1:
                print("Consulta marcada com sucesso!")
            else:
                print("Erro ao marcar consulta.")
        except mysql.connector.Error as e:
            print(f"Erro: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def historicoMedico(self, cpf):
        """
        Retorna o histórico de consultas de um paciente.

        Args:
            cpf (str): CPF do paciente.

        Returns:
            list: Lista de tuplas contendo informações das consultas (data, horário, status e nome do médico).
        """
        cursor = self.connection.cursor()
        try:
            sql_paciente = "SELECT id_paciente FROM paciente WHERE cpf = %s"
            val_paciente = (cpf,)
            cursor.execute(sql_paciente, val_paciente)
            resultado_paciente = cursor.fetchone()

            if resultado_paciente:
                id_paciente = resultado_paciente[0]

                sql_consultas = """
                          SELECT consulta.data, consulta.horario, consulta.status, medico.crm
                          FROM consulta 
                          INNER JOIN medico  ON consulta.crm = medico.crm
                          WHERE consulta.id_paciente = %s AND consulta.status IN ('I', 'R', 'A','D')
                          """
                val_consultas = (id_paciente,)
                cursor.execute(sql_consultas, val_consultas)
                resultados_consultas = cursor.fetchall()

                if resultados_consultas:
                    lista_consultas = []
                    status_map = {'I': 'Indisponível', 'R': 'Realizada', 'A': 'Agendada', 'D': 'Disponível'}

                    for consulta in resultados_consultas:
                        status_formatado = status_map.get(consulta[2], "Desconhecido")
                        nome_medico = self.descobrirNome(consulta[3])
                        consulta_tupla = (
                            f"{consulta[0]}",
                            f"{consulta[1]}",
                            f"{status_formatado}",
                            f"{nome_medico}"
                        )
                        lista_consultas.append(consulta_tupla)

                    return lista_consultas
            return None
        except mysql.connector.Error as e:
            print(f"Erro: {e}")
        finally:
            cursor.close()

    def mostrarHorarios(self, nome_dr):
        """
        Mostra os horários de consulta disponíveis de um médico.

        Args:
            nome_dr (str): Nome do médico.

        Returns:
            list: Lista de tuplas contendo informações dos horários de consulta (ID_Consulta, Data, Horário, Status).
        """
        crm = self.descobrirCrm(nome_dr)
        cursor = self.connection.cursor()
        try:
            sql_horarios = """
                      SELECT c.id_consulta, c.data, c.horario, c.status
                      FROM consulta c
                      INNER JOIN medico m ON c.crm = m.crm
                      WHERE c.crm = %s
                      """
            val = (crm,)
            cursor.execute(sql_horarios, val)
            resultados = cursor.fetchall()

            if resultados:
                lista_horarios = []
                status_map = {'I': 'Indisponível', 'R': 'Realizada', 'A': 'Agendada', 'D': 'Disponível'}

                for consulta in resultados:
                    status_formatado = status_map.get(consulta[3], "Desconhecido")
                    horario_tupla = (
                        f"ID_Consulta: {consulta[0]}",
                        f"Data: {consulta[1]}",
                        f"Horário: {consulta[2]}",
                        f"Status: {status_formatado}"
                    )
                    lista_horarios.append(horario_tupla)

                return lista_horarios
            else:
                print("Nenhuma consulta identificada.")
                return None
        except mysql.connector.Error as e:
            print(f"Erro: {e}")
        finally:
            cursor.close()

    def criar_adm(self, username, password):
        """
        Cria um novo administrador no sistema.

        Args:
            username (str): Nome de usuário do administrador.
            password (str): Senha do administrador.

        Returns:
            bool: True se o administrador foi criado com sucesso, False caso contrário.
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM usuario")
            count = cursor.fetchone()[0]
            if count > 0:
                print("Administrador já existente.")
                return True
            else:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(8))
                cursor.execute(
                    "INSERT INTO usuario (username, password) VALUES (%s, %s)",
                    (username, hashed_password.decode('utf-8'))
                )
                self.connection.commit()
                print("Administrador criado com sucesso.")
                return True
        except mysql.connector.Error as e:
            print(f"Erro ao criar administrador: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def autenticar_usuario(self, username, password):
        """
        Autentica um usuário no sistema.

        Args:
            username (str): Nome de usuário.
            password (str): Senha do usuário.

        Returns:
            bool: True se a autenticação for bem-sucedida, False caso contrário.
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT password FROM usuario WHERE username = %s", (username,))
            row = cursor.fetchone()

            if row:
                hashed_password = row[0].encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                    return True
                else:
                    return False
            else:
                return False
        except mysql.connector.Error as e:
            print(f"Erro ao autenticar usuário: {e}")
            return False
        finally:
            cursor.close()

    def padronizadoConsultas(self):
        """
        Cria consultas padrão para todos os médicos em dias úteis do ano atual.
        """
        cursor = self.connection.cursor()
        dias_ano = []
        data = datetime.today()
        ano_atual = data.year

        while data.year == ano_atual:
            dias_ano.append(data.strftime('%Y-%m-%d'))
            data += timedelta(days=1)

        try:
            sql = "SELECT crm FROM medico"
            cursor.execute(sql)
            medicos = cursor.fetchall()

            horas = ["07:00:00", "08:00:00", "09:00:00", "10:00:00", "13:00:00", "14:00:00", "15:00:00", "16:00:00",
                     "17:00:00"]

            for medico in medicos:
                crm = medico[0]

                # Verifica se o médico já tem consultas
                sql_check = "SELECT COUNT(*) FROM consulta WHERE crm = %s"
                cursor.execute(sql_check, (crm,))
                consulta_count = cursor.fetchone()[0]

                if consulta_count == 0:
                    for dia in dias_ano:
                        if datetime.strptime(dia, '%Y-%m-%d').weekday() not in (6, 0):
                            for hora in horas:
                                sql_insert = "INSERT INTO consulta (horario, data, status, crm) VALUES (%s, %s, 'D', %s)"
                                cursor.execute(sql_insert, (hora, dia, crm))
                        else:
                            for hora in horas:
                                sql_insert = "INSERT INTO consulta (horario, data, status, crm) VALUES (%s, %s, 'I', %s)"
                                cursor.execute(sql_insert, (hora, dia, crm))

            self.connection.commit()
        except mysql.connector.Error as e:
            print(f"Erro: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def historicoMedico(self, cpf):
        """
        Retorna o histórico médico de um paciente.

        Args:
            cpf (str): CPF do paciente.

        Returns:
            list: Lista de tuplas contendo informações das consultas (data, horário, status e nome do médico).
        """
        cursor = self.connection.cursor()
        try:
            sql_paciente = "SELECT id_paciente FROM paciente WHERE cpf = %s"
            val_paciente = (cpf,)
            cursor.execute(sql_paciente, val_paciente)
            resultado_paciente = cursor.fetchone()

            if resultado_paciente:
                id_paciente = resultado_paciente[0]

                sql_consultas = """
                       SELECT consulta.data, consulta.horario, consulta.status, medico.crm
                       FROM consulta 
                       INNER JOIN medico  ON consulta.crm = medico.crm
                       WHERE consulta.id_paciente = %s AND consulta.status IN ('I', 'R', 'A','D')
                       """
                val_consultas = (id_paciente,)
                cursor.execute(sql_consultas, val_consultas)
                resultados_consultas = cursor.fetchall()

                if resultados_consultas:
                    lista_consultas = []
                    status_map = {'I': 'Indisponível', 'R': 'Realizada', 'A': 'Agendada', 'D': 'Disponível'}

                    for consulta in resultados_consultas:
                        status_formatado = status_map.get(consulta[2], "Desconhecido")
                        nome_medico = self.descobrirNome(consulta[3])
                        consulta_tupla = (
                            f"Data: {consulta[0]}",
                            f"Horário: {consulta[1]}",
                            f"Status: {status_formatado}",
                            f"Doutor(a): {nome_medico}"
                        )
                        lista_consultas.append(consulta_tupla)

                    return lista_consultas
            return None
        except mysql.connector.Error as e:
            print(f"Erro: {e}")
        finally:
            cursor.close()

    def mostrarHorarios(self, nome_dr):
        """
        Mostra os horários disponíveis de um médico.

        Args:
            nome_dr (str): Nome do médico.

        Returns:
            list: Lista de tuplas contendo informações dos horários (ID da consulta, data, horário e status).
        """
        crm = self.descobrirCrm(nome_dr)
        cursor = self.connection.cursor()
        try:
            sql_horarios = """
                   SELECT c.id_consulta, c.data, c.horario, c.status
                   FROM consulta c
                   INNER JOIN medico m ON c.crm = m.crm
                   WHERE c.crm = %s
                   """
            val = (crm,)
            cursor.execute(sql_horarios, val)
            resultados = cursor.fetchall()

            if resultados:
                lista_horarios = []
                status_map = {'I': 'Indisponível', 'R': 'Realizada', 'A': 'Agendada', 'D': 'Disponível'}

                for consulta in resultados:
                    status_formatado = status_map.get(consulta[3], "Desconhecido")
                    horario_tupla = (
                        f"ID_Consulta: {consulta[0]}",
                        f"Data: {consulta[1]}",
                        f"Horário: {consulta[2]}",
                        f"Status: {status_formatado}"
                    )
                    lista_horarios.append(horario_tupla)

                return lista_horarios
            else:
                print("Nenhuma consulta identificada.")
                return None
        except mysql.connector.Error as e:
            print(f"Erro: {e}")
        finally:
            cursor.close()

    def criar_adm(self, username, password):
        """
        Cria um novo administrador no sistema.

        Args:
            username (str): Nome de usuário do administrador.
            password (str): Senha do administrador.

        Returns:
            bool: True se o administrador foi criado com sucesso, False caso contrário.
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM usuario")
            count = cursor.fetchone()[0]
            if count > 0:
                return True
            else:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(8))
                cursor.execute(
                    "INSERT INTO usuario (username, password) VALUES (%s, %s)",
                    (username, hashed_password.decode('utf-8'))
                )
                self.connection.commit()
                print("Administrador criado com sucesso.")
                return True
        except mysql.connector.Error as e:
            print(f"Erro ao criar administrador: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def autenticar_usuario(self, username, password):
        """
        Autentica um usuário no sistema.

        Args:
            username (str): Nome de usuário.
            password (str): Senha.

        Returns:
            bool: True se a autenticação for bem-sucedida, False caso contrário.
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT password FROM usuario WHERE username = %s", (username,))
            row = cursor.fetchone()

            if row:
                hashed_password = row[0].encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                    return True
                else:
                    return False
            else:
                return False
        except mysql.connector.Error as e:
            print(f"Erro ao autenticar usuário: {e}")
            return False
        finally:
            cursor.close()

    def atualizarPaciente(self, cpf, novo_nome, novo_email):
        """
        Atualiza informações de um paciente no banco de dados.

        Args:
            cpf (str): CPF do paciente a ser atualizado.
            novo_nome (str): Novo nome do paciente.
            novo_email (str): Novo email do paciente.
        """
        cursor = self.connection.cursor()
        try:
            sql_update = "UPDATE paciente SET nome = %s, email = %s WHERE cpf = %s"
            cursor.execute(sql_update, (novo_nome, novo_email, cpf))
            self.connection.commit()

            if cursor.rowcount == 1:
                print("Paciente atualizado com sucesso.")
            else:
                print("Nenhum paciente atualizado.")
        except mysql.connector.Error as e:
            print(f"Erro ao atualizar paciente: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def atualizarMedico(self, crm, novo_nome, novo_email):
        """
        Atualiza informações de um médico no banco de dados.

        Args:
            crm (str): CRM do médico a ser atualizado.
            novo_nome (str): Novo nome do médico.
            novo_email (str): Novo email do médico.
        """
        cursor = self.connection.cursor()
        try:
            sql_update = "UPDATE medico SET nome = %s, email = %s WHERE crm = %s"
            cursor.execute(sql_update, (novo_nome, novo_email, crm))
            self.connection.commit()

            if cursor.rowcount == 1:
                print("Médico atualizado com sucesso.")
            else:
                print("Nenhum médico atualizado.")
        except mysql.connector.Error as e:
            print(f"Erro ao atualizar médico: {e}")
            self.connection.rollback()
        finally:
            cursor.close()