# %% after: Run
import json
import shutil
import subprocess
import sys


def run(*args):
    """Run a lab entry point with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", *args], check=True)  # -u: each stage prints as it runs


run("regression.py", "all", "--quick", "--out", "quick.json")  # never overwrite the shipped captures
run("regression.py", "all", "--out", "mine.json")              # the article's budget, about 20 seconds
if shutil.which("Rscript"):                                     # optional: R's lm on the same models
    subprocess.run(["Rscript", "crosscheck.R"], check=True)
else:
    print("Rscript not found: the shipped crosscheck-R.csv stays as the author's R output")

# %% after: E1
run("regression.py", "nist", "--quick", "--out", "e1.json")
with open("e1.json", encoding="utf-8") as handle:
    mine = json.load(handle)["nist"]
with open("captures-quick.json", encoding="utf-8") as handle:
    author = json.load(handle)["nist"]
for name, cap in (("yours", mine), ("author's quick run", author)):
    lo, fi = cap["datasets"]["Longley"]["solvers"], cap["datasets"]["Filip"]["solvers"]
    print(f"{name:20s} exact {cap['exact']['matched']}/{cap['exact']['total']}; Longley QR "
          f"{min(lo['Householder QR']['lre']):.2f}, normal equations {min(lo['normal equations (LU)']['lre']):.2f}; "
          f"Filip QR {min(fi['Householder QR']['lre']):.2f}; statsmodels default warns: "
          f"{fi['statsmodels OLS().fit()']['warnings']}")

# %% after: E2
# Say which solvers should keep all eleven columns, and why, before running this cell.
fil = mine["datasets"]["Filip"]
print("smallest / largest singular value:", fil["sv_ratio"])
print("NumPy default cutoff:              ", fil["numpy_cutoff"])
print("statsmodels pseudoinverse cutoff:  ", fil["statsmodels_cutoff"])
print("machine precision (rcond=-1, SciPy):", sys.float_info.epsilon)

# %% after: E3
# Write down which summary numbers change and how many digits each solver gains before running this cell.
run("regression.py", "summary", "--quick", "--year-origin", "1954", "--out", "e3.json")
run("regression.py", "nist", "--quick", "--year-origin", "1954", "--out", "e3.json")

# %% after: E4
run("regression.py", "summary", "--quick", "--fault", "--out", "e4.json")

# %% after: E4  [skip-build]
# After your fix in regression.py: the same command should print R^2 0.995479 and sigma 304.854. Undo the edit afterwards.
run("regression.py", "summary", "--quick", "--fault", "--out", "e4.json")

# %% after: E5  [skip-build]
# Your extension: modified Gram-Schmidt two ways, scored on NIST's eleven datasets next to Householder QR.
import numpy as np

import regression as lab


def mgs_qty(X, y):
    """Modified Gram-Schmidt on X, then R b = Q'y."""
    raise NotImplementedError("factor X column by column, subtracting each projection from the remaining columns")


def mgs_augmented(X, y):
    """Modified Gram-Schmidt on [X | y]; the coefficients solve R11 b = r12 from the last column of R."""
    raise NotImplementedError("factor the augmented matrix and back-substitute")


rng = np.random.default_rng(13)
A, b = rng.standard_normal((50, 5)), rng.standard_normal(50)
reference = np.linalg.lstsq(A, b, rcond=None)[0]
for solver in (mgs_qty, mgs_augmented):
    assert np.allclose(solver(A, b), reference, rtol=1e-12, atol=0), solver.__name__
for name in lab.NIST_MODEL:
    cert, data = lab.read_nist(name)
    X, y = lab.nist_design(name, data)
    digits = {s.__name__: min(lab.lre(v, float(c)) for v, c in zip(s(X, y), cert["b"])) for s in (mgs_qty, mgs_augmented)}
    print(f"{name:9s} scaled kappa {lab.kappa_scaled(X):9.2e}  " + "  ".join(f"{k} {v:5.2f}" for k, v in digits.items()))

# %% after: Safety and cleanup
import pathlib

for name in ("quick.json", "mine.json", "e1.json", "e3.json", "e4.json"):
    pathlib.Path(name).unlink(missing_ok=True)
shutil.rmtree(".nist", ignore_errors=True)
shutil.rmtree("__pycache__", ignore_errors=True)
