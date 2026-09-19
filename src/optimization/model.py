"""
Módulo de Otimização Linear Inteira Mista (MILP) para Gestão de Numerário em ATMs.
"""

from typing import Dict, Any
import pandas as pd
import pulp


class ATMCashOptimizer:
    """
    Formulação e resolução de problema de otimização de estoque de numerário
    em Caixas Eletrônicos via Programação Linear Inteira Mista (MILP).
    """

    def __init__(
        self,
        holding_cost_rate: float = 0.0005,
        refill_cost: float = 300.0,
        stockout_cost_rate: float = 0.05,
        atm_capacity: float = 200000.0,
        min_refill_amount: float = 10000.0,
        initial_balance: float = 50000.0,
        capacity: float = None,
        **kwargs,
    ):
        """
        Parâmetros do modelo financeiro e operacional.
        Aceita 'capacity' e kwargs genéricos para compatibilidade total.
        """
        self.holding_cost_rate = holding_cost_rate
        self.refill_cost = refill_cost
        self.stockout_cost_rate = stockout_cost_rate
        self.atm_capacity = capacity if capacity is not None else atm_capacity
        self.min_refill_amount = min_refill_amount
        self.initial_balance = initial_balance

    def solve(self, demand_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Formula e resolve o modelo MILP para a série temporal de demanda fornecida.
        """
        time_steps = len(demand_df)
        days = list(range(time_steps))

        # 1. Instanciar o problema de minimização
        prob = pulp.LpProblem("ATM_Cash_Optimization", pulp.LpMinimize)

        # 2. Variáveis de Decisão
        inventory = pulp.LpVariable.dicts("Inv", days, lowBound=0, upBound=self.atm_capacity, cat=pulp.LpContinuous)
        refill_qty = pulp.LpVariable.dicts("RefillQty", days, lowBound=0, upBound=self.atm_capacity, cat=pulp.LpContinuous)
        refill_event = pulp.LpVariable.dicts("RefillEvent", days, cat=pulp.LpBinary)
        stockout = pulp.LpVariable.dicts("Stockout", days, lowBound=0, cat=pulp.LpContinuous)

        # 3. Função Objetivo: Minimizar Custo de Carregamento + Custo Fixo de Transporte + Penalidade de Stockout
        prob += pulp.lpSum([
            (inventory[t] * self.holding_cost_rate) +
            (refill_event[t] * self.refill_cost) +
            (stockout[t] * self.stockout_cost_rate)
            for t in days
        ])

        # 4. Restrições do Sistema
        for t in days:
            demand = float(demand_df.iloc[t]["demand"])

            # Balanço de Estoque
            if t == 0:
                prob += inventory[t] == self.initial_balance + refill_qty[t] - demand + stockout[t]
            else:
                prob += inventory[t] == inventory[t - 1] + refill_qty[t] - demand + stockout[t]

            # Vinculação da Variável Binária de Abastecimento (Big-M)
            prob += refill_qty[t] <= self.atm_capacity * refill_event[t]
            prob += refill_qty[t] >= self.min_refill_amount * refill_event[t]

        # 5. Resolver o Modelo (com fallback resiliente para arquitetura ARM64)
        solver_executed = False

        if not solver_executed:
            try:
                solver = pulp.HiGHS_CMD(msg=False)
                if solver.available():
                    prob.solve(solver)
                    solver_executed = True
            except Exception:
                pass

        if not solver_executed:
            try:
                solver = pulp.PULP_CBC_CMD(msg=False)
                if solver.available():
                    prob.solve(solver)
                    solver_executed = True
            except Exception:
                pass

        if not solver_executed:
            prob.solve(pulp.PULP_CBC_CMD(msg=False, path=None))

        # 6. Extração dos Resultados
        schedule = []
        for t in days:
            schedule.append({
                "day": t,
                "demand": demand_df.iloc[t]["demand"],
                "inventory": pulp.value(inventory[t]),
                "refill_qty": pulp.value(refill_qty[t]),
                "refill_event": int(pulp.value(refill_event[t])),
                "stockout": pulp.value(stockout[t]),
            })

        schedule_df = pd.DataFrame(schedule)
        total_cost = pulp.value(prob.objective)

        return {
            "status": pulp.LpStatus[prob.status],
            "total_cost": total_cost,
            "schedule": schedule_df,
        }