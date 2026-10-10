import torch

import arch_probe_extension


x = torch.tensor([1.0, 2.0, 3.0], device="cuda")
y = arch_probe_extension.add_one(x)
torch.cuda.synchronize()
torch.testing.assert_close(y.cpu(), torch.tensor([2.0, 3.0, 4.0]))
print("extension probe: pass")
