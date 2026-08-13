# 🤿 Scuba Digital - Agente RAG Corporativo (Snorkel)

## 🎥 Demonstração em Produção

https://github.com/user-attachments/assets/463170c8-22d7-4dcb-a2c7-e1a7fe84d2ed

📺 **Prefere assistir com mais detalhes e em velocidade normal?** [Confira o vídeo completo no YouTube](https://youtu.be/k1MS9gGvWyU)

## ▶️ Teste ao Vivo

A aplicação está hospedada e rodando em produção na nuvem (Oracle Cloud Infrastructure). 
**[👉 Clique aqui para conversar com o Agente Snorkel](http://136.248.107.155:8501/)**

## 📖 Descrição Geral
Bem-vindo ao repositório do **Snorkel**, o agente de Inteligência Artificial conversacional desenvolvido para atuar como a base de conhecimento interna do **Scuba Digital**. Utilizando a arquitetura RAG (Retrieval-Augmented Generation), o Snorkel responde a dúvidas de colaboradores com base em documentos institucionais de diferentes departamentos (RH, Financeiro, Operacional e TI), processando de forma inteligente múltiplos formatos de arquivos.

## 🏗️ Arquitetura da Solução
O sistema foi desenhado para extrair, vetorizar e recuperar informações de forma semântica antes de gerar a resposta ao usuário.
* **Processamento de Dados:** Leitura e *chunking* de arquivos heterogêneos (PDF, CSV, JSON, Markdown).
* **Indexação Vetorial:** Armazenamento de embeddings no ChromaDB para busca por similaridade.
* **Orquestração (RAG):** Recuperação do contexto relevante acoplado ao *prompt* para mitigar alucinações e injeção de metadados nas respostas.
* **Geração e Memória:** Respostas naturais fundamentadas exclusivamente nos documentos internos, com suporte a histórico relacional (memória de curto prazo) e telemetria de avaliações.

## 🛠️ Tecnologias e Ferramentas
* **Linguagem:** Python
* **Interface e Front-end:** Streamlit
* **Orquestração de IA:** LangChain
* **LLM:** Cohere
* **Banco de Dados:** SQLite (Gestão de Sessões) e JSON (Métricas de Aceitação)
* **Infraestrutura e Deploy:** Docker, CI/CD (GitHub Actions) e Oracle Cloud Infrastructure (OCI Compute)

## 🚀 Instruções de Execução
A aplicação foi empacotada em contêineres para facilitar a reprodução do ambiente.

1. Clone o repositório: 
   ```bash
   git clone https://github.com/seu-usuario/agente-scuba-digital.git
   ```
2. Baixe a imagem atualizada: 
   ```bash
   docker pull seu-usuario/agente-snorkel:latest
   ```
3. Execute a aplicação mapeando os volumes de dados e métricas:
   ```bash
   docker run -d --name agente-snorkel -p 8501:8501 \
     -v ~/chroma_db:/app/chroma_db \
     -v ~/feedbacks_log.json:/app/feedbacks_log.json \
     -v ~/historico.db:/app/historico.db \
     seu-usuario/agente-snorkel:latest
   ```
4. Acesse no navegador via `http://localhost:8501` ou pelo IP do seu servidor.

## 💡 Exemplos de Uso

Abaixo estão interações reais que demonstram a capacidade do agente de cruzar informações, manter o contexto da conversa e recusar tópicos fora do escopo:

**Exemplo 1: Regras Operacionais e Retenção de Contexto**
> **👤 Usuário:** Como funciona o limite de PIX noturno para conta PJ?
> **🤖 Snorkel:** De acordo com o documento `faq_operacional.md`, o limite de transferências via PIX no período noturno (entre 20h00 e 06h00) para contas Pessoa Jurídica (Scuba PJ) é flexível. Ele é pré-aprovado mediante análise de faturamento dos últimos 90 dias e solicitação via painel web.
> 
> **👤 Usuário:** E se o valor for de 10 mil reais? *(Avaliando a memória da IA)*
> **🤖 Snorkel:** O limite noturno é flexível e depende da análise prévia. Portanto, se o valor de R$ 10.000,00 estiver dentro do limite pré-aprovado para a conta em questão, a transação poderá ser realizada. Caso contrário, será retida.

**Exemplo 2: Interpretação de Políticas de Segurança**
> **👤 Usuário:** O que acontece se houver múltiplas tentativas de senha (PIN) inválidas?
> **🤖 Snorkel:** De acordo com o documento `politica_seguranca_fraudes.pdf`, o sistema aplicará um **Bloqueio de segurança da conta**. O procedimento para desbloqueio exige o envio de um link seguro via e-mail corporativo cadastrado. Além disso, os atendentes são proibidos de solicitar senhas de acesso.

**Exemplo 3: Tratamento de Fora de Escopo (Fallback)**
> **👤 Usuário:** Me passe uma receita de bolo de cenoura.
> **🤖 Snorkel:** Desculpe, mas sou uma inteligência artificial desenvolvida exclusivamente para auxiliar com os documentos normativos e operacionais internos do Scuba Digital. Não encontrei nenhuma informação sobre receitas em nossa base de dados. Como posso ajudar com as suas dúvidas operacionais hoje?
