import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_cohere import CohereEmbeddings
from ingestion import carregar_e_processar_documentos

load_dotenv()

def criar_banco_vetorial():
    print("Iniciando carregamento de documentos...")
    
    diretorio_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho_data = os.path.join(diretorio_raiz, "data")
    
    documentos = carregar_e_processar_documentos(caminho_data)
    
    print("Gerando vetores com Cohere (embed-multilingual-v3.0)...")
    embeddings = CohereEmbeddings(model="embed-multilingual-v3.0")
    
    print("Salvando no ChromaDB...")
    vectorstore = Chroma.from_documents(
        documents=documentos,
        embedding=embeddings,
        persist_directory="chroma_db"
    )
    print("Banco vetorial criado com sucesso!")

if __name__ == "__main__":
    criar_banco_vetorial()