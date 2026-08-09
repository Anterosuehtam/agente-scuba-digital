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
        os.environ["COHERE_API_KEY"] = chave_cohere
    else:
        raise ValueError("❌ O cofre respondeu, mas o segredo veio vazio (None). Verifique se o OCID está correto.")

    print("🧠 Inicializando o motor do LangChain...")

    # Conecta ao banco vetorial com embeddings da Cohere
    embeddings = CohereEmbeddings(model="embed-multilingual-v3.0")
    vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 4, 
            "score_threshold": 0.5 # Apenas textos com pelo menos 50% de similaridade matemática passam
        } 
    )
    
    # Configura o LLM da Cohere (Command)
    llm = ChatCohere(model="command-a-03-2025", temperature=0.2, k_max_tokens=512)
    
    # Criação do Prompt e Correntes (RAG)
    system_prompt = (
        "Você é o Snorkel, um agente de IA corporativo do banco Scuba Digital. "
        "Seu objetivo é responder a dúvidas operacionais dos colaboradores usando APENAS os documentos internos fornecidos.\n\n"
        "Siga estas regras rigorosamente:\n"
        "1. Responda de forma clara, direta e profissional.\n"
        "2. CITAÇÃO OBRIGATÓRIA: Cite a fonte da informação utilizando o nome real do documento. NUNCA copie a marcação literal '[Nome do Arquivo]'. Substitua pelo nome verdadeiro que está nos metadados do contexto (Exemplo: 'De acordo com o documento faq_operacional.md...').\n"
        "3. Se a resposta recomendar contato com alguma área, forneça os e-mails e ramais APENAS se eles estiverem explicitamente descritos no contexto recuperado. Se não estiverem, informe apenas o nome da área e não invente contatos de forma alguma.\n"
        "4. FALLBACK: Se a resposta para a pergunta não estiver contida no contexto abaixo, não tente adivinhar. Você deve responder EXATAMENTE: 'Não encontrei essa informação nos documentos normativos disponíveis. Recomendo entrar em contato com a área responsável para obter esclarecimentos.' e parar de escrever.\n"
        "5. Nunca invente informações, dados ou regras.\n\n"
        "Contexto recuperado:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    return rag_chain