# 🏦 Scuba Digital - Agente RAG Corporativo (Snorkel)

## 📖 Descrição Geral
Bem-vindo ao repositório do **Snorkel**, o agente de Inteligência Artificial conversacional desenvolvido para atuar como a base de conhecimento interna do **Scuba Digital**. Utilizando a arquitetura RAG (Retrieval-Augmented Generation), o Snorkel responde a dúvidas de colaboradores com base em documentos institucionais de diferentes departamentos (RH, Financeiro, Operacional e TI), processando de forma inteligente múltiplos formatos de arquivos.

## 🏗️ Arquitetura da Solução
O sistema foi desenhado para extrair, vetorizar e recuperar informações de forma semântica antes de gerar a resposta ao usuário.
* **Processamento de Dados:** Leitura e *chunking* de arquivos heterogêneos (PDF, CSV, JSON, Markdown).
* **Indexação Vetorial:** Armazenamento de embeddings para busca por similaridade.
* **Orquestração (RAG):** Recuperação do contexto relevante acoplado ao *prompt* para mitigar alucinações.
* **Geração:** Resposta natural e precisa fundamentada exclusivamente nos documentos internos do Scuba Digital.

## 🛠️ Tecnologias e Ferramentas
* **Linguagem:** Python
* **Orquestração de IA:** LangChain
* **LLM:** Google Gemini
* **Manipulação de Dados:** Pandas
* **Infraestrutura e Deploy:** Oracle Cloud Infrastructure (OCI Compute)

## 🚀 Instruções de Execução
*(A ser preenchido quando finalizar o script de inicialização e o deploy na OCI)*
1. Clone o repositório: `git clone ...`
2. Instale as dependências: `pip install -r requirements.txt`
3. Configure as variáveis de ambiente (`.env`)
4. Execute a aplicação...

## 💡 Exemplos de Uso
*(A ser preenchido após a validação das respostas do agente)*
* **Pergunta:** ...
* **Resposta do Agente:** ...