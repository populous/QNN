# QLang 타입 규칙: C++ 구현 × Lean 명세·증명 (의존 타입 스타일)

아래는 "**구현은 C++**, **명세와 증명은 Lean**" 원칙을 따라, QLang 의 핵심 타입 규칙 (함수는 오버로드, 데이터는 사이즈로) 을 **C++ 템플릿 메타프로그래밍**과 **Lean 의존 타입**으로 짝지어 정리한 MD 초안입니다.

---

## 1) 설계 원칙

- **데이터는 사이즈로 타입 판별**: 레지스터·게이트의 "크기/아리티"가 타입 인자로 노출.
- **함수는 오버로드로 분기**: 같은 이름의 연산을 인자 타입/값에 따라 분기. C++ 는 템플릿 특수화, Lean 은 패턴/인덱스 분기.
- **컴파일 전 올바름**: Lean 이 명세·불변량을 증명, C++ 는 `static_assert`/SFINAE 로 런타임 전 위반을 타입 오류로 승격.

---

## 2) Lean 명세 (의존 타입)

### 2.1 기본 타입 정의

```lean
-- Nat: 자연수 (큐비트 수, 게이트 아리티)
-- Float: 실수 파라미터 (게이트 각도 등)

inductive Gate : Nat → Type
| fSim  (θ φ : Float) : Gate 2
| rzz   (θ   : Float) : Gate 2
| iswap               : Gate 2

inductive QReg : Nat → Type
| mk {n : Nat} : /* n-qubit storage */ → QReg n

def Circuit : Type := Unit  -- (실제론 회로 IR)
```

- `Gate 2`는 2-큐비트 게이트만 허용. `Gate 3` 생성자는 없으므로 타입 단계에서 아리티 통제.

### 2.2 apply 연산 (크기 일치만 타입 성립)

```lean
def apply {k : Nat} : Gate k → QReg k → Circuit
| _, _, _ => ()  -- (실제론 회로 구성)
```

- 타입 규칙:
  \[
  \frac{g : \text{Gate}\ k \quad r : \text{QReg}\ k}{\text{apply}\ g\ r : \text{Circuit}}
  \]
  k 가 불일치하면 적용 불가 → 타입 오류.

### 2.3 불변량 정리 (증명 예시)

```lean
-- 예: "fSim 은 항상 2-큐비트 게이트다"
theorem fSim_arity (θ φ : Float) :
  (Gate.fSim θ φ : Gate k) → k = 2 := by
  intro h
  cases h
  rfl
```

- 이런 정리는 "파라미터가 무엇이든 fSim 의 아리티는 2"를 보장. C++ 에서 `static_assert(N==2)` 와 대응.

---

## 3) C++ 구현 (템플릿 메타프로그래밍)

### 3.1 게이트/레지스터 타입

```cpp
#include <cstddef>
#include <type_traits>

// k-큐비트 게이트 (k 는 템플릿 인자)
template<std::size_t k>
struct Gate;

// 2-큐비트 게이트 특수화: fSim
template<>
struct Gate<2> {
    double theta;
    double phi;
};

// N-큐비트 레지스터
template<std::size_t N>
struct QReg {
    // 실제 메모리/버퍼는 구현 생략
};
```

- `Gate<2>`와 `Gate<3>`은 서로 다른 타입. `Gate<3>`은 정의되지 않아 인스턴스화 시 오류.

### 3.2 apply 함수 (크기 일치만 인스턴스화)

```cpp
struct Circuit {};

template<std::size_t k>
Circuit apply(Gate<k> g, QReg<k> r) {
    // 실제 회로 구성 로직
    return {};
}
```

- 호출 예:
  ```cpp
  Gate<2> g{1.0, 0.5};
  QReg<2> r;
  auto c = apply(g, r);  // OK

  QReg<3> r3;
  // auto c2 = apply(g, r3);  // 컴파일 오류: k 불일치
  ```
- 이는 Lean 의 `apply {k} : Gate k → QReg k → Circuit`과 1:1 대응.

### 3.3 정적 조건 (static_assert)

```cpp
template<std::size_t N>
void require_2qubit() {
    static_assert(N == 2, "2-qubit only");
}
```

- Lean 정리 `fSim_arity`가 "fSim 은 항상 2"를 증명한 것과 동일하게, C++ 는 `static_assert` 로 컴파일 전 위반 포착.

---

## 4) C++ ↔ Lean 대응표

| 개념 | Lean (명세·증명) | C++ (구현) |
|------|------------------|------------|
| 레지스터 타입 | `QReg : Nat → Type` | `template<std::size_t N> struct QReg;` |
| 게이트 타입 | `Gate : Nat → Type` | `template<std::size_t k> struct Gate;` |
| apply 연산 | `apply {k} : Gate k → QReg k → Circuit` | `template<std::size_t k> Circuit apply(Gate<k>, QReg<k>);` |
| 아리티 증명 | `fSim_arity : k = 2` | `static_assert(N == 2, ...)` |
| 타입 오류 조건 | k 불일치 시 타입 성립 불가 | k 불일치 시 템플릿 인스턴스화 실패 (SFINAE) |

---

## 5) 확장: QMonad 문맥 (불변량 증명을 타입으로)

### Lean (의사)

```lean
inductive EntPreserved : Circuit → Type
| ok {c} (h : preservesEntanglement c) : EntPreserved c

def runQ (c : Circuit) (p : EntPreserved c) : Result := ...
```

- `runQ`는 `EntPreserved c` 증명이 있을 때만 타입이 성립.

### C++ 대응 (의사)

```cpp
template<typename Circuit>
requires EntanglementPreserved<Circuit>  // C++20 concepts 스타일
Result runQ(Circuit c);
```

- Lean 증명을 C++ concepts/traits 로 매핑하여 "증명된 불변량만 실행 허용"을 구현.

---

## 6) 사용 예시 (종단 간 흐름)

1. **Lean 에서 명세**: `Gate`, `QReg`, `apply` 타입 정의 + `fSim_arity` 같은 정리 증명.
2. **C++ 에서 구현**: 템플릿 시그니처를 Lean 명세와 맞추어 작성. `static_assert`/SFINAE 로 동일 제약 강제.
3. **검증**: Lean 증명이 "k=2 만 허용"을 보이면, C++ 에서 `Gate<2>` 외 호출은 컴파일 오류.
4. **실행**: 검증된 회로를 Qiskit/OpenQASM/NWQ-Sim 백엔드로 내보내어 실행.

---

이 MD 를 베이스로 실제 Lean 프로젝트 (.lean) 와 C++ 헤더 (.hpp) 를 짝지어 작성하면, "명세는 Lean 이 증명, 구현은 C++ 이 실행"하는 QLang 코어 타입 시스템을 구체화할 수 있습니다.
