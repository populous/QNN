#include "qnn_tmp.hpp"
#include <array>
#include <iostream>

int main() {
    constexpr std::size_t N = 3;  // 3 큐비트
    constexpr std::size_t P = 4;  // 층당 파라미터 4 개
    constexpr std::size_t L = 2;  // 2 층 QNN

    using Vec3 = StateVec<N>;
    using Mat3 = UnitaryMat<N>;

    // |0⟩^⊗3 상태 (개념적 초기화)
    Vec3 psi0{};
    psi0[0] = Cplx(1.0, 0.0);  // |000⟩

    // 진폭 인코딩 (실제로는 Lean 에서 계산/검증된 U 를 로드)
    AmplitudeEncoding<N> enc{};
    // enc.U = ... (2^3 × 2^3 유니터리)

    // QNN 층 정의 (개념적)
    QNN<N, P, L> qnn{};
    // qnn[l].apply = ... (theta → UnitaryMat<N>)

    // 파라미터
    std::array<std::array<double, P>, L> thetas{};

    double result = qnnPredict<N, P, L>(enc, qnn, thetas, psi0);

    std::cout << "QNN prediction (stub): " << result << std::endl;

    // 차원 불일치 예시 (컴파일 에러):
    // StateVec<4> bad_psi0{};  // N=4 는 N=3 과 다른 타입
    // qnnPredict<N, P, L>(enc, qnn, thetas, bad_psi0);  // compile error

    return 0;
}
