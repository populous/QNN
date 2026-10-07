#pragma once
#include <array>
#include <complex>
#include <cstdint>
#include <stdexcept>

using Cplx = std::complex<double>;

// n 큐비트 차원: 2^n (컴파일 타임 계산)
template <std::size_t N>
struct QubitDim {
    static constexpr std::size_t value = (std::size_t(1) << N);
};

// n 큐비트 상태 벡터 타입
template <std::size_t N>
using StateVec = std::array<Cplx, QubitDim<N>::value>;

// n 큐비트 유니터리 행렬 타입
template <std::size_t N>
using UnitaryMat = std::array<Cplx, QubitDim<N>::value * QubitDim<N>::value>;

// QNN 층: n 큐비트, p 개 파라미터
template <std::size_t N, std::size_t P>
struct QNNLayer {
    // 각 theta 벡터에 대해 유니터리 행렬을 반환하는 함수 포인터
    using ApplyFn = UnitaryMat<N> (*)(const std::array<double, P>&);
    ApplyFn apply;
};

// 전체 QNN: L 개의 층
template <std::size_t N, std::size_t P, std::size_t L>
using QNN = std::array<QNNLayer<N, P>, L>;

// 진폭 인코딩 구조 (런타임 데이터 + 타입 불변량)
template <std::size_t N>
struct AmplitudeEncoding {
    UnitaryMat<N> U;
    // 추가: is_unitary, is_normalized 증명은 런타임 어설션 또는
    //      Lean 측에서 이미 검증되었다고 가정
};

// QNN 예측 래퍼: 타입 레벨에서 n, p, L 고정
template <std::size_t N, std::size_t P, std::size_t L>
double qnnPredict(
    const AmplitudeEncoding<N>& enc,
    const QNN<N, P, L>& qnn,
    const std::array<std::array<double, P>, L>& thetas,
    const StateVec<N>& psi0
) {
    // 차원 상수
    constexpr std::size_t DIM = QubitDim<N>::value;

    // layers 를 평탄화: L * DIM * DIM
    std::array<Cplx, L * DIM * DIM> layersFlat{};
    for (std::size_t l = 0; l < L; ++l) {
        auto U = qnn[l].apply(thetas[l]);
        for (std::size_t i = 0; i < DIM * DIM; ++i) {
            layersFlat[l * DIM * DIM + i] = U[i];
        }
    }

    // 실제 연산은 Lean export 함수 호출 (스텁: 여기서는 0.0 반환)
    // return lean_qnn_predict(N, P, L, enc.U.data(), layersFlat.data(), psi0.data(), DIM);
    (void)enc; (void)layersFlat; (void)psi0;
    return 0.0;
}
