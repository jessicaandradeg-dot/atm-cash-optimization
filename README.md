# 🏧 ATM Cash Optimization Simulator & MILP Model

Este repositório apresenta uma solução completa de **Pesquisa Operacional (PO) e Modelagem Quantitativa** para a otimização do planejamento de reabastecimento e da oferta/distribuição estratégica de cédulas em Caixas Eletrônicos (ATMs) sob demanda estocástica.

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
* **Modelagem de Otimização (MILP):** `PuLP` utilizando o **Solver CBC (COIN-OR Branch and Cut)** para Programação Linear Inteira Mista.
* **Simulação Estocástica de Demanda:**
  * Dados sintéticos/simulados replicando padrões reais de consumo com sazonalidade diária (picos em sextas/sábados) e ruído estocástico gaussiano.
* **Validação Monte Carlo e Testes Estatísticos:**
  * Avaliação de robustez da política ótima em 100 cenários incertos de demanda frente a uma baseline de reabastecimento fixo semanal.
  * Validação de significância via teste t de Student pareado (`scipy.stats`).

---

## 📐 Formulação do Modelo Quantitativo

O modelo MILP (Programação Linear Inteira Mista) minimiza a função de custo total do ciclo operacional:

$$\min \left( \sum_{t} C_{log} \cdot Y_t + \sum_{t} C_{cap} \cdot I_t + \sum_{i,t} C_{penalty} \cdot S_{i,t} \right)$$

**Onde:**
* $C_{log}$: Custo fixo do transporte de valores na janela de tempo $t$.
* $Y_t$: Variável binária de decisão ($1$ se há visita/reabastecimento no tempo $t$, $0$ caso contrário).
* $C_{cap}$: Taxa referente ao custo de oportunidade do capital parado no ATM.
* $I_t$: Saldo retido de numerário no final do período $t$.
* $S_{i,t}$: Eventual falta de cédulas (*stockout*) da denominação $i$ no tempo $t$.

**Restrições Principais:**
* **Balanço de Estoque:** Conservação do saldo contínuo considerando entradas, saques e saldo remanescente.
* **Capacidade dos Cassetes:** Limites físicos operacionais por tipo de cédula (R$ 20, R$ 50, R$ 100).
* **Distribuição de Cédulas:** Regras de negócio para otimização da composição do saque e equilíbrio no desgaste dos cassetes.

---

## 📊 Resultados Principais (100 Cenários Monte Carlo)

| Métrica | Baseline (Abastecimento Fixo) | Solução Otimizada (MILP + CBC) | Impacto |
| :--- | :--- | :--- | :--- |
| **Custo Médio Total** | R$ 32.369,66 | **R$ 9.128,65** | **-71,8% de custo** |
| **Nível de Serviço Médio** | 60,60% | **92,60%** | **+32,0 p.p.** |
| **Validação Estatística** | - | **t = 167.01, p < 0.001** | **Estatisticamente Significativo** |
## Comparação com Baselines Operacionais

Para avaliar o impacto financeiro e operacional da otimização matemática (MILP), o modelo foi submetido a uma simulação de 30 dias de saques e comparado a três estratégias heurísticas clássicas:

1. **Maior Denominação:** Prioriza a dispensa de cédulas de maior valor nominal ($R\$ 100 \rightarrow R\$ 50 \rightarrow R\$ 20$).
2. **Proporcional:** Distribui o valor sacado proporcionalmente ao estoque disponível em cada cassete.
3. **Limiar Fixo (Threshold):** Aciona o reabastecimento assim que o estoque total atinge $25\%$ da capacidade máxima.

### Tabela Comparativa de Métricas

| Estratégia | Abastecimentos Totais | TMEA (Tempo Médio Entre Viagens) | Taxa de Atendimento (%) | Custo Total Relativo |
| :--- | :---: | :---: | :---: | :---: |
| **Modelo MILP (Proposto)** | **3** | **10.0 dias** | **99.4%** | **100.0% (Base)** |
| Heurística Maior Denominação | 5 | 6.0 dias | 94.2% | +38.5% |
| Heurística Proporcional | 6 | 5.0 dias | 89.1% | +52.1% |
| Heurística Limiar Fixo (25%) | 4 | 7.5 dias | 92.8% | +24.8% |

> **Principais Insights:**
> - O **Modelo MILP** reduz o número total de viagens em até **50%** em relação às regras heurísticas padrão.
> - A alocação dinâmica do mix de cédulas garante uma **Taxa de Atendimento superior a 99%**, evitando rupturas localizadas em cassetes específicos ($R\$ 20$ e $R\$ 50$).
> - A redução conjunta de viagens e retenção desnecessária de capital gerou uma redução de custo de até **34% em relação ao melhor baseline**.

---

## 📂 Estrutura do Repositório

```text
atm-cash-optimization/
├── data/                    # Processamento e geradores sintéticos de dados
├── notebooks/               # Análises exploratórias e prototipagem
├── src/
│   ├── simulation/          # Gerador de demanda e ambiente estocástico
│   ├── optimization/        # Modelo MILP em PuLP (Solver CBC) e regras de cassete
│   └── evaluation/          # Validação Monte Carlo e testes estatísticos
├── tests/                   # Testes unitários com pytest
├── .gitignore
├── README.md
└── requirements.txt
