from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension


setup(
    name="arch_probe_extension",
    ext_modules=[
        CUDAExtension(
            name="arch_probe_extension",
            sources=["binding.cpp", "kernel.cu"],
            extra_compile_args={"cxx": ["-O2"], "nvcc": ["-O2"]},
        )
    ],
    cmdclass={"build_ext": BuildExtension},
)
