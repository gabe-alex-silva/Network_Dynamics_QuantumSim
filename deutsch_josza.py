import cirq

def classical_threshold_assignment(S_n, Sigma_T):
    """
    For each x in S_n: if x >= Sigma_T => 1, else => 0.
    Return a dict threshold_dict[x] = 0 or 1.
    """
    threshold_dict = {}
    for x in S_n:
        threshold_dict[x] = 1 if x >= Sigma_T else 0
    return threshold_dict

def build_deutsch_josza_oracle_7q(qubits, ancilla, S_n, threshold_dict, assign_complement):
    """
    7 data qubits + 1 ancilla:
      For x in [0..127]:
        if x in S_n => f(x) = threshold_dict[x],
        else => f(x) = assign_complement.
      If f(x)=1, flip ancilla's phase.
    """
    circuit = cirq.Circuit()
    n = len(qubits)  # should be 7
    def f(x):
        if x in threshold_dict:
            return threshold_dict[x]
        else:
            return assign_complement
    
    for x in range(2**n):
        if f(x) == 1:
            bin_str = format(x, '0{}b'.format(n))
            ops = []
            for i, bit in enumerate(bin_str):
                if bit == '0':
                    ops.append(cirq.X(qubits[i]))
            # multi-controlled Z on ancilla
            ops.append(cirq.Z(ancilla).controlled_by(*qubits))
            for i, bit in enumerate(bin_str):
                if bit == '0':
                    ops.append(cirq.X(qubits[i]))
            circuit.append(ops)
    return circuit

def run_deutsch_josza_7q(S_n, threshold_dict, assign_complement, reps=1024):
    """
    7 system qubits + 1 ancilla:
      1) ancilla -> |1>
      2) H on all 7 + ancilla
      3) Oracle
      4) H on all 7 + ancilla
      5) measure
    """
    qubits = [cirq.LineQubit(i) for i in range(7)]
    ancilla = cirq.LineQubit(7)
    circuit = cirq.Circuit()
    
    # 1) ancilla -> |1>
    circuit.append(cirq.X(ancilla))
    # 2) hadamard on all 7 + ancilla
    for q in qubits + [ancilla]:
        circuit.append(cirq.H(q))
    
    # 3) Oracle
    oracle_circ = build_deutsch_josza_oracle_7q(qubits, ancilla, S_n, threshold_dict, assign_complement)
    circuit += oracle_circ
    
    # 4) final H
    for q in qubits + [ancilla]:
        circuit.append(cirq.H(q))
    
    # 5) measure
    circuit.append(cirq.measure(*qubits, ancilla, key='m'))
    
    sim = qsimcirq.QSimSimulator()
    result = sim.run(circuit, repetitions=reps)
    counts = result.histogram(key='m')
    return circuit, counts
