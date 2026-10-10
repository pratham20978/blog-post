#include <torch/extension.h>

torch::Tensor add_one_cuda(torch::Tensor input);

torch::Tensor add_one(torch::Tensor input) {
    TORCH_CHECK(input.is_cuda(), "input must be a CUDA tensor");
    TORCH_CHECK(input.scalar_type() == torch::kFloat32,
                "input must have dtype float32");
    return add_one_cuda(input);
}

PYBIND11_MODULE(TORCH_EXTENSION_NAME, module) {
    module.def("add_one", &add_one, "Add one with a CUDA kernel");
}
