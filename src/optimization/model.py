import sys
from pathlib import Path

# Adiciona a raiz do projeto ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import pulp


class ATMCashOptimizer:
    """Modelo de Programação Linear Inteira Mista (MILP) para otimização
    de abastecimento de caixas eletrônicos (ATMs) utilizando PuLP.
    """

    def __init__(
        self,
        capacity: float = 200000.0,
        refill_cost: float = 500.0,
        stockout_penalty_per_unit: float = 0.05,
        initial_balance: float = 150000.0
    ):
        self.capacity = capacity
        self.refill_cost = refill_cost
        self.stockout_penalty_per_unit = stockout_penalty_per_unit
        self.initial_balance = initial_balance

    def solve(self, demand_df: pd.DataFrame) -> dict:
        """Formula e resolve o problema de otimização de abastecimento."""
        demands = demand_df['demand'].tolist()
        T = len(demands)

        # 1. Instanciar o Problema de Minimização
        prob = pulp.LpProblem("ATM_Cash_Optimization", pulp.LpMinimize)

        # 2. Variáveis de Decisão
        x = [pulp.LpVariable(f"refill_{t}", cat=pulp.LpBinary) for t in range(T)]
        I = [pulp.LpVariable(f"inventory_{t}", lowBound=0, upBound=self.capacity, cat=pulp.LpContinuous) for t in range(T)]
        s = [pulp.LpVariable(f"stockout_{t}", lowBound=0, cat=pulp.LpContinuous) for t in range(T)]

        # 3. Função Objetivo
        total_refill_cost = pulp.lpSum([x[t] * self.refill_cost for t in range(T)])
        total_stockout_cost = pulp.lpSum([s[t] * self.stockout_penalty_per_unit for t in range(T)])

        prob += total_refill_cost + total_stockout_cost, "Total_Operational_Cost"

        # 4. Restrições do Sistema
        for t in range(T):
            prev_inventory = self.initial_balance if t == 0 else I[t - 1]
            prob += I[t] == prev_inventory + (self.capacity * x[t]) - demands[t] + s[t], f"Inventory_Balance_{t}"

        # 5. Resolver o Modelo
        prob.solve(pulp.PULP_CBC_CMD(msg=False))

        # 6. Extrair Resultados
        refill_schedule = [bool(pulp.value(x[t])) for t in range(T)]
        opt_cost = pulp.value(prob.objective)

        return {
            'status': pulp.LpStatus[prob.status],
            'refill_schedule': refill_schedule,
            'optimal_cost': opt_cost
        }


if __name__ == '__main__':
    from src.simulation.environment import ATMEvironment
    from src.simulation.generator import ATMDemandSimulator

    gen = ATMDemandSimulator(base_demand=50000.0, seed=42)
    df_demand = gen.generate_series(start_date='2026-01-01', days=30)

    optimizer = ATMCashOptimizer(capacity=200000.0, refill_cost=500.0)
    opt_results = optimizer.solve(df_demand)

    print(f"Status do Solver: {opt_results['status']}")

    env = ATMEvironment(capacity=200000.0, refill_cost=500.0)
    sim_results = env.simulate_policy(df_demand, opt_results['refill_schedule'])

    print("\n--- Métricas da Solução Otimizada (MILP) ---")
    for key, val in sim_results['metrics'].items():
        print(f"{key}: {val}")