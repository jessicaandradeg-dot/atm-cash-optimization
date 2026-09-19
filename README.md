# 🏧 ATM Cash Optimization Simulator & MILP Model

Este repositório apresenta uma solução completa de **Pesquisa Operacional (PO) e Modelagem Quantitativa** para a otimização do planejamento de reabastecimento, decisão sequencial e composição dinâmica de cédulas em Caixas Eletrônicos (ATMs) sob demanda estocástica.

---

## 📌 Contexto e Problema de Negócio

O gerenciamento de numerário em redes de ATMs envolve um trade-off analítico entre três pilares:
1. **Custo Logístico (Transporte de Valores):** Cada visita de carro-forte possui um custo fixo elevado para sangria/abastecimento.
2. **Custo de Oportunidade do Capital:** Dinheiro ocioso mantido nos cassetes sem render juros.
3. **Eficiência no Mix de Cédulas & Penalidade por Stockout:** Falta de numerário ou exaustão prematura de denominações específicas (R$ 20, R$ 50, R$ 100) gera falhas no saque e insatisfação do cliente.

O objetivo do projeto é determinar a política ótima de reabastecimento e alocação por cassete que minimiza o custo total de operação, garantindo alto nível de serviço.

---

## 🛠️ Metodologia e Tecnologias

* **Linguagem & Ambiente:** Python 3.x, `pandas`, `numpy`, `scipy`
* **Modelagem de Otimização (MILP):** `PuLP` utilizando suporte a múltiplos solvers: **COIN-OR Branch and Cut (CBC)** e **HiGHS_CMD**.
* **Decisão Sequencial sob Incerteza & Reamostragem:**
  * Reamostragem não-paramétrica (**Bootstrap**) a partir do histórico de saques.
  * Formulação com **Horizonte Movel (Rolling Horizon)** e regra de *fallback* heurístico em caso de extrapolação do tempo limite do solver.
* **Auditabilidade e Explicabilidade:**
  * Módulo de logging estruturado (`src/audit_logger.py`) gerando rastreabilidade completa em `.json` (estado inicial, demanda solicitada, tempo de execução e ação tomada por saque).

---

## 📐 Formulação do Modelo Quantitativo (MILP com Decisão de Mix)

O modelo MILP (Programação Linear Inteira Mista) minimiza a função de custo total do ciclo operacional e decide explicitamente a composição de notas liberadas em cada operação:

$$\min \sum_{t=1}^{T} \left( C_{\text{log}} \cdot Y_t + C_{\text{cap}} \sum_{d \in \{20,50,100\}} d \cdot I_{d,t} + \sum_{d \in \{20,50,100\}} \pi_d \cdot S_{d,t} \right)$$

### Definindo Variáveis de Decisão:
* $Y_t \in \{0, 1\}$: Variável binária de decisão ($1$ se há visita/reabastecimento no tempo $t$, $0$ caso contrário).
* $x_{d, t} \in \mathbb{Z}^+$: **Quantidade de cédulas da denominação $d$ dispensadas no saque do dia $t$**.
* $I_{d, t} \ge 0$: Saldo mantido no cassete da denominação $d$ no final do período $t$.
* $S_{d, t} \ge 0$: Ruptura (demanda não atendida em BRL) da denominação $d$ no dia $t$.

### Restrições Matemáticas:
1. **Atendimento da Demanda por Denominação:**
   $$\sum_{d \in \{20, 50, 100\}} d \cdot x_{d, t} = D_t - \sum_{d} S_{d, t} \quad \forall t$$
2. **Balanço de Estoque em Cassetes:**
   $$I_{d, t} = I_{d, t-1} - x_{d, t} + K_d \cdot Y_t \quad \forall d \in \{20, 50, 100\}, \forall t$$
3. **Capacidade Máxima do Cassete:**
   $$I_{d, t} \le K_d \quad \forall d, \forall t \quad (K_{100}=2000, K_{50}=2000, K_{20}=2000)$$

---

## 📊 Resultados Principais e Métricas por Denominação

| Estratégia | Abastecimentos | TMEA (Dias) | Nível de Serviço ($R\$ 100$) | Nível de Serviço ($R\$ 50$) | Nível de Serviço ($R\$ 20$) | Custo Total Relativo |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Modelo MILP (CBC / HiGHS)** | **3** | **10.0 dias** | **99.8%** | **99.2%** | **99.1%** | **100.0% (Base)** |
| Heurística Maior Denominação | 5 | 6.0 dias | 98.1% | 91.5% | 85.0% | +38.5% |
| Heurística Proporcional | 6 | 5.0 dias | 90.2% | 88.4% | 88.7% | +52.1% |
| Heurística Limiar Fixo (25%) | 4 | 7.5 dias | 95.0% | 92.1% | 90.3% | +24.8% |

---

## 📂 Estrutura do Repositório

```text
atm-cash-optimization/
├── data/                    # Processamento e geradores sintéticos de dados
├── notebooks/               # Análises exploratórias e prototipagem
├── src/
│   ├── simulation/          # Gerador de demanda e amostragem Bootstrap
│   ├── optimization/        # Modelo MILP em PuLP (Solvers CBC e HiGHS)
│   ├── baselines.py         # Heurísticas operacionais (Maior Denominação, Proporcional, Limiar)
│   └── audit_logger.py      # Logger de explicabilidade e rastreabilidade em JSON
├── tests/                   # Testes unitários com pytest
├── .gitignore
├── README.md
└── requirements.txt
