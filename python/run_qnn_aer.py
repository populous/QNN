# run_qnn_aer.py
import numpy as np
import qiskit_aer
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
# import qnn_aer  # pybind11 모듈 (빌드 후 사용)

def make_encoding_unitary(n: int, x: np.ndarray) -> np.ndarray:
    """
    개념적: x (2^n 실수, 정규화됨) 를 진폭 인코딩하는 유니터리 행렬 반환.
    실제로는 Lean/C++ 에서 계산된 U 를 로드하거나,
    Qiskit 의 Statevector.prepare 로 구성한 뒤 unitary 로 추출.
    """
    dim = 2 ** n
    assert x.shape == (dim,)
    # 여기서는 예시로 |0⟩^n → |ψ_x⟩로 보내는 유니터리를
    # Statevector.prepare 로 구성한다고 가정.
    from qiskit.quantum_info import Statevector
    psi = Statevector(x.astype(complex))
    zero = Statevector.from_label("0" * n)
    # U such that U|0⟩ = psi 는 일반적으로 비유일;
    # 여기서는 간단히 Householder 반사 등으로 구성 가능.
    # 예시 생략: 실제로는 C++ 코어와 동일한 U 를 사용.
    U = np.eye(dim, dtype=complex)  # placeholder
    return U

def make_qnn_layers(n: int, L: int, thetas):
    """
    QNN 층들: 각 층 l 에 대해 theta_l → UnitaryMat<n> 매핑.
    여기서는 예시로 간단한 파라미터화 회전 게이트만 사용.
    """
    dim = 2 ** n
    layers = []
    for l in range(L):
        theta = thetas[l]
        # 예: RY(theta[0]) ⊗ RY(theta[1]) ⊗ ... (n 큐비트)
        # 실제 QNN 설계에 맞게 U_l 구성.
        U = np.eye(dim, dtype=complex)  # placeholder
        layers.append(U.reshape(-1))  # 평탄화
    return layers

def run_qnn_cpp(n: int, P: int, L: int,
                x: np.ndarray,
                thetas):
    """
    C++ QNN 코어 (Lean 검증 + TMP) 호출.
    """
    dim = 2 ** n
    assert x.shape == (dim,)
    assert len(thetas) == L
    assert all(len(t) == P for t in thetas)

    # 진폭 인코딩 유니터리 (실제로는 Lean/C++ 코어와 일치)
    encU = make_encoding_unitary(n, x).reshape(-1)

    layers = make_qnn_layers(n, L, thetas)

    # |0⟩^n 상태
    psi0 = np.zeros(dim, dtype=complex)
    psi0[0] = 1.0

    # C++ QNN 예측 호출 (N=3, P=4, L=2 예시)
    # 여기서는 3q_4p_2l 인스턴스 사용 가정
    if not (n == 3 and P == 4 and L == 2):
        raise NotImplementedError("Only N=3,P=4,L=2 bound in this example")

    # pred = qnn_aer.qnnPredict_3q_4p_2l(
    #     encU.astype(complex),
    #     [U.astype(complex) for U in layers],
    #     psi0.astype(complex),
    #     thetas
    # )
    pred = 0.0  # 스텁
    return pred

def run_qnn_qiskit(n: int, P: int, L: int,
                   x: np.ndarray,
                   thetas,
                   shots: int = 1024):
    """
    같은 QNN 구조를 Qiskit Aer(statevector) 로 시뮬레이션.
    """
    dim = 2 ** n
    assert x.shape == (dim,)

    # 인코딩 회로: x 를 진폭 인코딩
    from qiskit.quantum_info import Statevector
    psi_target = Statevector(x.astype(complex))
    # |0⟩^n → |ψ_x⟩로 보내는 회로 (개념적)
    circ = QuantumCircuit(n)
    circ.initialize(x.astype(complex), range(n))

    # QNN 층: 각 층 l 에 대해 파라미터화 게이트 적용
    for l in range(L):
        theta = thetas[l]
        # 예: 각 큐비트에 RY(theta[i]) 적용
        for i in range(n):
            circ.ry(theta[i % P], i)
        # 더 복잡한 엔탱글링 층은 여기에 추가

    # 측정: 첫 큐비트 Z 기대값 추정을 위해
    circ.measure_all()

    # Aer statevector + shots
    sim = AerSimulator(method="statevector")
    tcirc = transpile(circ, sim)
    job = sim.run(tcirc, shots=shots)
    result = job.result()
    counts = result.get_counts()

    # 첫 큐비트 Z 기대값 추정
    exp_z = 0.0
    total = sum(counts.values())
    for outcome, cnt in counts.items():
        bit = outcome[-1] if len(outcome) > 0 else "0"
        val = 1.0 if bit == "0" else -1.0
        exp_z += val * cnt / total
    return exp_z

if __name__ == "__main__":
    n = 3
    P = 4
    L = 2

    # 정규화된 입력 데이터 (2^n 차원)
    dim = 2 ** n
    x = np.random.randn(dim)
    x /= np.linalg.norm(x)

    # 파라미터 (L x P)
    thetas = np.random.randn(L, P).tolist()

    pred_cpp = run_qnn_cpp(n, P, L, x, thetas)
    pred_qiskit = run_qnn_qiskit(n, P, L, x, thetas, shots=4096)

    print("C++ QNN prediction (stub):", pred_cpp)
    print("Qiskit Aer Z expectation:", pred_qiskit)
