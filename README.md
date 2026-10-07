# QNN: DependentType Driven QNN

Lean-verified specifications + C++ TMP type-safe interfaces + Qiskit Aer execution.

## Goal

Build large-scale encoding-based QNNs where physical invariants (qubit count = 2^n dimension, unitarity, normalization) are encoded at the type level, so that structurally invalid QNNs fail at compile time.

## Architecture

- **Lean layer**: Formal specs and proofs for qubit–dimension relations, unitarity, normalization, and QNN invariants.
- **C++ TMP layer**: Type-safe wrappers (`Vector<T,N>`, `UnitaryMat<N>`, `QNNLayer<N,P>`) that encode these invariants as template parameters.
- **Python + Qiskit Aer**: pybind11 bindings to run verified QNN cores on statevector simulators and real backends.

## Repository Structure

```
lean/          # Lean 4 specifications and proofs
cpp/           # C++ TMP headers and implementations
python/        # Python bindings and Qiskit integration
docs/          # Learning materials (TMP tutorial, dependent types in C++)
```

## Phase Plan

- **Phase 0**: Project setup, roadmap, and TMP learning texts.
- **Phase 1**: Lean specs for qubit dimension, unitarity, and QNN core.
- **Phase 2**: C++ TMP type-safe vector/matrix/QNN wrappers.
- **Phase 3**: pybind11 + Qiskit Aer integration.
- **Phase 4**: Hardware-aware qubit mapping (faulty qubit avoidance).

## Status

- Repository created.
- Learning roadmap and TMP tutorial plan added.
