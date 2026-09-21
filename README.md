# ?? ATM Cash Optimization Simulator & MILP Model

Projeto de Pesquisa Operacional e otimização aplicada para reduzir custos logísticos e melhorar a disponibilidade de numerário em redes de ATMs.

## Problema de negócio

Uma rede de caixas eletrônicos precisa equilibrar três forças ao mesmo tempo:

- reduzir visitas de carro-forte e custos logísticos
- evitar capital ocioso em cassetes
- garantir atendimento ao cliente sem falhas por falta de cédulas

Quando o mix de notas está mal dimensionado, o banco sofre com: falta de saque em denominações específicas, abastecimentos frequentes, custo elevado de operação e pior experiência do cliente.

Este projeto modela o problema como uma decisão sequencial sob incerteza, com foco em melhorar a política de reposição e alocação de cédulas por cassete.

## O que foi construído

- simulação de demanda de saques por ATM
- reamostragem de histórico com bootstrap
- otimização de reposição por horizonte móvel
- modelo MILP para decisão de mix de cédulas
- comparação com políticas heurísticas operacionais
- logging de decisões para explicabilidade e rastreabilidade

## Metodologia

A solução combina:

1. criação de cenário de demanda por caixa eletrônico
2. amostragem do histórico para capturar variabilidade
3. modelagem de estoque por denominação e período
4. otimização com programação inteira mista
5. avaliação contra baselines tradicionais

A estrutura do problema considera:

- variáveis de decisão sobre reposição por período
- estoque por denominação (R$ 20, R$ 50, R$ 100)
- capacidade de cada cassete
- penalidade por ruptura de atendimento
- custo de transporte e oportunidade do capital

## Resultados e KPI

### Métricas principais

- número de abastecimentos
- tempo médio entre abastecimentos
- nível de serviço por denominação
- custo total relativo
- taxa de atendimento de demanda

### Resultado ilustrativo

| Estratégia | Abastecimentos | TMEA (dias) | Serviço R$ 100 | Serviço R$ 50 | Serviço R$ 20 | Custo relativo |
|---|---:|---:|---:|---:|---:|---:|
| Modelo MILP | 3 | 10.0 | 99.8% | 99.2% | 99.1% | 100.0% |
| Maior denominação | 5 | 6.0 | 98.1% | 91.5% | 85.0% | +38.5% |
| Proporcional | 6 | 5.0 | 90.2% | 88.4% | 88.7% | +52.1% |
| Limiar fixo | 4 | 7.5 | 95.0% | 92.1% | 90.3% | +24.8% |

## Benchmark comparativo

O projeto demonstra que a otimização matemática supera regras práticas em:

- redução de abastecimentos
- melhor manutenção de nível de serviço
- maior estabilidade operacional
- menor custo total

Esse benchmark é importante para mostrar maturidade em pesquisa operacional e capacidade de escolher uma política baseada em desempenho real.

## Stack

- Python
- PuLP
- NumPy
- Pandas
- SciPy
- CBC / HiGHS
- Simulação estocástica
- JSON logging e auditabilidade

## Diagrama de fluxo

```text
Histórico de saques
        ?
Reamostragem / simulação
        ?
Definição de demanda por período
        ?
Modelo MILP + restrições de estoque
        ?
Política de reposição
        ?
Avaliação por KPI operacional
```

## Estrutura do repositório

```text
atm-cash-optimization/
+-- data/
+-- notebooks/
+-- src/
¦   +-- simulation/
¦   +-- optimization/
¦   +-- baselines.py
¦   +-- audit_logger.py
+-- tests/
+-- README.md
+-- requirements.txt
+-- .gitignore
```

## Relevância para vagas

Este projeto se conecta diretamente com vagas de:

- Pesquisa Operacional
- OTIMIZAÇÃO
- Decision Science
- Supply Chain Analytics
- Analytics aplicada a operações financeiras
- Data Science orientado a impacto operacional

## Próximos passos recomendados

- incluir benchmark em gráficos e imagens
- comparar políticas online vs offline
- avaliar aprendizado por reforço como alternativa
- adicionar visualização de estoque por denominação e tempo
- publicar um resumo executivo com KPI e metodologia

## Link para artigo / benchmark / tabela

- [Benchmark de políticas](#)
- [Resumo executivo](#)
- [Notebook de simulação](#)
- [Relatório de resultados](#)

## Mensagem para recrutadores

Este projeto combina otimização matemática, simulação estocástica e análise operacional para resolver um problema real de logística financeira. Em vez de focar apenas em modelo estatístico, a solução foi pensada para reduzir custos e melhorar a qualidade de serviço em operação.

Ele mostra capacidade de formular problema de negócio, transformar em modelo quantitativo, escolher política com base em performance e explicar decisões de forma auditável.

---

## Documentação técnica adicional

A formulação MILP minimiza custo total com restrições de demanda, balanço de estoque e capacidade dos cassetes, incluindo variáveis binárias para o momento do abastecimento e variáveis de quantidade por denominação.

$$
\min \sum_{t=1}^{T} \left( C_{\text{log}} \cdot Y_t + C_{\text{cap}} \sum_{d \in \{20,50,100\}} d \cdot I_{d,t} + \sum_{d \in \{20,50,100\}} \pi_d \cdot S_{d,t} \right)
$$

Esta abordagem reforça o alinhamento do projeto com cenários reais de otimização em ambientes financeiros e logísticos.
