import pytest
import pulp
from src.solver_config import ATMOptimizerSolver

def test_solver_initialization_and_capabilities():
    """Valida se o gerenciador de solver suporta CBC e HiGHS."""
    cbc_solver = ATMOptimizerSolver(solver_name="CBC")
    highs_solver = ATMOptimizerSolver(solver_name="HIGHS")
    
    assert cbc_solver.solver_name == "CBC"
    assert highs_solver.solver_name == "HIGHS"

def test_infeasible_demand_scenario():
    """Testa o comportamento do modelo diante de uma demanda inviável fisicamente."""
    prob = pulp.LpProblem("Infeasible_ATM_Test", pulp.LpMinimize)
    
    # Variável de saldo
    I_100 = pulp.LpVariable("I_100", lowBound=0, upBound=2000, cat=pulp.LpInteger)
    
    # Demanda irreal de R$ 5.000.000
    prob += I_100 * 100 >= 5_000_000
    prob += I_100
    
    solver = pulp.PULP_CBC_CMD(msg=False)
    prob.solve(solver)
    
    # Valida se o solver detecta Inviabilidade (Infeasible status code)
    assert pulp.LpStatus[prob.status] in ["Infeasible", "Undefined"]