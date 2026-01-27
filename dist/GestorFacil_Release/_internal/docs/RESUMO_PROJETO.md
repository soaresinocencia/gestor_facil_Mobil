# Resumo e Avaliação do Projecto: Gestor Fácil

## 1. Avaliação do Projecto

### Pontos Fortes

* **Interface Moderna**: Utiliza `CustomTkinter` para criar uma interface visualmente limpa, com suporte a temas (dark/light implícito) e responsividade básica.
* **Robustez**: O sistema é "Offline-First", utilizando SQLite local, o que garante funcionamento mesmo sem internet.
* **Hierarquia de Acesso**: Implementação sólida de controlo de acesso (Super Admin, Admin, Gerente, Vendedor), garantindo que cada utilizador veja apenas o que deve.
* **Funcionalidades Completas**: Cobre todo o ciclo de vida essencial: Stock, Vendas (POS), Gestão de Equipe, Relatórios Financeiros e Despesas.
* **Portabilidade**: A estrutura está pronta para ser compilada num `.exe` independente.

### Oportunidades de Melhoria (Futuro)

* **Sincronização Cloud**: Atualmente é 100% local. Numa versão "Pro", poderia sincronizar dados com uma Google Sheet ou Firebase para o administrador ver dados remotamente.
* **Gestão de Clientes**: O POS permite digitar nome do cliente, mas não gerencia uma base de dados de "Clientes Fiéis" com histórico detalhado.
* **Impressão Térmica Direta**: O sistema gera PDFs. Para alta performance num supermercado, o ideal seria envio direto de comandos (ESC/POS) para a impressora, sem abrir PDF.

---

## 2. Como o Sistema Funciona (Arquitectura)

O sistema segue uma estrutura modular, o que facilita a manutenção.

### Estrutura de Pastas

* `main.py`: **O Motor de Arranque**. É onde tudo começa. Inicia a aplicação.
* `src/database.py`: **O Cérebro (Memória)**. Contém todas as funções que falam com o Banco de Dados (SQLite). Nenhuma tela mexe nos dados diretamente; elas pedem funções daqui.
* `src/ui/`: **A Cara (Interface)**.
  * `app.py`: A janela principal que gerencia a navegação (Sidebar).
  * `login.py`: A porta de entrada (segurança).
  * `pos.py`: O Frente de Caixa (Vendas).
  * `admin.py`: O escritório (Gestão de usuários, dashboards).
  * `stock.py`: O armazém.
* `src/reports.py` & `charts.py`: **Os Analistas**. Geram PDFs e Gráficos baseados nos dados.

### Fluxo de Dados

1. **Usuário** clica num botão (ex: "Finalizar Venda").
2. **Interface (`pos.py`)** recolhe os dados da tela e valida.
3. **Interface** chama **`database.py`** (ex: `registar_venda()`).
4. **Database** grava no arquivo `.db` e confirma.
5. **Interface** chama **`reports.py`** para gerar o PDF do recibo.

---

## 3. Guia de Utilização (Resumo)

### Para o Vendedor

* **Acesso**: Entra com sem Login/Senha fornecido pelo Admin.
* **Função**: A tela principal será o **POS (Ponto de Venda)**.
* **Como Vender**:
    1. Pesquise o produto ou clique na lista à esquerda.
    2. O produto vai para o carrinho à direita.
    3. Clique em "Finalizar Venda".
    4. Opcional: Digite nome do cliente ou imprima recibo.

### Para o Gerente

* **Acesso**: Tem acesso ao POS, mas também ao **Dashboard** e **Gestão de Stock**.
* **Função**: Monitorizar a loja e garantir que não falta produto.
* **Tarefas**:
  * Adicionar novos produtos no Stock.
  * Verificar alertas de stock baixo no Dashboard.
  * Lançar Despesas (água, luz, limpeza) no módulo Despesas.

### Para o Admin (Dono)

* **Acesso**: Total. Pode ver tudo o que o Gerente vê, mais a **Gestão de Equipe**.
* **Função**: Gerir o negócio e as pessoas.
* **Dashboards**:
  * Vê o Lucro Líquido (Vendas - Custo Produtos - Despesas).
  * Vê gráficos de vendas.
  * Vê o relatório "Vendas por Vendedor" para pagar comissões.
* **Segurança**: Pode Criar/Bloquear/Remover usuários no menu Administração.

---

## 4. Tecnologias Usadas

* **Linguagem**: Python 3.12+
* **Interface Gráfica**: CustomTkinter (Moderno, baseada em Tkinter).
* **Banco de Dados**: SQLite3 (Nativo, sem instalação extra).
* **Relatórios**: ReportLab (Geração de PDFs profissionais).
* **Gráficos**: Matplotlib (Geração de imagens estatísticas).
