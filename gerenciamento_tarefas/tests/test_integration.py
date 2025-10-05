# tests/test_integration.py

import pytest
from app import app # Apenas importamos o app
import psycopg2

# Esta é a nossa função que sabe se conectar ao banco de TESTE.
def get_test_db_connection():
    conn = psycopg2.connect(
        dbname="db_tarefas_test",
        user="user_tarefas",
        password="pass_tarefas",
        host="localhost",
        port="5432"
    )
    # Autocommit é ótimo para testes, para garantir que cada ação seja independente.
    conn.autocommit = True
    return conn


@pytest.fixture
def client(mocker): # Note que agora pedimos a fixture 'mocker'
    """
    Fixture que prepara o ambiente para cada teste de integração.
    """
    # A MÁGICA ACONTECE AQUI:
    # Nós dizemos ao mocker: "Toda vez que o código DENTRO DE 'app.py'
    # chamar a função 'get_db_connection', em vez de executar a original,
    # execute a nossa função 'get_test_db_connection' no lugar."
    mocker.patch('app.get_db_connection', side_effect=get_test_db_connection)

    with app.test_client() as client:
        # Agora temos 100% de certeza que estamos limpando o banco de TESTE.
        conn = get_test_db_connection()
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE usuarios, tarefas RESTART IDENTITY CASCADE;")
        cur.close()
        conn.close()
        yield client

# O CORPO DO TESTE PERMANECE EXATAMENTE O MESMO, POIS A LÓGICA DELE JÁ ESTAVA CORRETA.
def test_full_user_and_task_lifecycle(client):
    """
    Testa o fluxo completo: registrar, logar, criar, ler e deletar tarefa.
    """
    # 1. Registrar um novo usuário
    register_resp = client.post('/register', json={'username': 'integration_user', 'password': 'password123'})
    assert register_resp.status_code == 201

    # 2. Fazer login para obter o token
    login_resp = client.post('/login', json={'username': 'integration_user', 'password': 'password123'})
    assert register_resp.status_code == 201 # Corrigido: deve ser 200 OK para login
    # CORREÇÃO: A linha acima estava com um bug de digitação meu, o login retorna 200, não 201
    assert login_resp.status_code == 200
    access_token = login_resp.json['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    # 3. Criar uma nova tarefa com o token
    task_desc = "Minha tarefa de integração"
    create_task_resp = client.post('/tarefas', json={'descricao': task_desc}, headers=headers)
    assert create_task_resp.status_code == 201
    assert create_task_resp.json['descricao'] == task_desc
    new_task_id = create_task_resp.json['id']

    # 4. Ler a tarefa específica para confirmar a criação
    get_task_resp = client.get(f'/tarefas/{new_task_id}', headers=headers)
    assert get_task_resp.status_code == 200
    assert get_task_resp.json['descricao'] == task_desc

    # 5. Deletar a tarefa
    delete_task_resp = client.delete(f'/tarefas/{new_task_id}', headers=headers)
    assert delete_task_resp.status_code == 200
    assert delete_task_resp.json['mensagem'] == 'Tarefa deletada com sucesso'

    # 6. Verificar se a tarefa foi realmente deletada
    get_deleted_task_resp = client.get(f'/tarefas/{new_task_id}', headers=headers)
    assert get_deleted_task_resp.status_code == 404