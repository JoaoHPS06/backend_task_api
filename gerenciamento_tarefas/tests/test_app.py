# tests/test_app.py

import pytest
from app import app # Importa nossa aplicação Flask do arquivo app.py
import psycopg2 # Importamos para simular o erro específico do banco

# ----------------- CONFIGURAÇÃO DO AMBIENTE DE TESTE -----------------

@pytest.fixture
def client():
    """
    Esta é uma "fixture" do Pytest. Ela cria e configura um cliente de testes
    para nossa aplicação Flask antes de cada teste que a solicitar.
    """
    with app.test_client() as client:
        yield client

# ----------------- TESTES DA ROTA /register -----------------

def test_register_user_success(client, mocker):
    """
    Testa o caso de sucesso do cadastro de um novo usuário.
    'client' e 'mocker' são fixtures injetadas pelo Pytest.
    """
    # --- ARRANGE (Arrumar) ---
    # 1. Dados do novo usuário que vamos enviar na requisição
    new_user_data = {'username': 'testuser', 'password': 'password123'}

    # 2. Criando o "dublê" (Mock) do nosso banco de dados
    # mocker.patch diz: "Quando o código em 'app.py' tentar usar 'get_db_connection',
    # intercepte essa chamada e me dê o controle sobre ela."
    mock_conn = mocker.patch('app.get_db_connection')
    
    # Configuramos o mock para não fazer nada quando .commit() for chamado.
    # Isso evita erros, pois o mock não tem um método .commit() de verdade.
    mock_conn.return_value.cursor.return_value.commit = mocker.Mock()

    # --- ACT (Agir) ---
    # 3. Usamos o cliente de testes para fazer uma requisição POST para a rota
    response = client.post('/register', json=new_user_data)

    # --- ASSERT (Afirmar) ---
    # 4. Verificamos se a resposta é a que esperamos
    assert response.status_code == 201
    assert response.json['msg'] == 'Usuário criado com sucesso'


def test_register_existing_user_error(client, mocker):
    """
    Testa o caso de erro onde o usuário a ser cadastrado já existe.
    """
    # --- ARRANGE ---
    existing_user_data = {'username': 'joao', 'password': 'senha123'}
    
    # 1. Configuramos o mock do banco de dados para simular um erro.
    # Quando o método .execute() do cursor for chamado, ele deve levantar
    # um psycopg2.IntegrityError, que é o que aconteceria de verdade se
    # tentássemos inserir um username que já existe.
    mock_conn = mocker.patch('app.get_db_connection')
    mock_cursor = mock_conn.return_value.cursor.return_value
    mock_cursor.execute.side_effect = psycopg2.IntegrityError("Username já existe")

    # --- ACT ---
    # 2. Fazemos a requisição que esperamos que falhe
    response = client.post('/register', json=existing_user_data)

    # --- ASSERT ---
    # 3. Verificamos se a API lidou com o erro corretamente
    assert response.status_code == 400
    assert response.json['msg'] == 'Usuário já existe'