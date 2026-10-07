#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <vector>
#include <complex>
#include "qnn_tmp.hpp"

namespace py = pybind11;
using Cplx = std::complex<double>;

// StateVec<N>을 numpy array 로 변환 (개념적)
template <std::size_t N>
py::array_t<std::complex<double>> stateVecToNumpy(const StateVec<N>& v) {
    constexpr std::size_t DIM = QubitDim<N>::value;
    auto arr = py::array_t<std::complex<double>>(DIM);
    auto buf = arr.mutable_unchecked<1>();
    for (std::size_t i = 0; i < DIM; ++i) {
        buf(i) = v[i];
    }
    return arr;
}

// numpy array 를 StateVec<N> 으로 변환
template <std::size_t N>
StateVec<N> numpyToStateVec(const py::array_t<std::complex<double>>& arr) {
    constexpr std::size_t DIM = QubitDim<N>::value;
    if (arr.size() != static_cast<ssize_t>(DIM)) {
        throw std::invalid_argument("statevector dimension mismatch");
    }
    auto buf = arr.unchecked<1>();
    StateVec<N> v{};
    for (std::size_t i = 0; i < DIM; ++i) {
        v[i] = buf(i);
    }
    return v;
}

// QNN 예측 래퍼: Python 에서 (encU, layers, psi0, thetas) 받아 C++ QNN 호출
template <std::size_t N, std::size_t P, std::size_t L>
double qnnPredictPython(
    const py::array_t<std::complex<double>>& encU,   // (2^n)*(2^n)
    const std::vector<py::array_t<std::complex<double>>>& layers, // L 장
    const py::array_t<std::complex<double>>& psi0,   // 2^n
    const std::vector<std::vector<double>>& thetas   // L x P
) {
    constexpr std::size_t DIM = QubitDim<N>::value;

    if (encU.size() != static_cast<ssize_t>(DIM * DIM)) {
        throw std::invalid_argument("encU dimension mismatch");
    }
    if (layers.size() != L) {
        throw std::invalid_argument("layers count mismatch");
    }
    if (psi0.size() != static_cast<ssize_t>(DIM)) {
        throw std::invalid_argument("psi0 dimension mismatch");
    }

    // encU, layers, psi0 를 C++ 구조체로 복사 (스텁: 실제 연산은 생략)
    AmplitudeEncoding<N> enc{};
    {
        auto buf = encU.unchecked<1>();
        for (std::size_t i = 0; i < DIM * DIM; ++i) {
            enc.U[i] = buf(i);
        }
    }

    QNN<N, P, L> qnn{};
    // 여기서는 layers[l] 을 UnitaryMat<N> 로 해석하고,
    // QNNLayer::apply 를 단순 래퍼로 구현했다고 가정.

    auto psi0_cpp = numpyToStateVec<N>(psi0);

    // thetas 를 std::array<std::array<double,P>,L> 로 변환
    std::array<std::array<double, P>, L> thetasArr{};
    for (std::size_t l = 0; l < L; ++l) {
        for (std::size_t p = 0; p < P; ++p) {
            thetasArr[l][p] = thetas[l][p];
        }
    }

    // 실제 연산 (스텁: 0.0 반환)
    // return qnnPredict<N, P, L>(enc, qnn, thetasArr, psi0_cpp);
    (void)enc; (void)qnn; (void)thetasArr; (void)psi0_cpp;
    return 0.0;
}

// pybind11 모듈 등록: 특정 (N,P,L) 인스턴스만 노출
PYBIND11_MODULE(qnn_aer, m) {
    m.doc() = "QNN with Lean-verified core + C++ TMP + Qiskit Aer interface";

    // 예: 3 큐비트, P=4, L=2 인스턴스
    m.def("qnnPredict_3q_4p_2l",
          &qnnPredictPython<3, 4, 2>,
          py::arg("encU"),
          py::arg("layers"),
          py::arg("psi0"),
          py::arg("thetas"),
          "Run QNN prediction for N=3, P=4, L=2");

    // 필요시 다른 (N,P,L) 조합도 추가:
    // m.def("qnnPredict_4q_8p_3l", &qnnPredictPython<4, 8, 3>, ...);
}
