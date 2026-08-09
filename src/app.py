import streamlit as st
import json
import os
from agent import configurar_agente

# Arquivo que servirá como nosso "banco de dados" local de métricas
ARQUIVO_METRICAS = "feedbacks_log.json"

def salvar_feedback(pergunta, resposta, nota):
    """Salva a interação e a nota (1 para 👍, 0 para 👎) no arquivo JSON"""
    dado = {"pergunta": pergunta, "resposta": resposta, "nota": nota}
    try:
        if os.path.exists(ARQUIVO_METRICAS):
            with open(ARQUIVO_METRICAS, "r", encoding="utf-8") as f:
                logs = json.load(f)
        else:
            logs = []
            
        logs.append(dado)
        
        with open(ARQUIVO_METRICAS, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.sidebar.error(f"Erro ao salvar log: {e}")

def calcular_metricas():
    """Lê o arquivo JSON e retorna o total de avaliações e a taxa de aprovação"""
    if not os.path.exists(ARQUIVO_METRICAS):
        return 0, 0.0
    try:
        with open(ARQUIVO_METRICAS, "r", encoding="utf-8") as f:
            logs = json.load(f)
            total = len(logs)
            if total == 0: return 0, 0.0
            positivos = sum(1 for log in logs if log["nota"] == 1)
            taxa = (positivos / total) * 100
            return total, taxa
    except:
        return 0, 0.0

def obter_resposta_inteligente(rag_chain, mensagem_usuario):
    """
    Filtra saudações básicas antes de acionar o custo e o tempo do RAG.
    """
    saudacoes = ["olá", "ola", "oi", "tudo bem", "bom dia", "boa tarde", "boa noite", "oi snorkel", "olá snorkel"]
    mensagem_limpa = mensagem_usuario.lower().strip()
    
    # 1. Filtro Heurístico
    # Se a mensagem começar com uma saudação e for curta
    if any(mensagem_limpa.startswith(s) for s in saudacoes) and len(mensagem_limpa) < 30:
        return {
            "answer": "Olá! Estou aqui para ajudar. Como posso auxiliar com informações sobre os documentos internos do Scuba Digital?",
            "context": [] # Contexto vazio indica que não consultamos o banco
        }
    
    # 2. Execução Real do RAG (Acionado apenas para perguntas reais)
    return rag_chain.invoke({"input": mensagem_usuario})

# 1. Configuração da Página
st.set_page_config(page_title="Agente Snorkel", page_icon="🤿", layout="centered")
st.title("🤿 Agente Snorkel")
st.caption("🤖 **Aviso:** Sou uma Inteligência Artificial desenvolvida para auxiliar os colaboradores do Scuba Digital. Minhas respostas são baseadas exclusivamente nos documentos normativos internos.")

if "agente" not in st.session_state:
    st.session_state.agente = configurar_agente()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Como posso ajudar você com suas dúvidas operacionais hoje?", "sources": None, "feedback_registrado": True}
    ]

# Calcula as métricas antes de renderizar a barra lateral
total_feedbacks, taxa_aprovacao = calcular_metricas()

# Barra Lateral Corporativa
with st.sidebar:
    st.header("⚙️ Controle da Sessão")
    if st.button("Nova Conversa", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Olá! Como posso ajudar você com suas dúvidas operacionais hoje?", "sources": None, "feedback_registrado": True}
        ]
        st.rerun()
    
    st.divider()
    st.markdown("### 📈 Métricas de Aceitação")
    col1, col2 = st.columns(2)
    col1.metric("Avaliações", total_feedbacks)
    col2.metric("Aprovação", f"{taxa_aprovacao:.1f}%")
    
    st.divider()
    st.markdown("### 📊 Infraestrutura")
    st.markdown("- **Motor LLM:** Cohere (command-a)")
    st.markdown("- **Banco Vetorial:** ChromaDB")

# Renderiza o histórico
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])
        
        if msg.get("sources"):
            with st.expander("🔍 Ver documentos consultados"):
                for fonte in msg["sources"]:
                    st.markdown(f"- `{fonte}`")
        
        # Exibe o botão de feedback apenas para mensagens da IA (excluindo a saudação inicial)
        # e garante que o usuário só possa avaliar uma vez por resposta
        if msg["role"] == "assistant" and i > 0 and not msg.get("feedback_registrado", False):
            feedback = st.feedback("thumbs", key=f"feedback_{i}")
            
            if feedback is not None:
                # O Streamlit retorna 1 para polegar para cima e 0 para baixo
                pergunta_associada = st.session_state.messages[i-1]["content"]
                salvar_feedback(pergunta_associada, msg["content"], feedback)
                
                # Marca no histórico que essa mensagem já foi avaliada para não salvar duplicado no JSON
                st.session_state.messages[i]["feedback_registrado"] = True
                
                # Recarrega a tela para atualizar o painel de métricas na barra lateral
                st.rerun()

# Processamento de nova entrada
if prompt := st.chat_input("Digite sua dúvida operacional aqui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Analisando a base de conhecimento corporativa..."):
            try:
                resposta_agente = obter_resposta_inteligente(st.session_state.agente, prompt)
                
                texto_resposta = resposta_agente["answer"]

                # Conserta o bug do cifrão/LaTeX do Streamlit
                texto_resposta = texto_resposta.replace("$", "\\$")
                
                fontes_unicas = []
                if "context" in resposta_agente:
                    for doc in resposta_agente["context"]:
                        # Pega o caminho bruto salvo no banco
                        caminho_bruto = doc.metadata.get("source", "Documento desconhecido")
                        
                        # Converte barras do Windows para Linux e extrai só o nome do arquivo
                        nome_limpo = os.path.basename(caminho_bruto.replace("\\", "/"))
                        fontes_unicas.append(nome_limpo)
                    
                    # Remove duplicatas
                    fontes_unicas = list(set(fontes_unicas))
                
                st.markdown(texto_resposta)
                
                if fontes_unicas:
                    with st.expander("🔍 Ver documentos consultados"):
                        for fonte in fontes_unicas:
                            st.markdown(f"- `{fonte}`")
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": texto_resposta,
                    "sources": fontes_unicas,
                    "feedback_registrado": False # Habilita o botão de feedback para a nova resposta
                })
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Erro de comunicação: {e}")