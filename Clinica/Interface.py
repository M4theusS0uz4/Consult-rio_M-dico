import stdiomask
from Clinica.Consulta import Historico
from Clinica.Medico import Medico
from Clinica.Paciente import Paciente
from Clinica.Database import Database
from Clinica.Relatorio import Relatorio

def solicitar_credenciais():
    """
    Solicita as credenciais de login do usuário.

    Retorna:
        tuple: Uma tupla contendo o nome de usuário e a senha.
    """
    # Solicita o nome de usuário
    username = input("Digite seu nome de usuário: ")

    # Solicita a senha com asteriscos
    password = stdiomask.getpass("Digite sua senha: ")
    return username, password

def mostrar_especialidades(db):
    """
    Mostra as especialidades disponíveis na clínica.

    Args:
        db (Database): Instância do banco de dados.
    """
    especialidades = db.listarEspecialidades()
    if especialidades:
        print("Especialidades disponíveis:")
        for especialidade in especialidades:
            print(f"- {especialidade[0]}")
    else:
        print("Não há especialidades cadastradas no momento.")

def mostrar_horarios(nome_medico):
    """
    Mostra os horários disponíveis de um médico específico.

    Args:
        nome_medico (str): Nome do médico.
    """
    db = Database()
    horarios = db.mostrarHorarios(nome_medico)
    if horarios:
        print("Horários do médico:")
        for horario in horarios:
            print(f"ID_Consulta: {horario[0]}, Data: {horario[1]}, Horário: {horario[2]}, Status: {horario[3]}")
    else:
        print(f"Nenhum horário encontrado para o médico {nome_medico}.")

def formatar_cpf(cpf):
    """
    Formata um CPF para o formato XXX.XXX.XXX-XX.

    Args:
        cpf (str): O CPF a ser formatado.

    Retorna:
        str: O CPF formatado.

    Raises:
        ValueError: Se o CPF não contiver 11 dígitos.
    """
    cpf = ''.join(filter(str.isdigit, str(cpf)))
    if len(cpf) != 11:
        raise ValueError("O CPF deve conter 11 dígitos.")
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

def statusOff():
    """
    Desativa o status do sistema.

    Retorna:
        bool: Sempre retorna False.
    """
    return False

# Inicialização do status do sistema
status = True
while status:
    db = Database()
    username, password = solicitar_credenciais()
    credenciais = [username, password]
    db.criar_adm(username,password)
    login = db.autenticar_usuario(credenciais[0], credenciais[1])
    if login:
        while True:
            print("=" * 50)
            print("Gerenciamento banco de dados Clínica")
            print("=" * 50)
            print("Menu:\n"
                  "1. Cadastrar Paciente\n"
                  "2. Cadastrar Médico\n"
                  "3. Agendar consulta\n"
                  "4. Gerenciar horários e consultas\n"
                  "5. Gerar relatório\n"
                  "6. Consultar histórico médico\n"
                  "7. Atualizar cadastro\n"
                  "8. Sair\n")
            try:
                x = input("O que deseja realizar?: ")
                if x == "1":
                    # Cadastro de Paciente
                    p_nome = input("Insira o Primeiro nome do paciente: ")
                    p_sobrenome = input("Insira Sobrenome do paciente: ")
                    p_cpf = formatar_cpf(input("Insira CPF do paciente: "))
                    p_telefone = input("Insira Número de Telefone do paciente: ")
                    p_cep = input("Insira CEP do paciente: ")
                    p_numero = input("Insira Número Residencial do paciente: ")
                    p_complemento = input("Insira Complemento do paciente: ")
                    p_datanasc = input("Insira Data de nascimento do paciente (AAAA-MM-DD): ")
                    p_email = input("Insira email do paciente: ")
                    p = Paciente(p_nome, p_sobrenome, p_telefone, p_cpf, p_cep, p_numero, p_complemento, p_datanasc, p_email)
                    db.cadastrarPaciente(p)
                elif x == "2":
                    # Cadastro de Médico
                    m_nome = input("Insira nome do médico: ")
                    m_sobrenome = input("Insira sobrenome do médico: ")
                    m_crm = input("Insira CRM do médico: ")
                    m_especialidade = input("Insira especialidade do médico: ")
                    m_datanasc = input("Insira data de nascimento do médico (AAAA-MM-DD): ")
                    m_email = input("Insira email do médico: ")
                    m_telefone = input("Insira telefone do médico: ")
                    m_cep = input("Insira CEP do médico: ")
                    m_numero = input("Insira Número Residencial do médico: ")
                    m_complemento = input("Insira Complemento do médico: ")
                    # Criar um objeto Medico com os dados fornecidos
                    medico = Medico(m_crm, m_especialidade, m_nome, m_sobrenome, m_datanasc, m_email, m_telefone, m_cep,
                                    m_numero, m_complemento)

                    # Chamar o método cadastrarMedico da classe Database para inserir o médico no banco de dados
                    db.cadastrarMedico(medico)
                    db.padronizadoConsultas()
                elif x == "3":
                    # Agendar consulta
                    mostrar_especialidades(db)
                    especialidade = input("Digite Especialidade Desejada: ")
                    medicos = db.mostrarMedicosPorEspecialidade(especialidade)
                    if medicos:
                        print("Médicos disponíveis para a especialidade de", especialidade)
                        for medico in medicos:
                            print(f"CRM: {medico[0]}, Nome: {medico[1]}")
                    else:
                        print(f"Nenhum médico encontrado para a especialidade de {especialidade}.")
                        break
                    crm = input("Digite o CRM do Médico Desejado:")
                    dia_consulta = input("Digite o dia da consulta (AAAA-MM-DD): ")
                    horarios_disponiveis = db.mostrarConsultasDisponiveis(crm, dia_consulta)
                    if horarios_disponiveis:
                        print("Consultas disponíveis para o médico selecionado:")
                        for consulta in horarios_disponiveis:
                            print(f" {consulta[0]},  {consulta[1]},  {consulta[2]},  {consulta[3]}")
                    else:
                        print(f"Nenhuma consulta disponível para o médico com CRM {crm} no dia {dia_consulta}.")
                        break
                    horario = input("Digite o horário da consulta (HH:MM:SS): ")
                    p_cpf = formatar_cpf(input("Digite o CPF do paciente: "))
                    nome_dr = db.descobrirNome(crm)
                    db.marcarConsulta(nome_dr, dia_consulta, horario, p_cpf)
                elif x == "4":
                    # Gerenciamento de horários
                    print("=" * 50)
                    print("Gerenciamento de horários")
                    print("=" * 50)
                    print("Menu:\n"
                          "1. Disponibilizar horário\n"
                          "2. Indisponibilizar horário\n"
                          "3. Mostrar horários do médico\n"
                          "4. Voltar")
                    n = input("O que deseja fazer: ")
                    if n == "1":
                        # Disponibilizar horário
                        nome_dr = input("Digite o nome do médico: ")
                        data = input("Digite a data (AAAA-MM-DD): ")
                        horario = input("Digite o horário (HH:MM:SS): ")
                        db.disponibilizarHorario(nome_dr, data, horario)
                    elif n == "2":
                        # Indisponibilizar horário
                        nome_dr = input("Digite o nome do médico: ")
                        data = input("Digite a data (AAAA-MM-DD): ")
                        horario = input("Digite o horário (HH:MM:SS): ")
                        db.indisponibilizarHorario(nome_dr, data, horario)
                    elif n == "3":
                        # Mostrar horários do médico
                        nome_dr = input("Digite o nome do médico: ")
                        mostrar_horarios(nome_dr)
                    elif n == "4":
                        continue
                    else:
                        print("Opção inválida. Tente novamente.")
                elif x == "5":
                    # Gerar relatório
                    relatorio = Relatorio()
                    relatorio.imprimirRelatorio()
                elif x == "6":
                    # Consultar histórico médico
                    cpf = formatar_cpf(input("Insira o CPF: "))
                    historico = db.historicoMedico(cpf)
                    if historico is None:
                        print("Seu Histórico Médico está vazio.")
                    else:
                        print("Seu Histórico Médico:")
                        print(historico)
                elif x == "7":
                    # Atualizar cadastro
                    tipo_cadastro = input("Você é paciente ou médico? (P/M): ").upper()
                    if tipo_cadastro == "P":
                        cpf = formatar_cpf(input("Insira o CPF do paciente: "))
                        novo_nome = input("Novo nome: ")
                        novo_email = input("Novo email: ")
                        db.atualizarPaciente(cpf, novo_nome, novo_email)
                    elif tipo_cadastro == "M":
                        crm = input("Insira o CRM do médico: ")
                        novo_nome = input("Novo nome: ")
                        novo_email = input("Novo email: ")
                        db.atualizarMedico(crm, novo_nome, novo_email)
                    else:
                        print("Opção inválida.")
                elif x == "8":
                    # Sair
                    status = statusOff()
                    break
                else:
                    print("Opção inválida. Tente novamente.")
            except Exception as e:
                print(f"Erro: {e}")