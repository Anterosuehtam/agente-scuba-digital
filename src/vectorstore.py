import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from ingestion import carregar_e_processar_documentos

# Carrega as variáveis do arquivo .env (onde estará sua API Key)
load_dotenv()

def criar_banco_vetorial():
    print("1. Processando documentos da pasta data/...")
    
    chunks = carregar_e_processar_documentos(diretorio_data="data")
    
    if not chunks:
        print("Nenhum chunk retornado. Verifique a ingestão.")
        return None

    print(f"\n2. Inicializando modelo de Embeddings do Google...")
    # Modelo especializado do Google para transformar texto em vetor
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    print("3. Criando o banco vetorial Chroma e gerando coordenadas (isso pode levar alguns segundos)...")
    diretorio_db = "chroma_db"
    
    # Leitura dos chunks pelo Chroma, passa pelo modelo de embedding e salva no disco
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=diretorio_db
    )
    
    print(f"\n✅ Banco vetorial criado com sucesso! Dados salvos fisicamente na pasta '{diretorio_db}'.")
    return vectorstore

if __name__ == "__main__":
    criar_banco_vetorial()