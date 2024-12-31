####################################################################################################
#  Single-circuit for: 
#    - Grover membership of S_n 
#    - Threshold check f(s_i) 
#    - Deutsch–Jozsa to see if outputs are constant or not
#
#  NOTE: This test version of the code monolithically and conceptually combines all three functions.
#  See documentation throughout the code re conceptual 'short cuts' and approximations taken  
#####################################################################################################

import cirq
import qsimcirq
import numpy as np

def make_uniform_superposition(system_qubits):
    """
    Creates gates that put all `system_qubits` in a uniform superposition.
    """
    circuit = cirq.Circuit()
    for q in system_qubits:
        circuit.append(cirq.H(q))
    return circuit

def grover_mark_oracle(system_qubits, ancilla, S_n):
    """
    Marks (phase-flips) the states in S_n. 
    For demonstration, S_n is a list of decimal ints in [0..127].
    
    We'll do a simple multi-controlled Z for each pattern in S_n. 
    (In a real design, you might do more optimal circuit constructions.)
    """
    circuit = cirq.Circuit()
    n = len(system_qubits)
    
    for pattern in S_n:
        bin_str = format(pattern, '0{}b'.format(n))  # e.g. '1010101'
        # For each state in S_n, we do controlled phase flip: (-1) if the qubits match that state
        ops = []
        # Flip any qubits that are '0'
        for i, bit in enumerate(bin_str):
            if bit == '0':
                ops.append(cirq.X(system_qubits[i]))
        # Multi-controlled Z on ancilla
        # We'll do a Z on the ancilla, controlled by all system_qubits
        # Then we do X on ancilla to map that phase to an overall phase flip
        ops.append(cirq.X(ancilla))  # put ancilla in |1> so cphase can flip global phase
        ops.append(cirq.Z(ancilla).controlled_by(*system_qubits))
        ops.append(cirq.X(ancilla))
        # Unflip those '0' bits
        for i, bit in enumerate(bin_str):
            if bit == '0':
                ops.append(cirq.X(system_qubits[i]))

        circuit.append(ops)

    return circuit

def grover_diffusion(system_qubits):
    """
    Standard Grover diffusion: apply H, then X, multi-controlled Z, then X, then H.
    We'll do a single multi-controlled Z around the all-zero state.
    
    For the 7-qubit case, that's a big multi-controlled Z. For demonstration.
    """
    circuit = cirq.Circuit()
    n = len(system_qubits)
    # Step 1: H on all qubits
    for q in system_qubits:
        circuit.append(cirq.H(q))
    # Step 2: X on all qubits
    for q in system_qubits:
        circuit.append(cirq.X(q))
    # Step 3: multi-controlled Z on all
    circuit.append(cirq.Z(system_qubits[-1]).controlled_by(*system_qubits[:-1]))
    # Step 4: X on all qubits
    for q in system_qubits:
        circuit.append(cirq.X(q))
    # Step 5: H on all qubits
    for q in system_qubits:
        circuit.append(cirq.H(q))
    return circuit

def threshold_check(system_qubits, threshold_qubits, ancilla_eval, S_n, threshold_val):
    """
    Conceptual 'threshold check' as a binary comparison of system_qubits vs threshold_qubits.
    - If the decimal pattern is in S_n, compare: if system_qubits >= threshold -> flip ancilla_eval
    - If it's not in S_n, do nothing here (or do a controlled assignment of 0 or 1).
    
    Do a multi-controlled operation that checks membership in S_n, 
    then does the comparison if in S_n.
    
    Simplification: Do the comparison for *all* states (like a normal circuit),
    but we imagine that the "Grover marking" ancilla or some other ancilla can condition 
    whether or not we *apply* the threshold check. 
    """
    circuit = cirq.Circuit()
    n = len(system_qubits)
    
    # Store threshold in threshold_qubits, e.g. threshold_val = decimal
    # Prepare them in state = threshold_val
    # (in a real circuit a separate circuit would load the constant)
    
    # Define a subroutine that does: if system_qubits >= threshold => flip ancilla_eval
    # For demonstration here, do a naive bitwise approach:
    # from MSB to LSB:
    #   - If system_qubits bit is 1 and threshold bit is 0 => done => flip ancilla
    #   - If system_qubits bit is 0 and threshold bit is 1 => done => do nothing
    #   - else continue
    #
    # Not a minimal gate count, but a conceptual placeholder.
    #
    # Do controlled phase flips or toggles. 
    # Here, just do a single "≥ threshold_val" with a big if-check in python,
    # then apply or skip a flip. In a real circuit, need to do it with controlled gates. 
    
    # Concept demonstration: For each possible system state x in [0..127], 
    #   if x >= threshold_val => phase flip.
    #Replicate the idea of build_oracle type code from the simpler example.
    
    # Do a multi-controlled Z on ancilla_eval for each x >= threshold_val.
    for x in range(2**n):
        if x >= threshold_val and (x in S_n):
            bin_str = format(x, f'0{n}b')
            ops = []
            # Flip '0' bits
            for i, bit in enumerate(bin_str):
                if bit == '0':
                    ops.append(cirq.X(system_qubits[i]))
            # Now controlled-Z
            ops.append(cirq.Z(ancilla_eval).controlled_by(*system_qubits))
            # Unflip '0' bits
            for i, bit in enumerate(bin_str):
                if bit == '0':
                    ops.append(cirq.X(system_qubits[i]))
            circuit.append(ops)
    
    return circuit

def deutsch_jozsa_assign_complement(system_qubits, ancilla_dj, S_n, assign_val):
    """
    For states not in S_n, we force them to f=assign_val (0 or 1). 
    That means do a phase flip if assign_val=1, do nothing if assign_val=0, 
    and for states in S_n we phase flip if ancilla_eval is 1. 
    Treat ancilla_dj like a measurement qubit that gets the final 'constant or not' readout.
    
    Realistically, need to store the f(s_i) in some ancilla (like ancilla_eval) 
    and then do a "controlled phase flip" on ancilla_dj or the system qubits. 
    For demonstration, let's approximate it similarly to the build_oracle approach. 
    """
    circuit = cirq.Circuit()
    n = len(system_qubits)
    
    # For each possible x in 0..127:
    #   if x in S_n => do a phase flip if ancilla_eval was 1
    #   if x not in S_n => do a phase flip if assign_val=1
    #
    # We'll assume we have "ancilla_eval" storing "1" if f(x)=1, "0" if f(x)=0, 
    # but that itself requires additional logic. 
    # For demonstration, let's do exactly the approach from the simpler example:
    #   - If x in S_n: we look up f(x) in some classical dictionary. 
    #   - If x in S_n^c: f(x) = assign_val. 
    # Then do a multi-controlled Z on ancilla_dj if f(x)=1.
    
    # We can't easily read out the ancilla_eval from threshold_check above 
    # because that is within the same circuit. 
    # So let's just replicate the logic in python: if x in S_n => we do the threshold logic 
    #   (like f(x)=1 if x >= threshold, else 0),
    # if x in S_n^c => f(x)=assign_val
    
    # We'll define a quick function:
    def f_sx(x):
        # If x in S_n, we do threshold in python:
        if x in S_n:
            return 1 if x >= THRESHOLD_VAL else 0
        else:
            return assign_val  # forced
    
    for x in range(2**n):
        val = f_sx(x)
        if val == 1:
            bin_str = format(x, f'0{n}b')
            ops = []
            for i, bit in enumerate(bin_str):
                if bit == '0':
                    ops.append(cirq.X(system_qubits[i]))
            # controlled Z on ancilla_dj
            ops.append(cirq.Z(ancilla_dj).controlled_by(*system_qubits))
            for i, bit in enumerate(bin_str):
                if bit == '0':
                    ops.append(cirq.X(system_qubits[i]))
            circuit.append(ops)
    
    return circuit

################################################################################
# Combined Circuit
################################################################################

# INPUT PARAMETERS FOR THE NETWORK AND DYNAMIC MODEL
# Define a small S_n for demonstration
S_n_demo = [13, 78, 99]  # decimal patterns in [0..127] that the network actually realized
THRESHOLD_VAL = 64       # e.g. decimal representation of Sigma_T = 0b1000000

def build_full_circuit_run(assign_complement):
    """
    Build a single large circuit that:
    1) Creates uniform superposition over 7 system qubits
    2) Grover marking + diffusion to amplify states in S_n_demo
    3) Threshold check (in principle, for states in S_n_demo)
    4) Deutsch–Jozsa pass that assigns S_n^c -> assign_complement
    5) Final H on system qubits
    6) Measure
    """
    system_qubits = cirq.LineQubit.range(7)
    
    anc_grover = cirq.LineQubit(7)
    anc_dj = cirq.LineQubit(8)
    
    circuit = cirq.Circuit()
    
    # 1) Uniform superposition over system qubits
    circuit += make_uniform_superposition(system_qubits)
    
    # 2) Grover marking + diffusion 
    #    (Note: In a real computation do multiple iterations of oracle+diffusion, 
    #     but only doing 1 cycle for brevity.)
    circuit += grover_mark_oracle(system_qubits, anc_grover, S_n_demo)
    circuit += grover_diffusion(system_qubits)
    
    # 3) Threshold check - conceptually. Sstore the result in anc_dj or anc_grover, 
    #    skip here complicated gating. This is big. We'll do a partial approach:
    circuit += threshold_check(system_qubits, None, anc_grover, S_n_demo, THRESHOLD_VAL)
    
    # 4) Deutsch–Jozsa pass with the assigned complement
    circuit += deutsch_jozsa_assign_complement(system_qubits, anc_dj, S_n_demo, assign_val=assign_complement)
    
    # 5) Final round of H on the 7 system qubits (like standard DJ)
    for q in system_qubits:
        circuit.append(cirq.H(q))
    # (Optionally H on anc_dj if we want the usual DJ pattern for the ancilla too)
    circuit.append(cirq.H(anc_dj))
    
    # 6) Measure everything
    circuit.append(cirq.measure(*system_qubits, anc_grover, anc_dj, key='m'))
    
    return circuit


def main():
    # We will do two runs:
    #  1) assign_complement=0  => states not in S_n are forced to f(x)=0
    #  2) assign_complement=1  => states not in S_n are forced to f(x)=1
    
    qsim_sim = qsimcirq.QSimSimulator()
    
    print("=== RUN 1 (S_n^c => 0) ===")
    circuit_1 = build_full_circuit_run(assign_complement=0)
    print("Circuit 1:\n", circuit_1)
    result_1 = qsim_sim.run(circuit_1, repetitions=512)
    counts_1 = result_1.histogram(key='m')
    print("\nMeasurement histogram (decimal):", counts_1)
    
    print("\n=== RUN 2 (S_n^c => 1) ===")
    circuit_2 = build_full_circuit_run(assign_complement=1)
    print("Circuit 2:\n", circuit_2)
    result_2 = qsim_sim.run(circuit_2, repetitions=512)
    counts_2 = result_2.histogram(key='m')
    print("\nMeasurement histogram (decimal):", counts_2)

if __name__ == '__main__':
    main()
