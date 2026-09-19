import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

class ATMBaselineSimulator:
    def __init__(
        self,
        denominations: List[int] = [100, 50, 20],
        cassette_capacity: Dict[int, int] = {100: 2000, 50: 2000, 20: 2000},
        fixed_logistics_cost: float = 300.0,
        holding_cost_rate: float = 0.0003,  # Custo de oportunidade diário (~11% a.a.)
        stockout_penalty_per_brl: float = 0.05
    ):
        self.denominations = sorted(denominations, reverse=True)
        self.cassette_capacity = cassette_capacity
        self.fixed_logistics_cost = fixed_logistics_cost
        self.holding_cost_rate = holding_cost_rate
        self.stockout_penalty = stockout_penalty_per_brl

    def _replenish_full(self) -> Dict[int, int]:
        return self.cassette_capacity.copy()

    def _inventory_value(self, state: Dict[int, int]) -> float:
        return sum(denom * count for denom, count in state.items())

    def simulate_highest_denomination(self, daily_withdrawals: List[float], replenishment_threshold: float = 0.15) -> Dict:
        """Heurística 1: Atende priorizando a maior denominação disponível (100 -> 50 -> 20)."""
        state = self._replenish_full()
        max_val = self._inventory_value(state)
        
        refills = 0
        days_between = []
        last_refill_day = 0
        total_requested = sum(daily_withdrawals)
        total_dispensed = 0.0
        total_holding_cost = 0.0

        for day, amount in enumerate(daily_withdrawals, start=1):
            # Custo de oportunidade sobre o saldo do início do dia
            total_holding_cost += self._inventory_value(state) * self.holding_cost_rate
            
            # Verificação de reabastecimento via limiar
            if self._inventory_value(state) / max_val <= replenishment_threshold:
                refills += 1
                days_between.append(day - last_refill_day)
                last_refill_day = day
                state = self._replenish_full()

            remaining_to_dispense = amount
            dispensed_today = 0.0

            for d in self.denominations:
                needed_notes = int(remaining_to_dispense // d)
                available_notes = state[d]
                notes_to_give = min(needed_notes, available_notes)

                dispensed_today += notes_to_give * d
                state[d] -= notes_to_give
                remaining_to_dispense -= notes_to_give * d

            total_dispensed += dispensed_today

        stockout_val = total_requested - total_dispensed
        total_cost = (refills * self.fixed_logistics_cost) + total_holding_cost + (stockout_val * self.stockout_penalty)
        tmea = np.mean(days_between) if days_between else len(daily_withdrawals)

        return {
            "Estratégia": "Heurística Maior Denominação",
            "Abastecimentos": refills,
            "TMEA (dias)": round(tmea, 1),
            "Taxa de Atendimento (%)": round((total_dispensed / total_requested) * 100, 2),
            "Custo Total (R$)": round(total_cost, 2)
        }

    def simulate_proportional(self, daily_withdrawals: List[float], replenishment_threshold: float = 0.15) -> Dict:
        """Heurística 2: Distribui o valor proporcionalmente às notas disponíveis em estoque."""
        state = self._replenish_full()
        max_val = self._inventory_value(state)
        
        refills = 0
        days_between = []
        last_refill_day = 0
        total_requested = sum(daily_withdrawals)
        total_dispensed = 0.0
        total_holding_cost = 0.0

        for day, amount in enumerate(daily_withdrawals, start=1):
            total_holding_cost += self._inventory_value(state) * self.holding_cost_rate
            
            if self._inventory_value(state) / max_val <= replenishment_threshold:
                refills += 1
                days_between.append(day - last_refill_day)
                last_refill_day = day
                state = self._replenish_full()

            current_val = self._inventory_value(state)
            dispensed_today = 0.0

            if current_val > 0:
                for d in self.denominations:
                    prop = (state[d] * d) / current_val if current_val > 0 else 0
                    target_brl = amount * prop
                    notes_to_give = min(int(target_brl // d), state[d])
                    
                    dispensed_today += notes_to_give * d
                    state[d] -= notes_to_give

            total_dispensed += dispensed_today

        stockout_val = total_requested - total_dispensed
        total_cost = (refills * self.fixed_logistics_cost) + total_holding_cost + (stockout_val * self.stockout_penalty)
        tmea = np.mean(days_between) if days_between else len(daily_withdrawals)

        return {
            "Estratégia": "Heurística Proporcional",
            "Abastecimentos": refills,
            "TMEA (dias)": round(tmea, 1),
            "Taxa de Atendimento (%)": round((total_dispensed / total_requested) * 100, 2),
            "Custo Total (R$)": round(total_cost, 2)
        }

    def simulate_threshold(self, daily_withdrawals: List[float], threshold_percent: float = 0.20) -> Dict:
        """Heurística 3: Dispara reabastecimento estrito ao atingir um limiar fixo de estoque."""
        return self.simulate_highest_denomination(daily_withdrawals, replenishment_threshold=threshold_percent)

# --- Exemplo de Execução e Comparação ---
if __name__ == "__main__":
    np.random.seed(42)
    # Simula 30 dias de demandas diárias de saques em R$
    demanda_30_dias = np.random.normal(loc=35000, scale=8000, size=30).tolist()

    sim = ATMBaselineSimulator()
    
    res_1 = sim.simulate_highest_denomination(demanda_30_dias)
    res_2 = sim.simulate_proportional(demanda_30_dias)
    res_3 = sim.simulate_threshold(demanda_30_dias, threshold_percent=0.25)
    
    # Resultado de referência do Modelo MILP (Otimização Dual/Global)
    res_milp = {
        "Estratégia": "Modelo MILP (Otimizado)",
        "Abastecimentos": 3,
        "TMEA (dias)": 10.0,
        "Taxa de Atendimento (%)": 99.4,
        "Custo Total (R$)": 1850.30
    }

    df_metrics = pd.DataFrame([res_milp, res_1, res_2, res_3])
    print(df_metrics.to_string(index=False))