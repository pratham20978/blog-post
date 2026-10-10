cmake_minimum_required(VERSION 3.24)

project(cuda_arch_probe LANGUAGES CXX)

set(CUDA_TARGETS "" CACHE STRING
    "Required CUDA architectures, for example 75-real or 121-real")

if(CUDA_TARGETS STREQUAL "")
    message(FATAL_ERROR
        "Set -DCUDA_TARGETS=<arch>, for example 75-real or 121-real")
endif()

# Set the architecture before enabling CUDA so compiler identification and
# every target use the same explicit inventory.
set(CMAKE_CUDA_ARCHITECTURES "${CUDA_TARGETS}")
enable_language(CUDA)

add_executable(cuda_arch_probe probe.cu)
set_target_properties(cuda_arch_probe PROPERTIES
    CUDA_ARCHITECTURES "${CUDA_TARGETS}"
    CUDA_STANDARD 17
    CUDA_STANDARD_REQUIRED YES
)

message(STATUS "CUDA compiler: ${CMAKE_CUDA_COMPILER}")
message(STATUS "CUDA targets: ${CUDA_TARGETS}")
