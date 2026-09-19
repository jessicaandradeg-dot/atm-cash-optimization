import sys
from pathlib import Path

# Adiciona a raiz do projeto ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
import numpy as np
import pandas as pd


class ATMEvironment:
    """Simula o comportamento operacional diário de um caixa eletrônico (ATM).

    Avalia custos logísticos de abastecimento e penalidades por indisponibilidade (stockout).
    """

    def __init__(
        self,
        capacity: float = 200000.0,
        refill_cost: float = 500.0,
        stockout_penalty_per_unit: float = 0.05,
        initial_balance: float = 150000.0
    ):
        """
        Args:
            capacity: Capacidade máxima de cédulas em valor monetário (R$).
            refill_cost: Custo fixo logístico por operação de abastecimento (carro-forte, equipe).
            stockout_penalty_per_unit: Custo de oportunidade/penalidade por R$ não atendido por falta de saldo.
            initial_balance: Saldo inicial no caixa eletrônico no dia 0.
        """
        self.capacity = capacity
        self.refill_cost = refill_cost
        self.stockout_penalty_per_unit = stockout_penalty_per_unit
        self.initial_balance = initial_balance

    def simulate_policy(self, demand_df: pd.DataFrame, refill_schedule: list[bool]) -> dict:
        """Executa a simulação diária com base em uma agenda predefinida de abastecimentos.

        Args:
            demand_df: DataFrame contendo a coluna 'demand' diária.
            refill_schedule: Lista booleana do mesmo tamanho de demand_df indicando se haverá
                             abastecimento no início de cada dia.

        Returns:
            dict contendo histórico detalhado e métricas agregadas de desempenho.
        """
        if len(demand_df) != len(refill_schedule):
            raise ValueError("O tamanho do histórico de demanda e da agenda de abastecimento devem ser iguais.")

        balance = self.initial_balance
        history = []

        total_refill_cost = 0.0
        total_stockout_penalty = 0.0
        total_unmet_demand = 0.0
        total_refills = 0

        for i, row in demand_df.iterrows():
            date = row['date']
            demand = row['demand']
            is_refill = refill_schedule[i]

            # Abastecimento no início do dia (recarrega até a capacidade máxima)
            refill_amount = 0.0
            if is_refill:
                refill_amount = self.capacity - balance
                balance = self.capacity
                total_refills += 1
                total_refill_cost += self.refill_cost

            # Atendimento da demanda do dia
            if balance >= demand:
                cash_dispensed = demand
                unmet_demand = 0.0
            else:
                cash_dispensed = balance
                unmet_demand = demand - balance

            balance -= cash_dispensed

            # Cálculo de penalidade por falta de dinheiro (Stockout)
            stockout_cost = unmet_demand * self.stockout_penalty_per_unit
            total_stockout_penalty += stockout_cost
            total_unmet_demand += unmet_demand

            history.append({
                'date': date,
                'starting_balance_after_refill': balance + cash_dispensed,
                'demand': demand,
                'cash_dispensed': cash_dispensed,
                'unmet_demand': unmet_demand,
                'ending_balance': balance,
                'is_refill': is_refill,
                'refill_cost': self.refill_cost if is_refill else 0.0,
                'stockout_cost': stockout_cost
            })

        history_df = pd.DataFrame(history)
        total_demand = demand_df['demand'].sum()
        service_level = ((total_demand - total_unmet_demand) / total_demand) * 100.0 if total_demand > 0 else 100.0

        metrics = {
            'total_cost': total_refill_cost + total_stockout_penalty,
            'refill_cost': total_refill_cost,
            'stockout_penalty': total_stockout_penalty,
            'total_refills': total_refills,
            'total_unmet_demand': total_unmet_demand,
            'service_level_pct': round(service_level, 2)
        }

        return {
            'metrics': metrics,
            'history': history_df
        }


if __name__ == '__main__':
    from src.simulation.generator import ATMDemandSimulator

    # 1. Gerar demanda
    gen = ATMDemandSimulator(base_demand=50000.0, seed=42)
    df_demand = gen.generate_series(start_date='2026-01-01', days=30)

    # 2. Criar ambiente
    env = ATMEvironment(capacity=200000.0, refill_cost=500.0)

    # 3. Testar política simples: Abastecer toda Quinta-feira (weekday == 3)
    refill_thursdays = [date.weekday() == 3 for date in df_demand['date']]

    res = env.simulate_policy(df_demand, refill_thursdays)

    print("--- Métricas da Baseline (Abastecimento Fixo às Quintas) ---")
    for key, val in res['metrics'].items():
        print(f"{key}: {val}")