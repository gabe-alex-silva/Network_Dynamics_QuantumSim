import cirq
import qsimcirq
import matplotlib.pyplot as plt

def build_deutsch_jozsa_constant(qubits, ancilla):
    """
    Constructs the Deutsch–Jozsa oracle for a constant function f(x) = 1.
    Oracle flips the phase of the ancilla qubit for all inputs.
    """
    circuit = cirq.Circuit()
    
    # Since f(x) = 1 for all x, apply a Z gate to the ancilla qubit.
    # This introduces a global phase flip for all basis states.
    circuit.append(cirq.Z(ancilla))
    
    return circuit

def deutsch_jozsa_constant_function():
    """
    Executes the Deutsch–Jozsa algorithm to test for a constant function f(x) = 1.
    """
    # Define qubits: 7 system qubits and 1 ancilla qubit
    system_qubits = cirq.LineQubit.range(7)
    ancilla = cirq.LineQubit(7)
    
    circuit = cirq.Circuit()
    
    # Step 1: Initialize ancilla qubit to |1>
    circuit.append(cirq.X(ancilla))
    
    # Step 2: Apply Hadamard gates to all qubits
    circuit.append(cirq.H.on_each(*system_qubits))
    circuit.append(cirq.H(ancilla))
    
    # Step 3: Apply the Deutsch–Jozsa oracle for f(x) = 1
    oracle = build_deutsch_jozsa_constant(system_qubits, ancilla)
    circuit += oracle
    
    # Step 4: Apply Hadamard gates to all system qubits again
    circuit.append(cirq.H.on_each(*system_qubits))
    circuit.append(cirq.H(ancilla))
    
    # Step 5: Measure all qubits
    circuit.append(cirq.measure(*system_qubits, ancilla, key='m'))
    
    print("=== Deutsch–Jozsa Algorithm: Constant Function f(x) = 1 ===")
    print("Circuit:")
    print(circuit)
    
    # Initialize simulator
    sim = qsimcirq.QSimSimulator()
    
    # Run simulation
    result = sim.run(circuit, repetitions=1024)
    
    # Extract histogram
    counts = result.histogram(key='m')
    
    print("\nMeasurement histogram (decimal):", counts)
    
    # Plot the histogram
    plot_histogram(counts, "Deutsch–Jozsa Measurement Histogram (Constant Function)")
    
    # Interpretation
    if len(counts) == 1 and 0 in counts:
        print("\nResult: Function is constant as expected.")
    else:
        print("\nResult: Function is not identified as constant. Check the oracle implementation.")

def plot_histogram(hist, title):
    """
    Plots a histogram of measurement results.
    """
    keys = sorted(hist.keys())
    values = [hist[k] for k in keys]
    plt.figure(figsize=(12, 6))
    plt.bar(keys, values, color='skyblue')
    plt.title(title)
    plt.xlabel('Measurement Outcome (Decimal)')
    plt.ylabel('Counts')
    plt.xticks(keys)  # To show all outcome labels
    plt.show()

if __name__ == "__main__":
    deutsch_jozsa_constant_function()
