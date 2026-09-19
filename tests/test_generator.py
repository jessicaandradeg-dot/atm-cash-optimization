import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.simulation.generator import ATMDemandSimulator


def test_generate_series_shape_and_columns():
    simulator = ATMDemandSimulator(base_demand=50000.0, seed=42)
    df = simulator.generate_series(start_date='2026-01-01', days=10)

    assert len(df) == 10
    assert 'date' in df.columns
    assert 'demand' in df.columns
    assert (df['demand'] >= 0).all()