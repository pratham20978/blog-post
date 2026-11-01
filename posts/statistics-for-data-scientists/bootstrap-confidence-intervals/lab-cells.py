# %% after: Run
import json
import subprocess
import sys


def run(*args):
    """Run a lab entry point with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", *args], check=True)  # -u: each stage prints as it runs


run("bootstrap.py", "all", "--quick", "--out", "mine.json")  # never overwrite the shipped captures

# %% after: E1
with open("mine.json", encoding="utf-8") as handle:
    mine = json.load(handle)
with open("captures-quick.json", encoding="utf-8") as handle:
    author = json.load(handle)
for name, cap in (("yours", mine), ("author's quick run", author)):
    ex, rec, cov = cap["example"], cap["reconcile"], cap["coverage"]["methods"]["bca"]
    lo, hi = ex["intervals"]["bca"]
    print(f"{name:20s} SE {ex['se_boot']:.4f}, z0 {ex['z0']:+.4f}, a {ex['a']:+.5f}, BCa {lo:.4f} to {hi:.4f}; "
          f"SciPy diff {rec['scipy']['max_abs_diff']:.1e}, R diff {rec['r']['max_abs_diff']:.1e}; "
          f"BCa coverage {100 * cov['coverage']:.1f}% +- {100 * cov['mcse']:.1f}")

# %% after: E2
# Name the school you expect to move r most before running this cell.
ex = mine["example"]
jack, schools = ex["jackknife"], ex["schools"]
centre = sum(jack) / len(jack)
d = [centre - j for j in jack]
s2, s3 = sum(v * v for v in d), sum(v**3 for v in d)
print(f"a = {s3 / (6 * s2**1.5):+.5f}")
for school, j, v in sorted(zip(schools, jack, d), key=lambda t: -abs(t[2]))[:3]:
    print(f"school {school}: leave-one-out r {j:.4f}, d {v:+.4f}, share of sum d^3 {100 * v**3 / s3:.0f}%")

# %% after: E3
run("bootstrap.py", "example", "--quick", "--drop", "6", "--out", "e3.json")

# %% after: E4
run("bootstrap.py", "example", "--quick", "--fault", "--out", "fault.json")

# %% after: E5  [skip-build]
# Your m-out-of-n function goes here; the acceptance test is the README's self-check.
import numpy as np


def upper_bound(sample, m, B, rng, level=0.95):
    """One-sided upper bound for a uniform endpoint from B resamples of size m: to be written."""
    raise NotImplementedError


rng = np.random.default_rng(1)
covered = [upper_bound(rng.random(1000), 50, 2000, rng) >= 1.0 for _ in range(1000)]
print(f"coverage {100 * np.mean(covered):.1f}%")

# %% after: Safety and cleanup
import pathlib

for name in ("mine.json", "full.json", "e3.json", "fault.json"):
    pathlib.Path(name).unlink(missing_ok=True)
