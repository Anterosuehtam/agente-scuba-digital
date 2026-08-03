import streamlit as st
from agent import configurar_agente

# 1. Configuração da Página
st.set_page_config(page_title="Agente Snorkel", page_icon="🤿", layout="centered")

# Requisito A: Indicação clara de que é uma IA
st.title("🤿 Agente Snorkel")
st.caption("🤖 **Aviso:** Sou uma Inteligência Artificial desenvolvida para auxiliar os colaboradores do Scuba Digital. Minhas respostas são baseadas exclusivamente nos documentos normativos internos.")

# Inicializa o agente na sessão se não existir
if "agente" not in st.session_state:
    st.session_state.agente = configurar_agente()

# Requisito D: Histórico de conversa para contexto
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Como posso ajudar você com suas dúvidas operacionais hoje?", "sources": None}
    ]

# Barra Lateral (Menu de Controle)
with st.sidebar:
    st.header("⚙️ Controle da Sessão")
    if st.button("Nova Conversa", use_container_width=True):
        # Limpa o histórico para iniciar um novo contexto
        st.session_state.messages = [
            {"role": "assistant", "content": "Olá! Como posso ajudar você com suas dúvidas operacionais hoje?", "sources": None}
        ]
        st.rerun()
    
    st.divider()
    st.markdown("### 📊 Informações do Sistema")
    st.markdown("- **Motor LLM:** Cohere (command-a)")
    st.markdown("- **Recuperação:** ChromaDB (MMR)")
    st.markdown("- **Status:** Online")

# Renderiza o histórico de mensagens na tela
for i, msg in enumerate(st.session_state.messages):
    # Customiza os avatares para diferenciar máquina e humano
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])
        
        # Requisito B: Exibição elegante das fontes ocultas em um Expander
        if msg.get("sources"):
            with st.expander("🔍 Ver documentos consultados"):
                for fonte in msg["sources"]:
                    st.markdown(f"- `{fonte}`")
        
        # Requisito C: Botão de Feedback (Apenas para respostas da IA, ignorando a primeira saudação)
        if msg["role"] == "assistant" and i > 0:
            # O Streamlit possui um componente nativo de thumbs up/down
            st.feedback("thumbs", key=f"feedback_{i}")

# Caixa de entrada de texto
if prompt := st.chat_input("Digite sua dúvida operacional aqui..."):
    # Adiciona a pergunta do usuário no histórico e exibe
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Gera a resposta do agente
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Analisando a base de conhecimento corporativa..."):
            try:
                # Chama o nosso RAG (agora blindado com MMR e Temperatura 0)
                resposta_agente = st.session_state.agente.invoke({"input": prompt})
                texto_resposta = resposta_agente["answer"]
                
                # Extrai as fontes para exibir na UI
                fontes_unicas = []
                if "context" in resposta_agente:
                    # Usa um set para evitar nomes de arquivos duplicados caso o MMR traga múltiplos trechos do mesmo documento
                    fontes_unicas = list(set([doc.metadata.get("source", "Documento desconhecido") for doc in resposta_agente["context"]]))
                
                # Exibe a resposta
                st.markdown(texto_resposta)
                
                # Exibe o expander de fontes interativo
                if fontes_unicas:
                    with st.expander("🔍 Ver documentos consultados"):
                        for fonte in fontes_unicas:
                            st.markdown(f"- `{fonte}`")
                
                # Salva a resposta completa (com fontes) no histórico
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": texto_resposta,
                    "sources": fontes_unicas
                })
                
                # Força o recarregamento da tela para renderizar o botão de feedback na mensagem recém-criada
                st.rerun()
                
            except Exception as e:
                st.error(f"Erro de comunicação com o motor de IA: {e}")