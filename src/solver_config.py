import logging
import json
import time
from typing import Dict, Any
import pulp

# Configuração de Logging para Auditabilidade
logging.basicConfig(
    filename='atm_decisions_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ATMOptimizerSolver:
    def __init__(self, solver_name: str = "CBC"):
        self.solver_name = solver_name.upper()

    def _get_solver(self, time_limit_sec: int = 30):
        """Seleciona entre os solvers CBC e HiGHS com limite de tempo e fallback."""
        if self.solver_name == "HIGHS":
            # HiGHS é um solver moderno open-source de alta performance
            return pulp.HiGHS_CMD(timeLimit=time_limit_sec, msg=False)
        else:
            return pulp.PULP_CBC_CMD(timeLimit=time_limit_sec, msg=False)

    def log_decision_event(self, day: int, initial_state: Dict[int, int], demand: float, decision: Dict[str, Any], solver_time: float, status: str):
        """Mecanismo de Explicabilidade e Auditabilidade exigido pela vaga."""
        audit_payload = {
            "day": day,
            "status": status,
            "solver_used": self.solver_name,
            "execution_latency_sec": round(solver_time, 4),
            "cassette_state_before": initial_state,
            "requested_demand_brl": demand,
            "action_taken": decision
        }
        logging.info(f"AUDIT_DECISION: {json.dumps(audit_payload)}")
        return audit_payload