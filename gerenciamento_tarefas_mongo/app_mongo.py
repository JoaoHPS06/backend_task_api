# app_mongo.py

from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId # Essencial para converter strings para ObjectId
import bson.errors # Para tratar erros de ID inválido

# --- CONFIGURAÇÃO ---
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# --- CONFIGURAÇÃO DO MONGODB ---
client = MongoClient('mongodb://user_tarefas:pass_tarefas@localhost:27017/')
db = client.db_tarefas
tarefas_collection = db.tarefas

# --- ROTAS DA API (VERSÃO MONGODB) ---

# [READ] Obter todas as tarefas
@app.route('/tarefas', methods=['GET'])
def get_tarefas():
    todas_as_tarefas = list(tarefas_collection.find({}))
    for tarefa in todas_as_tarefas:
        tarefa['_id'] = str(tarefa['_id']) # Converte ObjectId para string
    return jsonify(todas_as_tarefas)

# [READ] Obter uma tarefa por ID
@app.route('/tarefas/<string:tarefa_id>', methods=['GET'])
def get_tarefa_by_id(tarefa_id):
    try:
        oid = ObjectId(tarefa_id)
    except bson.errors.InvalidId:
        return jsonify({'erro': 'ID de tarefa inválido'}), 400
        
    tarefa = tarefas_collection.find_one({'_id': oid})
    
    if tarefa is None:
        return jsonify({'erro': 'Tarefa não encontrada'}), 404
    
    tarefa['_id'] = str(tarefa['_id'])
    return jsonify(tarefa)

# [CREATE] Criar uma nova tarefa
@app.route('/tarefas', methods=['POST'])
def create_tarefa():
    dados = request.get_json()
    if not dados or 'descricao' not in dados or not dados['descricao'].strip():
        return jsonify({'erro': 'A chave "descricao" é obrigatória e não pode ser vazia.'}), 400

    nova_tarefa = {
        'descricao': dados['descricao'],
        'concluida': False  # Regra de negócio: sempre começa como não concluída
    }
    resultado = tarefas_collection.insert_one(nova_tarefa)

    # Pegamos o _id gerado e o retornamos na resposta
    id_inserido = str(resultado.inserted_id)
    tarefa_criada = tarefas_collection.find_one({'_id': ObjectId(id_inserido)})
    tarefa_criada['_id'] = str(tarefa_criada['_id'])

    return jsonify(tarefa_criada), 201

# [UPDATE] Atualizar uma tarefa
@app.route('/tarefas/<string:tarefa_id>', methods=['PUT'])
def update_tarefa(tarefa_id):
    try:
        oid = ObjectId(tarefa_id)
    except bson.errors.InvalidId:
        return jsonify({'erro': 'ID de tarefa inválido'}), 400

    dados = request.get_json()
    if not dados or 'descricao' not in dados or 'concluida' not in dados:
        return jsonify({'erro': 'As chaves "descricao" e "concluida" são obrigatórias.'}), 400

    resultado = tarefas_collection.update_one(
        {'_id': oid},
        {'$set': {
            'descricao': dados['descricao'],
            'concluida': dados['concluida']
        }}
    )

    if resultado.matched_count == 0:
        return jsonify({'erro': 'Tarefa não encontrada'}), 404

    tarefa_atualizada = tarefas_collection.find_one({'_id': oid})
    tarefa_atualizada['_id'] = str(tarefa_atualizada['_id'])
    return jsonify(tarefa_atualizada)

# [DELETE] Deletar uma tarefa
@app.route('/tarefas/<string:tarefa_id>', methods=['DELETE'])
def delete_tarefa(tarefa_id):
    try:
        oid = ObjectId(tarefa_id)
    except bson.errors.InvalidId:
        return jsonify({'erro': 'ID de tarefa inválido'}), 400

    resultado = tarefas_collection.delete_one({'_id': oid})

    if resultado.deleted_count == 0:
        return jsonify({'erro': 'Tarefa não encontrada'}), 404

    return jsonify({'mensagem': 'Tarefa deletada com sucesso'})


if __name__ == '__main__':
    app.run(debug=True, port=5001)
