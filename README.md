# Network_Dynamics_QuantumSim
Cirq python library quantum simulation to test if a neural network model can sustain inherent dynamic activity beyond some arbitrary observation time or if the activity ceases through quiescence or saturation via an ’epileptic’-like state. 


## Overview

This repository contains code for simulating a quantum circuit that integrates Grover's algorithm, thresholding, and the Deutsch–Jozsa algorithm using [Cirq](https://quantumai.google/cirq) and [qsim](https://github.com/quantumlib/qsim). The simulation aims to identify specific quantum states, apply a threshold comparison, and determine whether the network of nodes is quiescent, epileptic, or mixed based on the results.

## Features

- **Grover's Algorithm**: Identifies and amplifies marked quantum states within a 7-qubit system.
- **Threshold Comparator**: Applies a classical threshold to determine binary outcomes based on quantum states.
- **Deutsch–Jozsa Algorithm**: Evaluates whether a function is constant or balanced across the quantum states.
- **Modular Design**: Separate modules for Grover's algorithm, Deutsch–Jozsa, and utility functions.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gabe-alex-silva/Network_Dynamics_QuantumSim.git

## Related arXiv paper
See https://arxiv.org/abs/2403.18963 for full theoretical details, test example constructions, circuit design, and the relevance of the notation used in this code. 

Gabriel A. Silva
- University of California San Diego
- gsilva@ucsd.edu

