import os
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    TextLoader,
    CSVLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

def carregar_e_processar_documentos(diretorio_data="../data"):
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
            
            # Passo 4: Atribuição de metadados
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
    # Testando o script isoladamente
    chunks_finais = carregar_e_processar_documentos(diretorio_data="data")
    
    if chunks_finais:
        print("\n--- Validação do Primeiro Chunk ---")
        print(f"METADADOS: {chunks_finais[0].metadata}")
        print(f"CONTEÚDO:\n{chunks_finais[0].page_content[:300]}...")