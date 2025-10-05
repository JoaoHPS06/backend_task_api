import psycopg2
from flask import Flask, jsonify, request
from passlib.context import CryptContext
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity

# --- CONFIGURAÇÃO ---
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# --- CONFIGURAÇÃO DE SEGURANÇA ---
app.config["JWT_SECRET_KEY"] = "sua-chave-secreta-super-forte-mude-isso" # Mude esta chave!
jwt = JWTManager(app)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
DB_CONFIG = {
    "dbname": "db_tarefas",
    "user": "user_tarefas",
    "password": "pass_tarefas",
    "host": "pg-gerenciador-tarefas", 
    "port": "5432"
}

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

# --- ENDPOINTS DE AUTENTICAÇÃO ---

@app.route('/register', methods=['POST'])
def register():
    dados = request.get_json()
    if not dados or 'username' not in dados or 'password' not in dados:
        return jsonify({"msg": "Faltando username ou password"}), 400
    username = dados['username']
    password_hash = pwd_context.hash(dados['password'])
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO usuarios (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({"msg": "Usuário já existe"}), 400
    finally:
        cur.close()
        conn.close()
    return jsonify({"msg": "Usuário criado com sucesso"}), 201

@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    if not dados or 'username' not in dados or 'password' not in dados:
        return jsonify({"msg": "Faltando username ou password"}), 400
    username = dados['username']
    password = dados['password']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash FROM usuarios WHERE username = %s", (username,))
    user_data = cur.fetchone()
    cur.close()
    conn.close()
    if user_data and pwd_context.verify(password, user_data[1]):
        # Passamos o ID do usuário como a 'identity' para facilitar as buscas
        access_token = create_access_token(identity=str(user_data[0]))
        return jsonify(access_token=access_token)
    return jsonify({"msg": "Usuário ou senha inválidos"}), 401


# --- ROTAS DE TAREFAS (PROTEGIDAS) ---

@app.route('/tarefas', methods=['POST'])
@jwt_required()
def create_tarefa():
    usuario_id = get_jwt_identity() # Pega o ID do usuário direto do token
    dados = request.get_json()
    if not dados or 'descricao' not in dados or not dados['descricao'].strip():
        return jsonify({'erro': 'A "descricao" é obrigatória e não pode ser vazia'}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO tarefas (descricao, concluida, usuario_id) VALUES (%s, %s, %s) RETURNING id;',
        (dados['descricao'], False, usuario_id)
    )
    novo_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    nova_tarefa = {'id': novo_id, 'descricao': dados['descricao'], 'concluida': False}
    return jsonify(nova_tarefa), 201

@app.route('/tarefas', methods=['GET'])
@jwt_required()
def get_tarefas():
    usuario_id = get_jwt_identity()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, descricao, concluida FROM tarefas WHERE usuario_id = %s ORDER BY id;', (usuario_id,))
    tarefas_tuplas = cur.fetchall()
    cur.close()
    conn.close()
    tarefas = [{'id': t[0], 'descricao': t[1], 'concluida': t[2]} for t in tarefas_tuplas]
    return jsonify(tarefas)

# NOVA ROTA GET BY ID
@app.route('/tarefas/<int:tarefa_id>', methods=['GET'])
@jwt_required()
def get_tarefa_by_id(tarefa_id):
    usuario_id = get_jwt_identity()
    conn = get_db_connection()
    cur = conn.cursor()
    # A query agora busca pela tarefa E pelo dono
    cur.execute(
        "SELECT id, descricao, concluida FROM tarefas WHERE id = %s AND usuario_id = %s",
        (tarefa_id, usuario_id)
    )
    tarefa_tupla = cur.fetchone()
    cur.close()
    conn.close()
    if tarefa_tupla is None:
        # Não especificamos se a tarefa não existe ou se pertence a outro usuário
        # por questões de segurança. Apenas retornamos 404.
        return jsonify({'erro': 'Tarefa não encontrada'}), 404
    tarefa = {'id': tarefa_tupla[0], 'descricao': tarefa_tupla[1], 'concluida': tarefa_tupla[2]}
    return jsonify(tarefa)

# NOVA ROTA PUT
@app.route('/tarefas/<int:tarefa_id>', methods=['PUT'])
@jwt_required()
def update_tarefa(tarefa_id):
    usuario_id = get_jwt_identity()
    dados = request.get_json()
    if not dados or 'descricao' not in dados or 'concluida' not in dados:
        return jsonify({'erro': 'As chaves "descricao" e "concluida" são obrigatórias.'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    # O UPDATE também tem uma cláusula WHERE para o usuario_id, garantindo
    # que você só possa editar suas próprias tarefas.
    cur.execute(
        "UPDATE tarefas SET descricao = %s, concluida = %s WHERE id = %s AND usuario_id = %s",
        (dados['descricao'], dados['concluida'], tarefa_id, usuario_id)
    )
    conn.commit()
    linhas_afetadas = cur.rowcount
    cur.close()
    conn.close()

    if linhas_afetadas == 0:
        return jsonify({'erro': 'Tarefa não encontrada ou não autorizada'}), 404
        
    tarefa_atualizada = {'id': tarefa_id, 'descricao': dados['descricao'], 'concluida': dados['concluida']}
    return jsonify(tarefa_atualizada)


@app.route('/tarefas/<int:tarefa_id>', methods=['DELETE'])
@jwt_required()
def delete_tarefa(tarefa_id):
    usuario_id = get_jwt_identity()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tarefas WHERE id = %s AND usuario_id = %s", (tarefa_id, usuario_id))
    conn.commit()
    linhas_afetadas = cur.rowcount
    cur.close()
    conn.close()
    if linhas_afetadas == 0:
        return jsonify({'erro': 'Tarefa não encontrada ou não autorizada'}), 404
    return jsonify({'mensagem': 'Tarefa deletada com sucesso'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)