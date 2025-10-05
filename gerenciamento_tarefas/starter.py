# Gerenciador de Tarefas Simples
tarefas = [{"id" : 1, "descricao": "Estudar Python", "concluida": False}, 
           {"id" : 2, "descricao": "Ler um livro", "concluida": True},
           {"id" : 3, "descricao": "Fazer exercícios", "concluida": False} 
]

# Função para adicionar uma nova tarefa
def adicionar_tarefa(descricao):
    id_nova = len(tarefas) + 1
    nova_tarefa = {"id": id_nova, "descricao": descricao, "concluida": False}
    tarefas.append(nova_tarefa)

# Função para listar todas as tarefas com seu status
# Exemplo de saída: [ ] Tarefa 1: Estudar Python (se "concluida" for False)
# Exemplo de saída: [X] Tarefa 2: Criar projeto inicial (se "concluida" for True)
def listar_tarefas():
    for tarefa in tarefas:
        status = "[X]" if tarefa["concluida"] else "[ ]"
        print(f"{status} Tarefa {tarefa['id']}: {tarefa['descricao']}")

# Função para marcar uma tarefa como concluída
def concluir_tarefa(id):
    for tarefa in tarefas:
        if tarefa["id"] == id:
            tarefa["concluida"] = True
            return
    print("Tarefa não encontrada.")

adicionar_tarefa("Ir ao supermercado")
listar_tarefas()
concluir_tarefa(1)
print("\nApós concluir a tarefa 1:\n")
listar_tarefas()