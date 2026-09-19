import sys
from pathlib import Path

# Adiciona a raiz do projeto ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
from scipy import stats

from src.optimization.model import ATMCashOptimizer
from src.simulation.environment import ATMEvironment
from src.simulation.generator import ATMDemandSimulator


class PolicyEvaluator:
    """Realiza simulação Monte Carlo e testes de hipótese estatísticos

    para comparar diferentes políticas de abastecimento de caixa eletrônico.
    """

    def __init__(self, num_simulations: int = 100, days: int = 30):
        self.num_simulations = num_simulations
        self.days = days

    def run_monte_carlo(self) -> dict:
        """Executa a simulação Monte Carlo gerando cenários incertos de demanda."""
        baseline_costs = []
        milp_costs = []
        baseline_service = []
        milp_service = []

        # Usar uma demanda esperada para treinar o plano MILP
        train_gen = ATMDemandSimulator(base_demand=50000.0, seed=42)
        train_demand_df = train_gen.generate_series(start_date='2026-01-01', days=self.days)

        # Treinar o modelo MILP uma vez para obter a política fixa
        optimizer = ATMCashOptimizer(capacity=200000.0, refill_cost=500.0)
        opt_res = optimizer.solve(train_demand_df)
        milp_schedule = opt_res['refill_schedule']

        env = ATMEvironment(capacity=200000.0, refill_cost=500.0)

        for seed in range(self.num_simulations):
            # Gerar um cenário com ruído de demanda diferente
            gen = ATMDemandSimulator(base_demand=50000.0, seed=seed)
            scenario_df = gen.generate_series(start_date='2026-01-01', days=self.days)

            # Baseline: Abastecimento às quintas-feiras
            baseline_schedule = [date.weekday() == 3 for date in scenario_df['date']]

            # Avaliar ambas as políticas sob a mesma demanda incerta
            res_base = env.simulate_policy(scenario_df, baseline_schedule)
            res_milp = env.simulate_policy(scenario_df, milp_schedule)

            baseline_costs.append(res_base['metrics']['total_cost'])
            milp_costs.append(res_milp['metrics']['total_cost'])
            baseline_service.append(res_base['metrics']['service_level_pct'])
            milp_service.append(res_milp['metrics']['service_level_pct'])

        # Teste t de Student Pareado
        t_stat, p_value = stats.ttest_rel(baseline_costs, milp_costs)

        summary = {
            'baseline_mean_cost': np.mean(baseline_costs),
            'milp_mean_cost': np.mean(milp_costs),
            'baseline_mean_service': np.mean(baseline_service),
            'milp_mean_service': np.mean(milp_service),
            't_statistic': t_stat,
            'p_value': p_value
        }

        return summary


if __name__ == '__main__':
    evaluator = PolicyEvaluator(num_simulations=100)
    results = evaluator.run_monte_carlo()

    print("--- Resultados da Simulação Monte Carlo (100 Cenários) ---")
    print(f"Custo Médio Baseline: R$ {results['baseline_mean_cost']:.2f}")
    print(f"Custo Médio Otimizado (MILP): R$ {results['milp_mean_cost']:.2f}")
    print(f"Nível de Serviço Médio Baseline: {results['baseline_mean_service']:.2f}%")
    print(f"Nível de Serviço Médio Otimizado (MILP): {results['milp_mean_service']:.2f}%")
    print(f"\n--- Validação Estatística (Teste t Pareado) ---")
    print(f"Estatística t: {results['t_statistic']:.4f}")
    print(f"p-valor: {results['p_value']:.4e}")