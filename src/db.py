import sqlite3
import uuid
from datetime import datetime
import os

# Define o caminho do banco de dados (ficará na mesma pasta do ChromaDB no servidor)
DB_PATH = "historico.db"

def obter_conexao():
    """Cria e retorna uma conexão com o banco SQLite."""
    # check_same_thread=False permite que o Streamlit acesse o banco em múltiplas threads
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def inicializar_banco():
    """Cria as tabelas de sessões e mensagens caso não existam."""
    conexao = obter_conexao()
    cursor = conexao.cursor()
    
    # Tabela de Sessões (Os "Chats" individuais)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessoes (
            id TEXT PRIMARY KEY,
            titulo TEXT,
            data_criacao DATETIME
        )
    """)
    
    # Tabela de Mensagens vinculadas às sessões
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sessao_id TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME,
            FOREIGN KEY (sessao_id) REFERENCES sessoes (id) ON DELETE CASCADE
        )
    """)
    
    conexao.commit()
    conexao.close()

def criar_sessao(titulo="Nova Conversa"):
    """Cria uma nova sessão e retorna o ID gerado."""
    sessao_id = str(uuid.uuid4())
    conexao = obter_conexao()
    cursor = conexao.cursor()
    
    cursor.execute(
        "INSERT INTO sessoes (id, titulo, data_criacao) VALUES (?, ?, ?)",
        (sessao_id, titulo, datetime.now())
    )
    
    conexao.commit()
    conexao.close()
    return sessao_id

def listar_sessoes():
    """Retorna todas as sessões ordenadas da mais recente para a mais antiga."""
    conexao = obter_conexao()
    cursor = conexao.cursor()
    
    cursor.execute("SELECT id, titulo, data_criacao FROM sessoes ORDER BY data_criacao DESC")
    sessoes = cursor.fetchall()
    conexao.close()
    
    # Formata a saída em uma lista de dicionários para facilitar o uso no Streamlit
    return [{"id": s[0], "titulo": s[1], "data_criacao": s[2]} for s in sessoes]

def salvar_mensagem(sessao_id, role, content):
    """Salva uma mensagem (do usuário ou da IA) em uma sessão específica."""
    conexao = obter_conexao()
    cursor = conexao.cursor()
    
    cursor.execute(
        "INSERT INTO mensagens (sessao_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (sessao_id, role, content, datetime.now())
    )
    
    conexao.commit()
    conexao.close()

def carregar_mensagens(sessao_id):
    """Carrega todo o histórico de mensagens de uma sessão específica."""
    conexao = obter_conexao()
    cursor = conexao.cursor()
    
    cursor.execute(
        "SELECT role, content FROM mensagens WHERE sessao_id = ? ORDER BY timestamp ASC",
        (sessao_id,)
    )
    mensagens = cursor.fetchall()
    conexao.close()
    
    return [{"role": m[0], "content": m[1]} for m in mensagens]

def deletar_sessao(sessao_id):
    """Exclui uma sessão e todas as suas mensagens (ON DELETE CASCADE)."""
    conexao = obter_conexao()
    cursor = conexao.cursor()
    
    # A exclusão em cascata garante que as mensagens também sumam
    cursor.execute("DELETE FROM sessoes WHERE id = ?", (sessao_id,))
    
    conexao.commit()
    conexao.close()

# Executa a criação das tabelas automaticamente ao importar o arquivo
inicializar_banco()