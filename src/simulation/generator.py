import numpy as np
import pandas as pd


class ATMDemandSimulator:
    """Simula demanda diária de saques em caixas eletrônicos (ATMs)

    com sazonalidade semanal e variabilidade estocástica.
    """

    def __init__(self, base_demand: float = 50000.0, seed: int = 42):
        self.base_demand = base_demand
        self.seed = seed
        np.random.seed(self.seed)

        # Fatores multiplicadores por dia da semana (Seg=0, Dom=6)
        # Sexta e Sábado possuem maior volume de saques
        self.dow_factors = {
            0: 0.9,   # Segunda
            1: 0.8,   # Terça
            2: 0.85,  # Quarta
            3: 0.95,  # Quinta
            4: 1.4,   # Sexta
            5: 1.3,   # Sábado
            6: 0.8    # Domingo
        }

    def generate_series(self, start_date: str, days: int) -> pd.DataFrame:
        """Gera uma série temporal de demanda diária para o caixa eletrônico.

        Args:
            start_date (str): Data inicial no formato 'YYYY-MM-DD'.
            days (int): Quantidade de dias a simular.

        Returns:
            pd.DataFrame: DataFrame com colunas ['date', 'day_of_week', 'demand'].
        """
        dates = pd.date_range(start=start_date, periods=days, freq='D')
        records = []

        for date in dates:
            dow = date.dayofweek
            factor = self.dow_factors[dow]

            # Incerteza (ruído normal centrado em 1.0 com 15% de desvio padrão)
            noise = np.random.normal(loc=1.0, scale=0.15)
            daily_demand = max(0.0, round(self.base_demand * factor * noise, 2))

            records.append({
                'date': date,
                'day_of_week': date.strftime('%A'),
                'demand': daily_demand
            })

        return pd.DataFrame(records)


if __name__ == '__main__':
    simulator = ATMDemandSimulator()
    df = simulator.generate_series(start_date='2026-01-01', days=30)
    print("--- Primeiras linhas da demanda simulada ---")
    print(df.head())