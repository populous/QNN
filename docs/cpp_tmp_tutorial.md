# C++ TMP 학습 튜토리얼

## 00. Introduction

- TMP = 컴파일 타임에 타입·값을 계산하는 프로그래밍
- 목적: 런타임 오버헤드 제거, 타입 안전성, 불변량 인코딩
- Lean/Idris 의존 타입과의 비교

## 01. Basics Templates

- 타입/비타입 파라미터
- `std::array<T, N>` 예시

```cpp
template <typename T, std::size_t N>
struct Vector {
    std::array<T, N> data;
    static constexpr std::size_t size() noexcept { return N; }
};
```

## 02. Type Traits

- `std::is_integral`, `std::conditional_t`
- 타입 속성 조회·변환

## 03. Alias Templates

- `using Name = ...` 로 타입 함수 표현

## 04. SFINAE / enable_if

- 타입 기반 분기

## 05. C++20 Concepts

- `concept`, `requires`
- `std::integral`, `NonEmptyVector`

## 06. constexpr / consteval

- 컴파일 타임 계산
- `if constexpr` 분기

## 07. Modern TMP Patterns

- CRTP, tag dispatch, policy-based design

## 08. Type Mapper Strategies

- `std::type_identity`, alias mapper

## 09. Safe Indexing

- `static_assert` 범위 체크

## 10. Dependent Style in C++

- 크기·범위·불변량 타입 인코딩 종합

## 11. QNN HW-Aware TMP

- `QubitSpace<N>`, `StateVec` 타입
