import pulp

def resolver_dispensacao_saque(valor_saque, saldo_cassetes, solver_name="CBC"):
    """
    Otimiza a dispensação de cédulas por saque (Mix R$ 20, R$ 50, R$ 100).
    Minimiza o esgotamento desproporcional dos cassetes.
    """
    denominacoes = [100, 50, 20]
    prob = pulp.LpProblem("Dispensacao_Cassetes", pulp.LpMinimize)
    
    x = {d: pulp.LpVariable(f"notas_{d}", lowBound=0, cat="Integer") for d in denominacoes}
    prob += pulp.lpSum([x[d] for d in denominacoes])
    
    prob += pulp.lpSum([d * x[d] for d in denominacoes]) == valor_saque, "Valor_Exato"
    for d in denominacoes:
        prob += x[d] <= saldo_cassetes.get(d, 0), f"Limite_Cassete_{d}"
        
    if solver_name == "HiGHS":
        solver = pulp.HiGHS_CMD(msg=False)
    else:
        solver = pulp.PULP_CBC_CMD(msg=False)
        
    status = prob.solve(solver)
    if status == pulp.LpStatusOptimal:
        return {d: int(x[d].varValue) for d in denominacoes}
    return None

def baseline_maior_denominacao(valor_saque, saldo_cassetes):
    res = {}
    sobra = valor_saque
    for d in [100, 50, 20]:
        qtd = min(sobra // d, saldo_cassetes.get(d, 0))
        res[d] = qtd
        sobra -= qtd * d
    return res if sobra == 0 else None

def baseline_proporcional(valor_saque, saldo_cassetes):
    total_saldo = sum(saldo_cassetes.values())
    if total_saldo == 0: return None
    res = {}
    sobra = valor_saque
    for d in [100, 50, 20]:
        prop = (saldo_cassetes[d] * d) / total_saldo
        qtd = min(int((valor_saque * prop) // d), saldo_cassetes[d])
        res[d] = qtd
        sobra -= qtd * d
    return res

def baseline_limiar(valor_saque, saldo_cassetes, limiar_minimo=10):
    if saldo_cassetes.get(100, 0) > limiar_minimo:
        return baseline_maior_denominacao(valor_saque, saldo_cassetes)
    else:
        return baseline_proporcional(valor_saque, saldo_cassetes)import pulp

def resolver_dispensacao_saque(valor_saque, saldo_cassetes, solver_name="CBC"):
    """
    Otimiza a dispensação de cédulas por saque (Mix R$ 20, R$ 50, R$ 100).
    Minimiza o esgotamento desproporcional dos cassetes.
    """
    denominacoes = [100, 50, 20]
    prob = pulp.LpProblem("Dispensacao_Cassetes", pulp.LpMinimize)
    
    x = {d: pulp.LpVariable(f"notas_{d}", lowBound=0, cat="Integer") for d in denominacoes}
    prob += pulp.lpSum([x[d] for d in denominacoes])
    
    prob += pulp.lpSum([d * x[d] for d in denominacoes]) == valor_saque, "Valor_Exato"
    for d in denominacoes:
        prob += x[d] <= saldo_cassetes.get(d, 0), f"Limite_Cassete_{d}"
        
    if solver_name == "HiGHS":
        solver = pulp.HiGHS_CMD(msg=False)
    else:
        solver = pulp.PULP_CBC_CMD(msg=False)
        
    status = prob.solve(solver)
    if status == pulp.LpStatusOptimal:
        return {d: int(x[d].varValue) for d in denominacoes}
    return None

def baseline_maior_denominacao(valor_saque, saldo_cassetes):
    res = {}
    sobra = valor_saque
    for d in [100, 50, 20]:
        qtd = min(sobra // d, saldo_cassetes.get(d, 0))
        res[d] = qtd
        sobra -= qtd * d
    return res if sobra == 0 else None

def baseline_proporcional(valor_saque, saldo_cassetes):
    total_saldo = sum(saldo_cassetes.values())
    if total_saldo == 0: return None
    res = {}
    sobra = valor_saque
    for d in [100, 50, 20]:
        prop = (saldo_cassetes[d] * d) / total_saldo
        qtd = min(int((valor_saque * prop) // d), saldo_cassetes[d])
        res[d] = qtd
        sobra -= qtd * d
    return res

def baseline_limiar(valor_saque, saldo_cassetes, limiar_minimo=10):
    if saldo_cassetes.get(100, 0) > limiar_minimo:
        return baseline_maior_denominacao(valor_saque, saldo_cassetes)
    else:
        return baseline_proporcional(valor_saque, saldo_cassetes)