# %% after: Run
import json
import subprocess
import sys


def run(*args):
    """Run a lab entry point with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", *args], check=True)  # -u: each stage prints as it runs


run("likelihood.py", "all", "--quick", "--out", "mine.json")  # never overwrite the shipped captures

# %% after: E1
with open("mine.json", encoding="utf-8") as handle:
    mine = json.load(handle)
with open("captures-quick.json", encoding="utf-8") as handle:
    author = json.load(handle)
for name, cap in (("yours", mine), ("author's quick run", author)):
    v1, b = cap["poisson"]["v1"], cap["boundary"]["null_boundary"]["v1"]
    st = v1["nulls"]["0.85"]
    print(f"{name:20s} lam_hat {v1['lam_hat']} SE {v1['se']}; H0 0.85: Wald {st['wald']} score {st['score']} "
          f"LR {st['lr']}; k_hat {cap['nb']['k_hat']}; LR = 0 in {b['p_zero']} +- {b['p_zero_mcse']}, "
          f"P(LR > 3.841) {b['p_gt_3841']} +- {b['p_gt_3841_mcse']}")

# %% after: E2
b = mine["boundary"]["null_boundary"]["v1"]
print("share with LR = 0:          ", b["p_zero"])  # write your prediction down before this line
print("share with variance <= mean:", b["p_boundary_score"])

# %% after: E3
run("likelihood.py", "boundary", "--quick", "--boundary-n", "50", "--out", "e3.json")
run("likelihood.py", "poisson", "--quick", "--corps", "VIII", "--out", "e3.json")

# %% after: E4
run("likelihood.py", "boundary", "--quick", "--fault", "--out", "fault.json")

# %% after: E5  [skip-build]
# Write zip_fit(values, counts) above this cell, returning (pi_hat, lam_hat, loglik, lr), then run it.
import math

import numpy as np

hits, squares = np.array([0, 1, 2, 3, 4, 7]), np.array([229, 211, 93, 35, 7, 1])
pi_hat, lam_hat, loglik, lr = zip_fit(hits, squares)
n, ybar = squares.sum(), (hits * squares).sum() / squares.sum()
print(f"pi_hat {pi_hat:.5f}, lam_hat {lam_hat:.5f}, LR {lr:.5f}; zeros {squares[0]} against n exp(-ybar) "
      f"{n * math.exp(-ybar):.3f}")
assert 0 <= pi_hat < 1 and abs(pi_hat - 0.016) < 0.001 and abs(lr - 0.094) < 0.001

# %% after: Safety and cleanup
import pathlib

for name in ("mine.json", "full.json", "e3.json", "fault.json"):
    pathlib.Path(name).unlink(missing_ok=True)
