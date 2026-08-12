import os
from dotenv import load_dotenv
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    TextLoader,
    CSVLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_cohere import CohereEmbeddings

OCID_COHERE = "ocid1.vaultsecret.oc1.sa-saopaulo-1.amaaaaaapd6tuwyaihvn4bsux3pxlohsuv7ixj2a4n7nnbzswjzpwbvffoea"

def carregar_e_processar_documentos(diretorio_data="data"):
    """
    Lê diferentes formatos de arquivos de um diretório e os divide em chunks.
    """
    documentos_brutos = []
    
    # Passo 1: Extração por formato
    print("Iniciando leitura dos arquivos...")
    for arquivo in os.listdir(diretorio_data):
        caminho_completo = os.path.join(diretorio_data, arquivo)
        
        try:
            if arquivo.endswith(".pdf"):
                loader = PyPDFLoader(caminho_completo)
                docs = loader.load()
            elif arquivo.endswith(".md"):
                loader = UnstructuredMarkdownLoader(caminho_completo)
                docs = loader.load()
            elif arquivo.endswith(".txt"):
                loader = TextLoader(caminho_completo, encoding="utf-8")
                docs = loader.load()
            elif arquivo.endswith(".csv"):
                # CSVLoader converte cada linha em um documento estruturado
                loader = CSVLoader(caminho_completo, encoding="utf-8")
                docs = loader.load()
            else:
                continue
            
            # Passo 2: Atribuição de metadados
            for doc in docs:
                doc.metadata["nome_arquivo"] = arquivo
                
            documentos_brutos.extend(docs)
            print(f"Lido com sucesso: {arquivo}")
            
        except Exception as e:
            print(f"Erro ao ler {arquivo}: {e}")

    print(f"\nTotal de páginas/linhas extraídas: {len(documentos_brutos)}")

    # Passo 3: Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documentos_brutos)
    print(f"Documentos divididos em {len(chunks)} chunks.")
    
    return chunks


if __name__ == "__main__":
    print("🔍 Verificando credenciais de acesso...")
    
    # Carrega as variáveis do arquivo .env local (se ele existir)
    load_dotenv()
    
    # Tenta resgatar a chave localmente
    chave_cohere = os.getenv("COHERE_API_KEY")
    
    if chave_cohere:
        print("✅ Chave do Cohere carregada localmente via arquivo .env!")
    else:
        print("☁️ Chave local não encontrada. Tentando resgatar do OCI Vault...")
        # Importamos o vault apenas se precisarmos dele, evitando crash no Windows
        from vault import resgatar_segredo
        chave_cohere = resgatar_segredo(OCID_COHERE)
        
        if chave_cohere:
            os.environ["COHERE_API_KEY"] = chave_cohere
            print("✅ Chave do Cohere carregada com sucesso do OCI Vault!")
        else:
            raise ValueError("❌ O cofre respondeu, mas o segredo veio vazio.")

    # Testando o script e processando os dados
    chunks_finais = carregar_e_processar_documentos(diretorio_data="data")
    
    if chunks_finais:
        print("\n--- Validação do Primeiro Chunk ---")
        print(f"METADADOS: {chunks_finais[0].metadata}")
        print(f"CONTEÚDO:\n{chunks_finais[0].page_content[:300]}...")
        
        print("\n💾 Gerando embeddings e salvando documentos no ChromaDB...")
        embeddings = CohereEmbeddings(model="embed-multilingual-v3.0")
        
        vectorstore = Chroma.from_documents(
            documents=chunks_finais,
            embedding=embeddings,
            persist_directory="chroma_db"
        )
        print("✅ Ingestão concluída com sucesso! Banco de dados populado.")