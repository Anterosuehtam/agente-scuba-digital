import streamlit as st
import json
import os
import db
from agent import configurar_agente
from langchain_core.messages import HumanMessage, AIMessage

# Arquivo que servirá como nosso "banco de dados" local de métricas
ARQUIVO_METRICAS = "feedbacks_log.json"

def salvar_feedback(pergunta, resposta, nota, motivo="", sessao_id=None, msg_index=None):
    dado = {
        "pergunta": pergunta, 
        "resposta": resposta, 
        "nota": nota, 
        "motivo": motivo,
        "sessao_id": sessao_id,
        "msg_index": msg_index
    }
    try:
        logs = []
        if os.path.exists(ARQUIVO_METRICAS) and os.path.getsize(ARQUIVO_METRICAS) > 0:
            with open(ARQUIVO_METRICAS, "r", encoding="utf-8") as f:
                logs = json.load(f)
                
        logs.append(dado)
        
        with open(ARQUIVO_METRICAS, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.sidebar.error(f"Erro ao salvar log: {e}")

def calcular_metricas():
    # Retorna 0 se o arquivo não existir ou estiver vazio (0 bytes)
    if not os.path.exists(ARQUIVO_METRICAS) or os.path.getsize(ARQUIVO_METRICAS) == 0:
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

def obter_interacoes_avaliadas():
    # Retorna um conjunto (set) com a dupla (sessao_id, msg_index)
    avaliadas = set()
    if os.path.exists(ARQUIVO_METRICAS) and os.path.getsize(ARQUIVO_METRICAS) > 0:
        try:
            with open(ARQUIVO_METRICAS, "r", encoding="utf-8") as f:
                logs = json.load(f)
                for log in logs:
                    s_id = log.get("sessao_id")
                    m_idx = log.get("msg_index")
                    if s_id is not None and m_idx is not None:
                        avaliadas.add((s_id, m_idx))
        except:
            pass
    return avaliadas

def obter_resposta_inteligente(rag_chain, mensagem_usuario, historico_mensagens):
    """
    Agora a função recebe o histórico e formata para a memória do LangChain.
    """
    saudacoes = ["olá", "ola", "oi", "tudo bem", "bom dia", "boa tarde", "boa noite", "oi snorkel", "olá snorkel"]
    mensagem_limpa = mensagem_usuario.lower().strip()
    
    if any(mensagem_limpa.startswith(s) for s in saudacoes) and len(mensagem_limpa) < 30:
        return {
            "answer": "Olá! Estou aqui para ajudar. Como posso auxiliar com informações sobre os documentos internos do Scuba Digital?",
            "context": []
        }
    
    # Converte as mensagens do SQLite para o formato de objetos que o LangChain exige
    chat_history = []
    for msg in historico_mensagens:
        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            chat_history.append(AIMessage(content=msg["content"]))
            
    # Execução Real do RAG enviando o histórico embutido
    return rag_chain.invoke({
        "input": mensagem_usuario,
        "chat_history": chat_history
    })

# 1. Configuração da Página
st.set_page_config(page_title="Agente Snorkel", page_icon="🤿", layout="centered")
st.title("🤿 Agente Snorkel")
st.caption("🤖 **Aviso:** Sou uma Inteligência Artificial desenvolvida para auxiliar os colaboradores do Scuba Digital. Minhas respostas são baseadas exclusivamente nos documentos normativos internos.")

if "agente" not in st.session_state:
    st.session_state.agente = configurar_agente()

# GERENCIAMENTO DE SESSÕES (CHATS)
sessoes_existentes = db.listar_sessoes()

# Se não houver nenhuma sessão ativa na memória, pega a última do banco ou cria uma nova
if "sessao_atual_id" not in st.session_state:
    if sessoes_existentes:
        st.session_state.sessao_atual_id = sessoes_existentes[0]["id"]
    else:
        st.session_state.sessao_atual_id = db.criar_sessao("Chat 1")

# Garante que as mensagens exibidas na tela pertençam à sessão correta
if "mensagens_tela" not in st.session_state or st.session_state.get("ultima_sessao_carregada") != st.session_state.sessao_atual_id:
    mensagens_banco = db.carregar_mensagens(st.session_state.sessao_atual_id)
    
    # Se a sessão for nova e estiver vazia, cria a saudação inicial e salva no banco
    if not mensagens_banco:
        saudacao = "Olá! Como posso ajudar você com suas dúvidas operacionais hoje?"
        db.salvar_mensagem(st.session_state.sessao_atual_id, "assistant", saudacao)
        mensagens_banco = [{"role": "assistant", "content": saudacao}]
        
    st.session_state.mensagens_tela = mensagens_banco
    st.session_state.ultima_sessao_carregada = st.session_state.sessao_atual_id
# --------------------------------------------------

total_feedbacks, taxa_aprovacao = calcular_metricas()

# 2. Barra Lateral
with st.sidebar:
    st.header("⚙️ Controle da Sessão")
    if st.button("Nova Conversa", use_container_width=True):
        # Conta a quantidade de chats para dar um nome sequencial (Ex: Chat 2, Chat 3)
        qtd_chats = len(db.listar_sessoes()) + 1
        novo_id = db.criar_sessao(f"Chat {qtd_chats}")
        st.session_state.sessao_atual_id = novo_id
        st.rerun()
        
    st.divider()
    st.markdown("### 🗂️ Histórico de Conversas")
    
    # Lista todos os chats salvos no SQLite como botões interativos
    for sessao in db.listar_sessoes():
        # Divide a barra em duas colunas: uma grande pro nome, uma pequena pra lixeira
        col1, col2 = st.columns([8, 2])
        
        with col1:
            if sessao["id"] == st.session_state.sessao_atual_id:
                st.button(f"👉 {sessao['titulo']}", key=f"btn_{sessao['id']}", use_container_width=True, disabled=True)
            else:
                if st.button(f"💬 {sessao['titulo']}", key=f"btn_{sessao['id']}", use_container_width=True):
                    st.session_state.sessao_atual_id = sessao["id"]
                    st.rerun()
                    
        with col2:
            # Botão de apagar
            if st.button("🗑️", key=f"del_{sessao['id']}", help="Apagar conversa"):
                db.deletar_sessao(sessao["id"])
                
                # Se apagou a sessão que estava aberta na tela, remove da memória para forçar a criação de uma nova
                if sessao["id"] == st.session_state.sessao_atual_id:
                    del st.session_state.sessao_atual_id
                    
                st.rerun()
                
    st.divider()
    st.markdown("### 📈 Métricas de Aceitação")
    col1, col2 = st.columns(2)
    col1.metric("Avaliações", total_feedbacks)
    col2.metric("Aprovação", f"{taxa_aprovacao:.1f}%")

# Carrega as avaliações do disco rígido uma única vez antes de montar o chat
interacoes_avaliadas = obter_interacoes_avaliadas()

# 3. Renderiza o histórico da tela
for i, msg in enumerate(st.session_state.mensagens_tela):
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])
        
        if msg.get("sources"):
            with st.expander("🔍 Ver documentos consultados"):
                for fonte in msg["sources"]:
                    st.markdown(f"- `{fonte}`")
                    
        # Identifica a pergunta exata que gerou esta resposta
        pergunta_associada = ""
        if msg["role"] == "assistant" and i > 0:
            pergunta_associada = st.session_state.mensagens_tela[i-1]["content"]
                    
        # A MÁGICA CORRIGIDA: Verifica se ESTA exata mensagem NESTE exato chat já foi avaliada
        ja_avaliada = msg.get("feedback_registrado", False) or (st.session_state.sessao_atual_id, i) in interacoes_avaliadas

        # Exibe os botões de feedback APENAS se a interação ainda não foi avaliada
        if msg["role"] == "assistant" and i > 0 and not ja_avaliada:
            
            # Divide o espaço para alinhar os botões customizados lado a lado
            col_like, col_deslike, col_vazia = st.columns([1, 1, 10])
            
            # Lógica do Like
            with col_like:
                # Mantemos o ID da sessão na chave para evitar conflitos de cache
                if st.button("👍", key=f"like_{st.session_state.sessao_atual_id}_{i}"):
                    # Salva nota 1, motivo vazio (""), e a "impressão digital" da mensagem
                    salvar_feedback(pergunta_associada, msg["content"], 1, "", st.session_state.sessao_atual_id, i)
                    st.session_state.mensagens_tela[i]["feedback_registrado"] = True
                    st.toast("Avaliação positiva registrada!")
                    st.rerun()
                    
            # Lógica do Deslike com a caixinha flutuante
            with col_deslike:
                with st.popover("👎"):
                    motivo = st.text_area("O que podemos melhorar nessa resposta?", key=f"txt_{st.session_state.sessao_atual_id}_{i}")
                    
                    if st.button("Enviar Feedback", key=f"btn_{st.session_state.sessao_atual_id}_{i}"):
                        salvar_feedback(pergunta_associada, msg["content"], 0, motivo)
                        st.session_state.mensagens_tela[i]["feedback_registrado"] = True
                        st.toast("Feedback enviado com sucesso!")
                        st.rerun()

# 4. Processamento de nova entrada
if prompt := st.chat_input("Digite sua dúvida operacional aqui..."):
    
    # Grava a pergunta do usuário no banco SQLite primeiro!
    db.salvar_mensagem(st.session_state.sessao_atual_id, "user", prompt)
    
    # Atualiza a tela
    nova_msg_user = {"role": "user", "content": prompt}
    st.session_state.mensagens_tela.append(nova_msg_user)
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Analisando a base de conhecimento corporativa..."):
            try:
                # Isola o histórico (sem a pergunta atual) para enviar à IA
                historico_para_ia = st.session_state.mensagens_tela[:-1]
                
                resposta_agente = obter_resposta_inteligente(st.session_state.agente, prompt, historico_para_ia)
                
                texto_resposta = resposta_agente["answer"]
                texto_resposta = texto_resposta.replace("$", "\\$")
                
                fontes_unicas = []
                if "context" in resposta_agente:
                    for doc in resposta_agente["context"]:
                        caminho_bruto = doc.metadata.get("source", "Documento desconhecido")
                        nome_limpo = os.path.basename(caminho_bruto.replace("\\", "/"))
                        fontes_unicas.append(nome_limpo)
                    fontes_unicas = list(set(fontes_unicas))
                
                st.markdown(texto_resposta)
                
                if fontes_unicas:
                    with st.expander("🔍 Ver documentos consultados"):
                        for fonte in fontes_unicas:
                            st.markdown(f"- `{fonte}`")
                
                # Grava a resposta gerada pela IA no banco SQLite
                db.salvar_mensagem(st.session_state.sessao_atual_id, "assistant", texto_resposta)
                
                st.session_state.mensagens_tela.append({
                    "role": "assistant", 
                    "content": texto_resposta,
                    "sources": fontes_unicas,
                    "feedback_registrado": False 
                })
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Erro de comunicação: {e}")