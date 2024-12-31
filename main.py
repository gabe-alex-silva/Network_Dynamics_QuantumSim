# ============================
# main.py 
# ============================
def main_demo_run():
    # S_n: some set of 7-bit patterns
    S_n = [20, 27, 29, 55]
    print("=== Values of S_n in this run =", S_n, "===")
    
    # Step 1: GROVER to identify/amplify states in S_n
    # Choose # of iterations (try 2..5 for demonstration)
    num_grover_iterations = 3
    grover_circ, hist_data, hist_anc = run_grover_search_on_7qubits_with_ancilla(
        S_n, num_iterations=num_grover_iterations, repetitions=512
    )
    print("\n--- Grover Phase ---")
    print("Grover circuit (truncated to 30 lines):")
    print(str(grover_circ)[:1000], "...")  # just not to overflow
    
    # Summarize counts for the marked states
    # "hist_data" is a Counter, we can do:
    total_marked_counts = 0
    for x in S_n:
        c = hist_data[x]
        total_marked_counts += c
        print(f"State {x} => {c} counts")
    print(f"Sum of marked states: {total_marked_counts}\n")
    
    # Step 2: threshold assignment
    # Suppose threshold=20 => any x >= 20 => 1, else => 0
    Sigma_T = 15
    print("=== The value of the threshold Sigma_T in this run =", Sigma_T, "===")
    threshold_dict = classical_threshold_assignment(S_n, Sigma_T)
    print("--- Threshold assignment ---")
    for x in S_n:
        print(f"x={x}, threshold => {threshold_dict[x]}")
    
    # Step 3: DEUTSCH–JOSZA
    #   (a) assign_complement=0 => states not in S_n forced to 0
    circ_dj_a, counts_a = run_deutsch_josza_7q(S_n, threshold_dict, assign_complement=0, reps=512)
    print("\n--- Deutsch–Jozsa run #1 (complement=0) ---")
    print("Measurement histogram:", counts_a)
    
    #   (b) assign_complement=1 => states not in S_n forced to 1
    circ_dj_b, counts_b = run_deutsch_josza_7q(S_n, threshold_dict, assign_complement=1, reps=512)
    print("\n--- Deutsch–Jozsa run #2 (complement=1) ---")
    print("Measurement histogram:", counts_b)
    
    print("\nDone.")

# Actually run it:
main_demo_run()
