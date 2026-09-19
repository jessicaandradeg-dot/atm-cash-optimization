# ATM Cash Optimization Simulator & MILP Model

Este repositório apresenta uma solução de Pesquisa Operacional (PO) para otimização do abastecimento e distribuição de cédulas em Caixas Eletrônicos (ATMs) sob demanda estocástica.

## Contexto e Problema de Negócio

O gerenciamento de numerário em ATMs envolve um trade-off clássico:
- **Custo Logístico de Transportadora (Carro-forte):** Cada viagem possui um custo fixo elevado.
- **Custo de Oportunidade / Penalidade por Stockout:** A falta de cédulas gera insatisfação do cliente e perda de transações.

O objetivo do projeto é determinar a política ótima de abastecimento que minimiza o custo total de operação mantendo um alto nível de serviço.

## Metodologia e Arquitetura

1. **Simulação Estocástica de Demanda:**
   - Modelo com sazonalidade diária (picos em sextas/sábados) e ruído estocástico gaussiano.
2. **Modelo Otimizado (MILP):**
   - Formulado em **PuLP** como um problema de Programação Linear Inteira Mista com balanço de estoque e variáveis de decisão binárias para abastecimento.
3. **Validação Monte Carlo e Estatística:**
   - Avaliação da robustez da política ótima em 100 cenários incertos de demanda contra uma baseline de reabastecimento fixo semanal.
   - Aplicação de teste t de Student pareado via `scipy.stats`.

## Resultados Principais (100 Cenários Monte Carlo)

| Métrica | Baseline (Abastecimento Fixo) | Solução Otimizada (MILP) | Impacto |
| :--- | :--- | :--- | :--- |
| **Custo Médio Total** | R$ 32.369,66 | **R$ 9.128,65** | **-71,8% de custo** |
| **Nível de Serviço Médio** | 60,60% | **92,60%** | **+32,0 p.p.** |
| **Validação Estatística** | - | **t = 167.01, p < 0.001** | **Significativo** |

## Estrutura do Repositório

```text
atm-cash-optimization/
├── data/
├── notebooks/
├── src/
│   ├── simulation/      # Gerador de demanda e ambiente de simulação
│   ├── optimization/    # Modelo MILP em PuLP
│   └── evaluation/      # Simulação Monte Carlo e testes estatísticos
├── tests/               # Testes unitários com pytest
├── .gitignore
├── README.md
└── requirements.txt