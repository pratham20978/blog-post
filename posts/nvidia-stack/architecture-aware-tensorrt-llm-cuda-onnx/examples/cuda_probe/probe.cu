#include <cuda_runtime.h>

#include <cstdlib>
#include <iostream>

namespace {

void check(cudaError_t result, const char* operation) {
    if (result != cudaSuccess) {
        std::cerr << operation << ": " << cudaGetErrorString(result) << '\n';
        std::exit(EXIT_FAILURE);
    }
}

__global__ void record_compiled_arch(int* result) {
#ifdef __CUDA_ARCH__
    *result = __CUDA_ARCH__;
#else
    *result = -1;
#endif
}

}  // namespace

int main() {
    int device = 0;
    cudaDeviceProp properties{};
    check(cudaGetDevice(&device), "cudaGetDevice");
    check(cudaGetDeviceProperties(&properties, device), "cudaGetDeviceProperties");

    int* device_result = nullptr;
    int host_result = 0;
    check(cudaMalloc(&device_result, sizeof(int)), "cudaMalloc");
    record_compiled_arch<<<1, 1>>>(device_result);
    check(cudaGetLastError(), "kernel launch");
    check(cudaMemcpy(&host_result, device_result, sizeof(int), cudaMemcpyDeviceToHost),
          "cudaMemcpy");
    check(cudaFree(device_result), "cudaFree");

    std::cout << "device=" << properties.name << '\n'
              << "device_compute_capability=" << properties.major << '.'
              << properties.minor << '\n'
              << "selected_kernel___CUDA_ARCH__=" << host_result << '\n';
}
