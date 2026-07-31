import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_cohere import CohereEmbeddings, ChatCohere
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

def configurar_agente():
    # 1. Conecta ao banco vetorial com embeddings da Cohere
    embeddings = CohereEmbeddings(model="embed-multilingual-v3.0")
    vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    # 2. Configura o LLM da Cohere (Command)
    llm = ChatCohere(model="command-a-03-2025", temperature=0.3)
    
    # 3. Criação do Prompt e Correntes (RAG)
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
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    return rag_chain