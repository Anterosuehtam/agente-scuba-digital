# Manual Operacional e FAQ - Scuba Digital
**Versão do Documento:** 2.1.0 (Edição de Operações e Atendimento)
**Última Atualização:** Maio de 2026
**Departamento:** Suporte Operacional / Prevenção a Fraudes

---

## 1. Diretrizes de Atendimento e SLA
Este documento estabelece os procedimentos operacionais padrão (POP) para a resolução de chamados de clientes do Scuba Digital. O objetivo é garantir que o agente de suporte forneça informações precisas, amparadas pelas políticas do Banco Central do Brasil (Bacen) e pelas regras de negócio internas da instituição.

* **Tempo Médio de Resposta (TMR) Nível 1:** Até 3 minutos via chat.
* **Tempo de Resolução (SLA) Nível 2 (Análise de Risco):** Até 48 horas úteis.

---

## 2. Transações e Limites de PIX

### 2.1 Como funciona a regra do limite noturno para transferências via PIX?
Por determinação de segurança do Banco Central (Resolução BCB nº 142), o limite de transferências via PIX realizadas no período noturno (entre 20h00 e 06h00) é restrito a R$ 1.000,00 para todas as contas Pessoa Física (Varejo e Plus). 
* **Exceção:** Contas Pessoa Jurídica (Scuba PJ) possuem um limite noturno flexível, pré-aprovado mediante análise de faturamento dos últimos 90 dias e solicitação via painel web.

### 2.2 O cliente pode solicitar o aumento ou redução do limite noturno?
Sim. A gestão de limites é feita diretamente pelo aplicativo, na seção "Segurança > Meus Limites".
* **Redução de limite:** Aplicada imediatamente no sistema, refletindo na mesma hora.
* **Aumento de limite:** Por questões de prevenção a fraudes e engenharia social, a efetivação do novo limite leva um prazo obrigatório de 24 horas a 48 horas para ser aprovada pelo motor de risco. O suporte não possui permissão de sistema (bypass) para acelerar este prazo.

### 2.3 O que é o erro "Falha de Comunicação DICT" durante um PIX?
O DICT (Diretório de Identificadores de Contas Transacionais) é o sistema do Banco Central que armazena as chaves PIX. Quando ocorre o erro de timeout (código HTTP 504 no nosso backend), significa que o Scuba Digital não conseguiu consultar a chave do recebedor no Bacen. O atendente deve orientar o cliente a aguardar 15 minutos e tentar novamente, ou realizar a transferência utilizando os dados de agência e conta, contornando a consulta ao DICT.

---

## 3. Cartões de Crédito, Débito e Chargeback

### 3.1 Qual o prazo para que um estorno de compra cancelada reflita na fatura?
Quando um estabelecimento comercial confirma o cancelamento de uma compra, o prazo para que o estorno seja processado pela adquirente (maquininha), repassado à bandeira (Mastercard) e reflita na fatura do cliente é de 1 a 2 faturas subsequentes (média de 30 a 60 dias).
* **Fatura Aberta:** O crédito entra abatendo o valor total.
* **Fatura Fechada:** O crédito entrará obrigatoriamente como saldo positivo no mês seguinte. O suporte não pode antecipar estornos não processados pela bandeira.

### 3.2 O que fazer quando a compra é negada por "Suspeita de Fraude" (Código 59)?
O Código 59 indica que o nosso motor de risco (Scuba Shield) bloqueou a transação preventiva e temporariamente devido a um desvio no padrão de consumo do cliente (ex: compra de alto valor de madrugada em loja de eletrônicos internacional). 
* **Ação:** O cliente receberá um push no aplicativo solicitando reconhecimento facial (liveness check) para confirmar a tentativa de compra. Caso confirme, o cartão é desbloqueado automaticamente em até 5 minutos.

### 3.3 Como funciona o processo de Contestação de Compra (Chargeback)?
Se o cliente relatar fraude (não reconhece a compra) ou desacordo comercial (comprou, mas a loja não entregou), o atendente deve iniciar a disputa via portal de backoffice.
* **Prazo para abertura:** Até 90 dias após a data da compra.
* **Crédito de Confiança:** Em casos de suspeita de fraude onde o cliente tenha boletim de ocorrência, o Scuba Digital disponibiliza o "Crédito de Confiança" na fatura em até 3 dias úteis, enquanto a análise com a bandeira está em andamento.

---

## 4. Conta Rendimento e Impostos

### 4.1 Como funciona o rendimento automático da conta Scuba?
O saldo disponível na conta rende 100% do CDI automaticamente todos os dias úteis, desde que o valor permaneça na conta por um período superior a 30 dias (regra da poupança/RDB). Se o dinheiro for movimentado antes de 30 dias, o IOF (Imposto sobre Operações Financeiras) consome 100% da rentabilidade, zerando o ganho.

### 4.2 Quais impostos incidem sobre o rendimento?
* **IOF:** Incide apenas nos primeiros 29 dias (começa em 96% e zera no 30º dia).
* **Imposto de Renda (IR):** É retido na fonte, de forma regressiva, apenas sobre o lucro. Começa em 22,5% (até 180 dias) e cai até 15% (acima de 720 dias). O informe de rendimentos para declaração fica disponível todo mês de fevereiro no app.

---

## 5. Bloqueios e Segurança de Conta

### 5.1 O que é o "Bloqueio Cautelar" e quanto tempo ele dura?
Mecanismo de segurança acionado quando o banco identifica uma transação recebida (entrada via PIX) com indícios de fraude. O valor fica retido por até 72 horas. Se a transação for legítima, o saldo é liberado. Se for confirmada a fraude, o valor é devolvido ao banco de origem via MED (Mecanismo Especial de Devolução).

### 5.2 Quais são os passos iniciais caso o cliente relate perda ou roubo do celular?
O atendente Nível 1 deve executar imediatamente os seguintes comandos no terminal de segurança:
1. `Desconexão Global de Sessões` (derruba o token JWT do app).
2. `Bloqueio Temporário (BlockCode 41)` nos cartões físicos e virtuais.
3. Orientar o cliente a acessar o site do Scuba Digital pelo computador para acompanhar o status e instruí-lo a usar recursos remotos (Find My iPhone / Encontre meu Dispositivo Google) para apagar os dados do aparelho.

### 5.3 O que é o Modo Rua?
Uma funcionalidade ativada pelo cliente que restringe os limites de PIX, pagamentos e investimentos a R$ 200,00 sempre que o celular estiver desconectado de redes Wi-Fi confiáveis (como a da casa do cliente). É a principal defesa do banco contra furtos de dispositivos desbloqueados.