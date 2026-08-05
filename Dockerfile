# 1. Usa uma imagem oficial do Python, versão leve (slim) para economizar espaço
FROM python:3.11-slim

# 2. Define a pasta principal dentro do "computador" do container
WORKDIR /app

# 3. Copia a "receita de bolo" primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# 4. Instala todas as bibliotecas (agora incluindo oci e boto3)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia o restante do seu código (pastas src, data, etc.)
COPY . .

# 6. Avisa o Docker que a porta 8501 será usada
EXPOSE 8501

# 7. O comando que liga o servidor, apontando para o app.py dentro de src/
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]