# =========================
# grover.py 
# =========================

def build_grover_marking(data_qubits, ancilla, S_n):
    """
    Oracle step: flips the phase of states in S_n.
    data_qubits: list of 7 qubits
    ancilla: qubit for multi-controlled Z
    S_n: list of decimal integers in [0..127] that are marked
    """
    circuit = cirq.Circuit()
    n = len(data_qubits)  # 7
    for x in S_n:
        bin_str = format(x, f'0{n}b')
        ops = []
        # Flip qubits that are '0'
        for i, bit in enumerate(bin_str):
            if bit == '0':
                ops.append(cirq.X(data_qubits[i]))
        # multi-controlled Z on ancilla
        ops.append(cirq.Z(ancilla).controlled_by(*data_qubits))
        # Unflip qubits that were '0'
        for i, bit in enumerate(bin_str):
            if bit == '0':
                ops.append(cirq.X(data_qubits[i]))
        circuit.append(ops)
    return circuit

def build_grover_diffusion(data_qubits):
    """
    Standard Grover diffusion operator:
    1) H^n
    2) X^n
    3) Multi-controlled Z about |000...0>
    4) X^n
    5) H^n
    """
    circuit = cirq.Circuit()
    circuit.append(cirq.H.on_each(*data_qubits))
    circuit.append(cirq.X.on_each(*data_qubits))
    # multi-controlled Z on last qubit
    circuit.append(cirq.Z(data_qubits[-1]).controlled_by(*data_qubits[:-1]))
    circuit.append(cirq.X.on_each(*data_qubits))
    circuit.append(cirq.H.on_each(*data_qubits))
    return circuit

def run_grover_search_on_7qubits_with_ancilla(S_n, num_iterations=3, repetitions=512):
    """
    8 qubits total => 7 data + 1 ancilla
    Steps:
      - Put data qubits in uniform superposition
      - Repeat marking + diffusion `num_iterations` times
      - Measure
    Returns (final_circuit, histogram_data, histogram_ancilla)
    """
    # 1) Create 8 line qubits
    qubits = [cirq.LineQubit(i) for i in range(8)]
    data_qubits = qubits[:7]
    ancilla = qubits[7]
    
    circuit = cirq.Circuit()
    
    # 2) Uniform superposition on data qubits
    circuit.append(cirq.H.on_each(*data_qubits))
    
    # 3) Repeated marking + diffusion
    for _ in range(num_iterations):
        circuit += build_grover_marking(data_qubits, ancilla, S_n)
        circuit += build_grover_diffusion(data_qubits)
    
    # 4) Measure data qubits + ancilla
    circuit.append(cirq.measure(*data_qubits, key='m_data'))
    circuit.append(cirq.measure(ancilla, key='m_ancilla'))
    
    # 5) Simulate
    sim = qsimcirq.QSimSimulator()
    result = sim.run(circuit, repetitions=repetitions)
    
    hist_data = result.histogram(key='m_data')
    hist_anc  = result.histogram(key='m_ancilla')
    return circuit, hist_data, hist_anc
