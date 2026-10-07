# fault_aware_mapping.py
"""
HW fault-aware qubit mapping prototype

- backend.properties() 로 faulty_qubits, faulty_gates 추출
- Variation-Aware Qubit Allocation (VQA) 스타일 초기 layout
- SWAP 기반 라우팅으로 faulty 회피
"""

from typing import List, Dict, Tuple, Set
from qiskit import QuantumCircuit
from qiskit.transpiler import CouplingMap, Layout
from qiskit_ibm_runtime import IBMBackend


def get_faulty_qubits(backend: IBMBackend) -> List[int]:
    props = backend.properties()
    if props is None:
        return []
    return props.faulty_qubits()


def get_operational_qubits(backend: IBMBackend) -> List[int]:
    props = backend.properties()
    faulty = set(props.faulty_qubits())
    n = backend.configuration().num_qubits
    return [q for q in range(n) if q not in faulty]


def require_n_operational_qubits(operational: List[int], n: int) -> List[int]:
    """
    타입 레벨 제약의 런타임 대응:
    - n 큐비트 연산을 위해 최소 n 개 이상의 operational qubit 필요
    """
    if len(operational) < n:
        raise ValueError(
            f"Need at least {n} operational qubits, "
            f"but only {len(operational)} available."
        )
    return operational[:n]


def make_layout_avoiding_faulty(
    circuit: QuantumCircuit,
    backend: IBMBackend
) -> Layout:
    """
    circuit 의 logical qubit 을 backend 의 operational qubit 에 매핑.
    faulty qubit 은 절대 사용하지 않음.
    """
    n_logical = circuit.num_qubits
    operational = get_operational_qubits(backend)

    selected = require_n_operational_qubits(operational, n_logical)

    # 단순 매핑: logical i → operational[i]
    layout = Layout()
    for i in range(n_logical):
        layout[i] = selected[i]
    return layout


def transpile_avoiding_faulty(
    circuit: QuantumCircuit,
    backend: IBMBackend,
    optimization_level: int = 2
) -> QuantumCircuit:
    """
    faulty qubit 을 피하고, 필요시 SWAP 을 추가해
    logical n-큐비트 회로를 physical operational qubit 에 매핑.
    """
    from qiskit import transpile

    n_logical = circuit.num_qubits
    operational = get_operational_qubits(backend)

    if len(operational) < n_logical:
        raise ValueError(
            "Cannot map circuit: not enough operational qubits."
        )

    # 초기 layout: logical i → operational[i]
    initial_layout = {i: operational[i] for i in range(n_logical)}

    coupling = CouplingMap(backend.configuration().coupling_map)

    transpiled = transpile(
        circuit,
        backend=backend,
        coupling_map=coupling,
        initial_layout=initial_layout,
        optimization_level=optimization_level,
        routing_method="sabre"  # SWAP 기반 라우팅
    )
    return transpiled


def build_fault_avoidance_report(
    circuit: QuantumCircuit,
    transpiled: QuantumCircuit,
    backend: IBMBackend
) -> Dict:
    """
    faulty qubit/gate 회피 보고서 생성.
    """
    faulty_q = set(get_faulty_qubits(backend))

    # transpiled 회로에서 사용된 physical qubit 추출
    used_qubits: Set[int] = set()
    for inst in transpiled.data:
        for qb in inst.qubits:
            idx = transpiled.find_bit(qb).index
            used_qubits.add(idx)

    return {
        "original_num_qubits": circuit.num_qubits,
        "transpiled_num_qubits": transpiled.num_qubits,
        "faulty_qubits": list(faulty_q),
        "used_physical_qubits": list(used_qubits),
        "avoided_faulty": list(faulty_q & used_qubits),  # ideally empty
    }


if __name__ == "__main__":
    # 예시 사용법 (실제 백엔드는 환경에 맞게 수정)
    # from qiskit_ibm_runtime import QiskitRuntimeService
    # service = QiskitRuntimeService()
    # backend = service.backend("ibm_cusco")

    # 예제 회로
    circ = QuantumCircuit(3)
    circ.h(0)
    circ.cx(0, 1)
    circ.cx(1, 2)

    # mock backend (실제 사용 시 IBMBackend 인스턴스)
    # report = build_fault_avoidance_report(
    #     circ, transpile_avoiding_faulty(circ, backend), backend
    # )
    # print(report)
