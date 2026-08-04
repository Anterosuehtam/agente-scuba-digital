import os
from vault import resgatar_segredo
from langchain_community.vectorstores import Chroma
from langchain_cohere import CohereEmbeddings, ChatCohere
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

OCID_COHERE = "ocid1.vaultsecret.oc1.sa-saopaulo-1.amaaaaaapd6tuwyaihvn4bsux3pxlohsuv7ixj2a4n7nnbzswjzpwbvffoea"

def configurar_agente():
    print("🔐 Resgatando chave da LLM no OCI Vault...")
    chave_cohere = resgatar_segredo(OCID_COHERE)

    if chave_cohere:
        # Injeta a chave na memória do sistema durante a execução
        os.environ["COHERE_API_KEY"] = chave_cohere
    else:
        # Se falhar, o sistema avisa e encerra para não dar erro genérico depois
        raise ValueError("❌ Erro fatal: Não foi possível acessar a chave da Cohere no cofre.")

    print("🧠 Inicializando o motor do LangChain...")

    # Conecta ao banco vetorial com embeddings da Cohere
    embeddings = CohereEmbeddings(model="embed-multilingual-v3.0")
    vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 8, "fetch_k": 40}
    )
    
    # Configura o LLM da Cohere (Command)
    llm = ChatCohere(model="command-a-03-2025", temperature=0.0, k_max_tokens=512)
    
    # Criação do Prompt e Correntes (RAG)
    system_prompt = (
        "Você é o Snorkel, um agente de IA corporativo do banco Scuba Digital. "
        "Seu objetivo é responder a dúvidas dos colaboradores usando APENAS os documentos internos fornecidos. "
        "Siga estas regras rigorosamente:\n"
        "1. Responda de forma direta e profissional.\n"
        "2. Se a resposta exigir contato com alguma área (RH, TI, Jurídico), extraia e exiba os e-mails e ramais exatos do documento.\n"
        "3. Para perguntas fora do escopo bancário ou que não estão nos documentos (ex: receitas, curiosidades, etc), você deve responder EXATAMENTE com a frase: 'Não possuo essa informação nos documentos atuais.' e parar de escrever.\n"
        "4. Nunca invente informações, dados ou regras.\n\n"
        "Contexto recuperado:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    return rag_chain