# fSim 기반 QRNG 4-단계 Workflow

## 개요

QNN 아키텍처의 4-단계 실행 파이프라인을 fSim 기반 완전그래프 QRNG 로 구현하는 예시.

## 4-단계 Workflow

### Phase 1: Lean 명세·검증

**목표**: fSim 게이트와 QRNG 회로의 수학적 성질 검증

- `fSimGate : UnitaryMat 2` — 2-큐비트 fSim 게이트가 유니터리임 증명
- `QRNGCircuit n m` — n 큐비트, m 개 fSim 게이트로 구성된 회로
- `is_unitary_circuit` — 전체 회로가 유니터리임 검증
- `qrng_uniformity` — 출력 분포가 균일 분포에 가까움 정리

**파일**: `lean/QRNGCore.lean` (신규)

### Phase 2: C++ TMP 타입 안전 구현

**목표**: Lean 명세를 C++ 템플릿으로 타입 안전 래핑

- `fSimGate<N>(params, q1, q2)` — N 큐비트 시스템에서 fSim 게이트 구현
- `composeQRNG<N,M>(params)` — M 개 fSim 게이트 합성
- `sampleQRNG<N,M>(params, shots)` — QRNG 샘플링 함수
- 템플릿 인자 `N`, `M`으로 차원·게이트 수 컴파일 타임 검증

**파일**: `cpp/fsim_qrng.hpp` (신규)

### Phase 3: Python + Qiskit 실행

**목표**: 검증된 QRNG 를 Qiskit 으로 실행

- `build_fsim_qrng(n, params)` — Qiskit 회로 구성
- `run_qrng(backend, shots)` — Aer 또는 실제 백엔드에서 실행
- `extract_lehmer_code(counts)` — 측정 결과에서 Lehmer Code 추출

**파일**: `python/fsim_qrng.py` (신규)

### Phase 4: HW Fault-Aware Mapping

**목표**: 실제 백엔드의 faulty qubit 을 회피한 실행

- `fault_aware_qrng_mapping(backend, circuit)` — faulty 회피 layout
- `transpile_with_swap_insertion(...)` — SWAP 기반 라우팅
- `report_faulty_avoidance(...)` — 회피 보고서 생성

**파일**: `python/fsim_qrng_fault_aware.py` (신규)

## fSim 완전그래프 + Lehmer Code QRNG

### fSim 완전그래프

- n 큐비트 시스템에서 **모든 큐비트 쌍**에 fSim 게이트 적용
- 총 `n*(n-1)/2` 개의 fSim 게이트로 **완전 연결 그래프** 형성
- 각 fSim 게이트는 `(θᵢⱼ, φᵢⱼ)` 파라미터를 가짐

### Lehmer Code 기반 난수 추출

- 측정 결과 `|x₁x₂...xₙ⟩` 에서 **Lehmer Code** 계산
- Lehmer Code: 순열을 정수 인코딩하는 방식
  - `L[i] = #{j > i | xⱼ < xᵢ}`
- Lehmer Code 를 **균일 난수**로 변환
  - `random_int = Σ L[i] * (n-i)!`

### 예시: 3-큐비트 QRNG

```
fSim 게이트: (0,1), (0,2), (1,2) — 총 3 개
파라미터: (θ₀₁, φ₀₁), (θ₀₂, φ₀₂), (θ₁₂, φ₁₂)

회로:
|0⟩ ── fSim(θ₀₁,φ₀₁) ── fSim(θ₀₂,φ₀₂) ── M
|0⟩ ── fSim(θ₀₁,φ₀₁) ── fSim(θ₁₂,φ₁₂) ── M
|0⟩ ── fSim(θ₀₂,φ₀₂) ── fSim(θ₁₂,φ₁₂) ── M

측정 결과: |101⟩
Lehmer Code: L = [1, 0, 0]  (101 → 순열 [2,0,1] → Lehmer [1,0,0])
난수: 1*2! + 0*1! + 0*0! = 2
```

## 다음 단계

1. `lean/QRNGCore.lean` 작성 (fSim 게이트, QRNG 명세)
2. `cpp/fsim_qrng.hpp` 작성 (C++ TMP 래퍼)
3. `python/fsim_qrng.py` 작성 (Qiskit 실행)
4. `python/fsim_qrng_fault_aware.py` 작성 (faulty 회피)
5. 전체 파이프라인 통합 테스트
