##############################################################################
# This script allows testing and experimenting of Grover as a function of
# the number of elements in the set S_n and the number of Grover iterations.
# The output includes the frequency histogram of marked states in S_n
##############################################################################

#GROVER ORACLE
def build_oracle_mark_data_qubits(data_qubits, S_n):
    """
    data_qubits: list of 7 qubits (no ancilla!)
    S_n: set/list of marked decimal states in [0..127]
    
    For each x in S_n, we do:
      1) Flip '0'-bits so that the data qubits become |111...1> if state = x
      2) Multi-controlled Z on the last data qubit, controlled by the first (n-1)
      3) Unflip '0'-bits
    This imposes a global phase of -1 only on |x>.
    """
    circuit = cirq.Circuit()
    n = len(data_qubits)  # should be 7 (assuming 7-qubit search space)
    for x in S_n:
        bin_str = format(x, f'0{n}b')
        ops = []
        # 1) Flip any qubits whose bit is '0'
        for i, bit in enumerate(bin_str):
            if bit == '0':
                ops.append(cirq.X(data_qubits[i]))
        # 2) Multi-controlled Z on the last data qubit
        ops.append(
            cirq.Z(data_qubits[-1]).controlled_by(*data_qubits[:-1])
        )
        # 3) Unflip
        for i, bit in enumerate(bin_str):
            if bit == '0':
                ops.append(cirq.X(data_qubits[i]))
        circuit.append(ops)
    return circuit


# GROVER DIFFUSION
def build_grover_diffusion(data_qubits):
    """
    Standard Grover diffusion operator on the data qubits.
    1) H^n
    2) X^n
    3) multi-controlled Z (target = last qubit, controls = others)
    4) X^n
    5) H^n
    """
    circuit = cirq.Circuit()
    n = len(data_qubits)
    # 1) H on each qubit
    circuit.append(cirq.H.on_each(*data_qubits))
    # 2) X on each qubit
    circuit.append(cirq.X.on_each(*data_qubits))
    # 3) multi-controlled Z on last qubit, controlled by first (n-1)
    circuit.append(
        cirq.Z(data_qubits[-1]).controlled_by(*data_qubits[:-1])
    )
    # 4) X on each qubit
    circuit.append(cirq.X.on_each(*data_qubits))
    # 5) H on each qubit
    circuit.append(cirq.H.on_each(*data_qubits))
    return circuit

# GROVER MAIN RUN
def run_grover_7qubits(S_n, num_iterations=2, repetitions=512):
    """
    Perform Grover search over 7 data qubits (128 states).
    S_n: set/list of marked states (integers in [0..127])
    num_iterations = shots: number of times 'mark + diffusion' repetitions
    
    We'll measure data_qubits at the end and return a histogram.
    """
    # 1) Create 7 line qubits
    data_qubits = [cirq.LineQubit(i) for i in range(7)]
    
    # 2) Build the circuit
    circuit = cirq.Circuit()
    
    # (a) Put data_qubits into uniform superposition
    circuit.append(cirq.H.on_each(*data_qubits))
    
    # (b) Repeat Mark + Diffuse
    for _ in range(num_iterations):
        circuit += build_oracle_mark_data_qubits(data_qubits, S_n)
        circuit += build_grover_diffusion(data_qubits)
    
    # (c) Measure all
    circuit.append(cirq.measure(*data_qubits, key='m'))
    
    # 3) Simulate with qsim
    simulator = qsimcirq.QSimSimulator()
    result = simulator.run(circuit, repetitions=repetitions)
    histogram = result.histogram(key='m')
    
    return circuit, histogram


# TEST FUNCTIONS, I.E. INPUTS INTO MAIN: S_n and number of iterations
def main():
    # Pick some number of elements for S_n
    S_n = [5,15,23,45,67,87]

    #Specificy number of Grover iterations
    for num_iter in [0,1,2,3,4,5,6,7,8,9,10]:
        print(f"=== Grover with num_iterations={num_iter} ===")
        circ, hist = run_grover_7qubits(S_n, num_iterations=num_iter, repetitions=512)
        
        # Tally how many times we got the marked states:
        sum_marked = sum(hist[x] for x in S_n if x in hist)
        sum_unmarked = sum(hist[x] for x in hist if x not in S_n)
        
        print(f"Marked states counts: {sum_marked} out of 512 shots.")
        print(f"Sum of unmarked states: {sum_unmarked}.")
        
        # Possibly show the top few in the distribution
        top_items = sorted(hist.items(), key=lambda x: x[1], reverse=True)[:5]
        print("Histogram top few:", top_items)
        print()

if __name__ == '__main__':
    main()
