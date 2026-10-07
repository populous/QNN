cmake_minimum_required(VERSION 3.18)
project(qnn_tmp_example)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# pybind11 찾기
find_package(pybind11 CONFIG REQUIRED)

# qnn_tmp 헤더만 사용하는 예제
add_executable(qnn_example main.cpp)
target_include_directories(qnn_example PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# pybind11 모듈
pybind11_add_module(qnn_aer qnn_python.cpp)
target_include_directories(qnn_aer PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# 향후 Lean export 라이브러리 링크 시 여기에 추가
# find_package(Lean4 REQUIRED)
# target_link_libraries(qnn_aer PRIVATE Lean4::Lean)
