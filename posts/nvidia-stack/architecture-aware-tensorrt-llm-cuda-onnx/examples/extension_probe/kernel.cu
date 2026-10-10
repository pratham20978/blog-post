#include <c10/cuda/CUDAException.h>
#include <torch/extension.h>

namespace {

__global__ void add_one_kernel(const float* input, float* output, int64_t count) {
    const int64_t index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index < count) {
        output[index] = input[index] + 1.0F;
    }
}

}  // namespace

torch::Tensor add_one_cuda(torch::Tensor input) {
    auto contiguous = input.contiguous();
    auto output = torch::empty_like(contiguous);
    const int threads = 256;
    const int blocks = static_cast<int>((contiguous.numel() + threads - 1) / threads);
    add_one_kernel<<<blocks, threads>>>(
        contiguous.data_ptr<float>(), output.data_ptr<float>(), contiguous.numel());
    C10_CUDA_KERNEL_LAUNCH_CHECK();
    return output;
}
