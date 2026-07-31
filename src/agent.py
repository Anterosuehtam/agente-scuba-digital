import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Carrega a API Key do arquivo .env
load_dotenv()

def configurar_agente():
    # 1. Conecta ao banco vetorial
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    
    # O "retriever" é o motor de busca. Serve para trazer os 3 chunks mais relevantes (k=3)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # 2. Configurando o LLM (O modelo que vai gerar o texto final)
    # Usando a temperatura 0.3 para respostas mais precisas e menos "criativas" (evita alucinações)
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.3)

    # 3. Cria o Prompt (As regras de comportamento do Snorkel)
    system_prompt = (
        "Você é o Snorkel, um agente de IA corporativo do banco Scuba Digital. "
        "Seu objetivo é responder a dúvidas dos colaboradores usando APENAS os documentos internos fornecidos. "
        "Se a resposta não estiver no contexto fornecido, diga 'Não possuo essa informação nos documentos atuais'. "
        "Nunca invente regras, tarifas ou prazos. Seja profissional e direto.\n\n"
        "Contexto recuperado dos documentos:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # 4. Une tudo na arquitetura RAG
    # create_stuff_documents_chain injeta os chunks no {context} do prompt
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    # create_retrieval_chain conecta o buscador (Chroma) com o leitor (LLM)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    return rag_chain

if __name__ == "__main__":
    agente = configurar_agente()
    
    # Testando o agente no terminal
    print("--- Teste do Agente Snorkel ---\n")
    pergunta = "Qual o limite noturno do PIX para as contas Varejo e Plus?"
    print(f"Pergunta do colaborador: {pergunta}\n")
    print("Buscando e processando resposta...\n")
    
    resposta = agente.invoke({"input": pergunta})
    
    print(f"🤖 Snorkel: {resposta['answer']}")