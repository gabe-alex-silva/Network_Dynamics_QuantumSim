# ============================
# deutsch_josza.py
# ============================
def classical_threshold_assignment(S_n, Sigma_T):
    """
    If x >= Sigma_T => 1, else 0
    """
    threshold_dict = {}
    for x in S_n:
        threshold_dict[x] = 1 if x >= Sigma_T else 0
    return threshold_dict

import cirq
import qsimcirq

def build_deutsch_josza_oracle_7q(qubits, ancilla, S_n, threshold_dict, assign_complement):
    """
    S_n: set of actual states
    threshold_dict: {x: 0 or 1} if x in S_n
    assign_complement: 0 or 1 for x not in S_n
    """
    circuit = cirq.Circuit()
    n = len(qubits)
    
    def f(x):
        if x in threshold_dict:
            return threshold_dict[x]
        else:
            return assign_complement
    
    for x in range(2**n):
        if f(x) == 1:
            bin_str = format(x, f'0{n}b')
            ops = []
            # Flip 0-bits
            for i, bit in enumerate(bin_str):
                if bit == '0':
                    ops.append(cirq.X(qubits[i]))
            # multi-controlled Z on ancilla
            ops.append(cirq.Z(ancilla).controlled_by(*qubits))
            # unflip 0-bits
            for i, bit in enumerate(bin_str):
                if bit == '0':
                    ops.append(cirq.X(qubits[i]))
            circuit.append(ops)
    return circuit

def run_deutsch_josza_7q(S_n, threshold_dict, assign_complement, reps=512):
    """
    7 data qubits + 1 ancilla
    Steps:
      - ancilla -> |1>
      - H on all qubits
      - Oracle
      - H on all
      - measure
    """
    qubits = [cirq.LineQubit(i) for i in range(7)]
    ancilla = cirq.LineQubit(7)
    circuit = cirq.Circuit()
    
    # ancilla => |1>
    circuit.append(cirq.X(ancilla))
    # hadamard on all
    for q in qubits + [ancilla]:
        circuit.append(cirq.H(q))
    
    oracle = build_deutsch_josza_oracle_7q(qubits, ancilla, S_n, threshold_dict, assign_complement)
    circuit += oracle
    
    # final hadamard
    for q in qubits + [ancilla]:
        circuit.append(cirq.H(q))
    
    circuit.append(cirq.measure(*qubits, ancilla, key='m'))
    
    sim = qsimcirq.QSimSimulator()
    result = sim.run(circuit, repetitions=reps)
    counts = result.histogram(key='m')
    return circuit, counts
