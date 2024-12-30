import cirq

def build_grover_marking(data_qubits, ancilla, S_n):
    """
    Marking circuit (oracle) for Grover:
    - data_qubits: 7 qubits for the search space
    - ancilla: 1 additional qubit (the target of multi-controlled Z)
    - S_n: a list/set of integers in [0..127] to be phase-flipped
    """
    circuit = cirq.Circuit()
    n = len(data_qubits)  # should be 7
    for x in S_n:
        bin_str = format(x, '0{}b'.format(n))  # e.g. '0101101' for 7 bits
        ops = []
        # Flip '0'-bits so that the desired state is |111...1>
        for i, bit in enumerate(bin_str):
            if bit == '0':
                ops.append(cirq.X(data_qubits[i]))
        # Multi-controlled Z on ancilla, controlled by data_qubits
        # The ancilla is *not* in data_qubits, so no duplication
        ops.append(cirq.Z(ancilla).controlled_by(*data_qubits))
        # Unflip
        for i, bit in enumerate(bin_str):
            if bit == '0':
                ops.append(cirq.X(data_qubits[i]))
        circuit.append(ops)
    return circuit

def build_grover_diffusion(data_qubits):
    """
    Standard Grover diffusion operator on the 7 data qubits (no ancilla).
    1) H^n
    2) X^n
    3) Multi-controlled Z (target is the last data_qubit) 
    4) X^n
    5) H^n
    """
    circuit = cirq.Circuit()
    n = len(data_qubits)
    circuit.append(cirq.H.on_each(*data_qubits))
    circuit.append(cirq.X.on_each(*data_qubits))
    # multi-controlled Z on last data-qubit, controlled by the first (n-1)
    circuit.append(cirq.Z(data_qubits[-1]).controlled_by(*data_qubits[:-1]))
    circuit.append(cirq.X.on_each(*data_qubits))
    circuit.append(cirq.H.on_each(*data_qubits))
    return circuit

def run_grover_search_on_7qubits_with_ancilla(S_n, num_iterations=4, repetitions=1000):
    """
    8 qubits total:
      - data_qubits[0..6]: 7 for the search space
      - ancilla (qubit[7]): target of marking
    Steps:
      1) data_qubits -> uniform superposition
      2) ancilla -> |0> (unchanged)
      3) repeated marking + diffusion
      4) measure data_qubits (optionally also ancilla)
    Returns final circuit & histogram
    """
    # Create 8 line qubits: 7 data + 1 ancilla
    qubits = [cirq.LineQubit(i) for i in range(8)]
    data_qubits = qubits[:7]
    ancilla = qubits[7]
    
    circuit = cirq.Circuit()
    
    # Step 1: put only the data_qubits in uniform superposition
    circuit.append(cirq.H.on_each(*data_qubits))
    # The ancilla stays in |0>
    
    # Step 2: Grover iterations
    for _ in range(num_iterations):
        # Mark
        circuit += build_grover_marking(data_qubits, ancilla, S_n)
        # Diffuse
        circuit += build_grover_diffusion(data_qubits)
    
    # Step 3: measure data_qubits (and ancilla if you want)
    circuit.append(cirq.measure(*data_qubits, key='m_data'))
    circuit.append(cirq.measure(ancilla, key='m_ancilla'))
    
    sim = qsimcirq.QSimSimulator()
    result = sim.run(circuit, repetitions=repetitions)
    
    hist_data = result.histogram(key='m_data')
    hist_anc = result.histogram(key='m_ancilla')
    return circuit, hist_data, hist_anc
