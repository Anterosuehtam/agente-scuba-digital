import streamlit as st
from agent import configurar_agente

# 1. Configuração visual da página
st.set_page_config(page_title="Snorkel - Scuba Digital", page_icon="🤿")
st.title("🤿 Agente Snorkel")
st.markdown("Assistente interno para colaboradores do Banco Scuba Digital.")

# 2. Inicialização (Executa apenas uma vez)
if "agente" not in st.session_state:
    with st.spinner("Iniciando conexão segura com a base de conhecimento..."):
        st.session_state.agente = configurar_agente()

# 3. Gerenciamento do histórico de conversa
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# Renderiza mensagens anteriores na tela
for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. Caixa de texto para o colaborador interagir
if prompt := st.chat_input("Qual é a sua dúvida operacional?"):
    
    # Processa e exibe a resposta do Snorkel
    with st.chat_message("assistant"):
        with st.spinner("Consultando normativas..."):
            # A invocação traz a resposta e o contexto (os chunks recuperados)
            resposta = st.session_state.agente.invoke({"input": prompt})
            texto_resposta = resposta["answer"]
            documentos = resposta.get("context", [])
            
            # 1. Imprime a resposta do LLM
            st.markdown(texto_resposta)
            
            # 2. Extrai e imprime as Fontes Consultadas
            if documentos:
                st.markdown("---")
                st.markdown("**🔍 Fontes consultadas:**")
                fontes_unicas = set()
                
                # Coleta as fontes evitando repetições (usando set)
                for doc in documentos:
                    # O metadado 'source' guarda o caminho do arquivo original
                    fonte = doc.metadata.get("source", "Documento interno")
                    fontes_unicas.add(fonte)
                
                # Renderiza cada fonte na tela em formato de legenda (menor)
                for f in fontes_unicas:
                    st.caption(f"- {f}")
            
    # Salva a resposta no histórico da tela
    st.session_state.mensagens.append({"role": "assistant", "content": texto_resposta})