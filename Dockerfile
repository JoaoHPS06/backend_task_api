# 1. Imagem Base: Começamos com uma imagem oficial do Python
FROM python:3.11-slim

# 2. Diretório de Trabalho: Criamos uma pasta /app dentro do container
WORKDIR /app

# 3. Copiamos o arquivo de dependências
COPY requirements.txt .

# 4. Instalamos as dependências
RUN pip install -r requirements.txt

# 5. Copiamos o resto do código da nossa aplicação
COPY . .

# 6. Comando de Execução: O que o container vai rodar quando for iniciado
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]