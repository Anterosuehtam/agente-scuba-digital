import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_cohere import CohereEmbeddings, ChatCohere
from langchain_classic.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate 

OCID_COHERE = "ocid1.vaultsecret.oc1.sa-saopaulo-1.amaaaaaapd6tuwyaihvn4bsux3pxlohsuv7ixj2a4n7nnbzswjzpwbvffoea"

def configurar_agente():
    print("🔍 Verificando credenciais de acesso para o Agente...")

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
            raise ValueError("❌ O cofre respondeu, mas o segredo veio vazio (None). Verifique se o OCID está correto.")

    print("🧠 Inicializando o motor do LangChain...")

    # Conecta ao banco vetorial
    embeddings = CohereEmbeddings(model="embed-multilingual-v3.0")
    vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 4, 
            "score_threshold": 0.4
        } 
    )
    
    # Configura o LLM da Cohere
    llm = ChatCohere(model="command-a-03-2025", temperature=0.0, k_max_tokens=512)
    
    # Contextualizador
    contextualize_q_system_prompt = (
        "Dado o histórico de conversa e a pergunta mais recente do usuário "
        "que pode fazer referência a um contexto anterior, formule uma pergunta isolada "
        "que possa ser entendida sem o histórico. NUNCA responda a pergunta, "
        "apenas reformule-a ou retorne-a como está se não precisar de alterações."
    )
    
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"), # Injeta as mensagens antigas aqui
        ("human", "{input}"),
    ])
    
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # Prompt Principal Atualizado 
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
    
    # O prompt final também ganha o espaço reservado para a memória
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    # 1. Cria um mini-template para forçar o LangChain a colar o nome do arquivo junto com o texto
    document_prompt = PromptTemplate(
        input_variables=["page_content", "source"],
        template="[Nome do Arquivo: {source}]\nConteúdo: {page_content}"
    )
    
    # 2. Passa esse template para dentro da corrente
    question_answer_chain = create_stuff_documents_chain(
        llm=llm, 
        prompt=qa_prompt,
        document_prompt=document_prompt
    )
    
    # Une o reescritor (que busca no banco) com o respondedor final
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    return rag_chain