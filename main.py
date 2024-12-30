import cirq
import qsimcirq
import numpy as np
from collections import Counter
from grover import run_grover_search_on_7qubits_with_ancilla
from deutsch_josza import run_deutsch_josza_7q, classical_threshold_assignment

def main():
    #----------------------------------------
    # 0) Define the true S_n (marked states)
    #----------------------------------------
    S_n_true = [5, 12, 99, 100]  # 7-bit states that "occur" in our scenario
    print("=== EXAMPLE: S_n_true =", S_n_true, "===\n")
    
    #----------------------------------------
    # 1) RUN GROVER to identify these states
    #----------------------------------------
    grover_circ, hist_data, hist_anc = run_grover_search_on_7qubits_with_ancilla(
        S_n_true, 
        num_iterations=4, 
        repetitions=512
    )
    print("=== GROVER PHASE ===")
    print("Grover circuit:\n", grover_circ)
    
    print("\nGrover measurement (data) histogram:")
    print(hist_data)
    print("\nGrover ancilla measurement histogram:")
    print(hist_anc)
    print("\n(Interpretation: states in S_n_true are hopefully amplified in 'm_data'.)\n")
    
    #----------------------------------------
    # 2) Decide threshold and do classical assignment
    #----------------------------------------
    Sigma_T = 50
    threshold_dict = classical_threshold_assignment(S_n_true, Sigma_T)
    print("Threshold dict (x >= 50 => 1, else 0):")
    print(threshold_dict, "\n")
    
    #----------------------------------------
    # 3) DEUTSCH–JOSZA RUNS
    #----------------------------------------
    
    # (a) assign_complement = 0
    circ1, counts1 = run_deutsch_josza_7q(S_n_true, threshold_dict, assign_complement=0, reps=512)
    print("=== DEUTSCH-JOSZA RUN 1 (S_n^c => 0) ===")
    print("Circuit 1:\n", circ1)
    print("Measurement histogram (decimal):", counts1)
    print()
    
    # (b) assign_complement = 1
    circ2, counts2 = run_deutsch_josza_7q(S_n_true, threshold_dict, assign_complement=1, reps=512)
    print("=== DEUTSCH-JOSZA RUN 2 (S_n^c => 1) ===")
    print("Circuit 2:\n", circ2)
    print("Measurement histogram (decimal):", counts2)
    print()
    
    print("Done.")

if __name__ == "__main__":
    main()
