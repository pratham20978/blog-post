# Benchmark report — fill from measured output only

## Reproducibility tuple

| Field | Recorded value |
|---|---|
| Timestamp and timezone | |
| Host CPU architecture / OS | |
| GPU name, count, compute capability | |
| NVIDIA driver | |
| CUDA Toolkit (`nvcc`) | |
| Container digest or environment lockfile | |
| PyTorch version and CUDA build | |
| TensorRT-LLM version / commit | |
| Model repository and immutable revision | |
| Weight and KV-cache precision | |
| Tensor/pipeline/expert parallelism | |
| Input-token distribution | |
| Requested output-token distribution | |
| Request count / rate / concurrency | |
| Streaming | |
| Warm-up policy | |
| KV-cache memory fraction | |

## Results

| Metric | Unit | p50 | p90 | p99 | Mean |
|---|---:|---:|---:|---:|---:|
| Time to first token | ms | | | | |
| Inter-token latency / TPOT | ms/token | | | | |
| End-to-end request latency | ms | | | | |

| Aggregate metric | Value |
|---|---:|
| Output token throughput (tokens/s) | |
| Total token throughput (tokens/s) | |
| Completed requests | |
| Failed requests | |
| Peak GPU memory (MiB) | |

## Notes

- Record throttling, fallback-kernel warnings, OOM retries, and server errors.
- Do not compare rows produced with different model revisions or workloads as if
  they isolated a hardware or runtime change.
