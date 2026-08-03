# 1. Define a imagem base do sistema operacional (Python leve)
FROM python:3.11-slim

# 2. Define o diretório de trabalho dentro do container
WORKDIR /app

# 3. Copia o arquivo de dependências primeiro (otimiza o cache do Docker)
COPY requirements.txt .

# 4. Instala as bibliotecas necessárias
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia o restante do código e os dados para dentro do container
COPY src/ ./src/
COPY data/ ./data/

# 6. Libera a porta padrão do Streamlit para o mundo exterior
EXPOSE 8501

# 7. Comando definitivo para iniciar a aplicação
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]