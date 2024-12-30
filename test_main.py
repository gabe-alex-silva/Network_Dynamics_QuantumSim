import unittest
from grover import build_grover_marking, build_grover_diffusion
from deutsch_josza import classical_threshold_assignment

class TestQuantumCircuits(unittest.TestCase):
    def test_grover_marking(self):
        # Test if the Grover marking circuit is built without errors
        data_qubits = [cirq.LineQubit(i) for i in range(7)]
        ancilla = cirq.LineQubit(7)
        S_n = [5, 12, 99, 100] # The number and values of members in S_n are arbitrarily chosen. Replace as desired
        circuit = build_grover_marking(data_qubits, ancilla, S_n)
        self.assertIsInstance(circuit, cirq.Circuit)
        self.assertEqual(len(circuit.all_operations()), 4 * len(S_n))  # Each marked state adds 4 operations

    def test_grover_diffusion(self):
        # Test if the Grover diffusion circuit is built without errors
        data_qubits = [cirq.LineQubit(i) for i in range(7)]
        circuit = build_grover_diffusion(data_qubits)
        self.assertIsInstance(circuit, cirq.Circuit)
        expected_ops = 2 * len(data_qubits) + 1  # H, X, controlled Z, X, H
        self.assertEqual(len(circuit.all_operations()), expected_ops)

    def test_classical_threshold_assignment(self):
        # Test if the threshold assignment works correctly
        S_n = [5, 12, 99, 100]
        Sigma_T = 50
        threshold_dict = classical_threshold_assignment(S_n, Sigma_T)
        expected = {5: 0, 12: 0, 99: 1, 100: 1}
        self.assertEqual(threshold_dict, expected)

if __name__ == '__main__':
    unittest.main()
