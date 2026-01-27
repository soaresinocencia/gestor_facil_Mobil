# Checklist de Testes com Clientes (Piloto)

Antes de entregar ou demonstrar o sistema ao cliente, execute este roteiro para garantir que tudo corre bem.

## 1. Preparação (Antes de ir ao Cliente)

- [ ] **Limpeza de Dados**: Deseja apagar as vendas de teste? (Se sim, delete o arquivo `gestao_comercial.db` para começar do zero, ou use um script de limpeza).
- [ ] **Backup**: Copie a pasta do projeto para um Pen Drive ou Cloud como segurança.
- [ ] **Equipamento**: O computador do cliente tem Python instalado? Ou você vai levar o `.exe` compilado?

## 2. Testes Essenciais (Obrigatório funcionar na frente do cliente)

### A. Fluxo de Venda (O Coração do Sistema)

1. [ ] Abrir o Sistema e Logar como **Vendedor**.
2. [ ] Adicionar 2 produtos diferentes ao carrinho.
3. [ ] Alterar a quantidade de um deles para 2 unidades.
4. [ ] Finalizar a Venda (dinheiro).
5. [ ] **Verificar**: O Recibo (PDF) abriu? O valor total está certo?
6. [ ] **Verificar**: O Stock desses produtos diminuiu na quantia certa?

### B. Fluxo do Gerente/Admin

1. [ ] Logar como **Admin**.
2. [ ] Ir ao **Dashboard**.
3. [ ] Verificar se a venda que acabou de fazer aparece no "Faturamento Hoje".
4. [ ] Ir em **Relatórios** -> Gerar "Relatório Mensal".
5. [ ] **Verificar**: O PDF mostra o nome do Vendedor e o valor correto?

### C. Gestão de Usuários

1. [ ] Criar um novo usuário (ex: "vendedor_novo").
2. [ ] Sair (Logout) e tentar entrar com esse novo usuário.

## 3. Perguntas para fazer ao Cliente (Feedback)

- "O tamanho da letra está bom para ler?"
- "É fácil achar os produtos na busca?"
- "Falta alguma informação essencial no Recibo?"

## 4. Plano de Contingência (Se algo der errado)

- Se der erro, tire uma foto da mensagem de erro.
- Tenha o WhatsApp do suporte (você) fácil de acessar.
- Reinicie o programa e veja se o erro persiste.
