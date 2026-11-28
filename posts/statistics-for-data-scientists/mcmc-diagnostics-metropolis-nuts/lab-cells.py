# %% after: Run
import json
import subprocess
import sys


def run(*args):
    """Run a lab entry point with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", *args], check=True)  # -u: each stage prints as it runs


run("mcmc.py", "all", "--quick", "--out", "quick.json")  # never overwrite the shipped captures
run("mcmc.py", "all", "--out", "mine.json")              # the article's budget, about 2.5 minutes

# %% after: E1
run("mcmc.py", "pfizer", "--quick", "--out", "e1.json")
with open("e1.json", encoding="utf-8") as handle:
    mine = json.load(handle)["pfizer"]
with open("captures-quick.json", encoding="utf-8") as handle:
    author = json.load(handle)["pfizer"]
for name, cap in (("yours", mine), ("author's quick run", author)):
    est, dg = cap["estimates"], cap["diagnostics"]
    print(f"{name:20s} VE {100 * est['q025']['value']:.3f}% +- {100 * est['q025']['mcse']:.3f} to "
          f"{100 * est['q975']['value']:.3f}% +- {100 * est['q975']['mcse']:.3f}; R-hat {dg['rank']:.4f}; "
          f"bulk ESS {dg['ess_bulk']:.0f}; tail ESS {dg['ess_tail']:.0f}; {cap['check']}")

# %% after: E2
# Say which two of the three numbers will be equal, and why, before running this cell.
run("mcmc.py", "diagnostics", "--quick", "--out", "e2.json")
with open("e2.json", encoding="utf-8") as handle:
    d = json.load(handle)["diagnostics"]["nb_mu"]
print("tail ESS at 5% and 95% (Vehtari et al.):", round(d["mine"]["ess_tail"], 1))
print("tail ESS at 11% and 89%, by hand:      ", round(d["mine"]["ess_tail_11_89"], 1))
print("ArviZ's default on xarray input:        ", round(d["arviz"]["ess_tail_default_xarray"], 1))

# %% after: E3
# Write down your predicted acceptance, bulk ESS and R-hat before running this cell.
run("mcmc.py", "pfizer", "--quick", "--step", "0.01", "--out", "e3.json")

# %% after: E4
run("mcmc.py", "pfizer", "--quick", "--fault", "--out", "e4.json")

# %% after: E4  [skip-build]
# After your fix in mcmc.py: the same command should now print "check: PASS". Undo the edit afterwards.
run("mcmc.py", "pfizer", "--quick", "--fault", "--out", "e4.json")

# %% after: E5  [skip-build]
# Your extension: Clarke's squares under the same model and priors. Fill in the log posterior and the grid.
import numpy as np
from scipy import special

import mcmc

hits, squares = np.loadtxt("data/clarke1946_flying_bombs.csv", delimiter=",", comments="#", skiprows=1, unpack=True)


def logp_clarke(x):
    """Unnormalised log posterior of (log mu, log k) for Clarke's counts; x is an (m, 2) array of states."""
    raise NotImplementedError("your negative binomial log-likelihood plus the two N(0, 2^2) priors")


rng = np.random.default_rng(12)
# warm up, freeze a step, then: draws, acc = mcmc.metropolis(logp_clarke, start, step, 5000, rng)
# for each parameter: mcmc.summarize(...), mcmc.mcse_mean(...), mcmc.mcse_quantile(...); then your grid

# %% after: Safety and cleanup
import pathlib
import shutil

for name in ("quick.json", "mine.json", "e1.json", "e2.json", "e3.json", "e4.json"):
    pathlib.Path(name).unlink(missing_ok=True)
shutil.rmtree(".pytensor", ignore_errors=True)
shutil.rmtree("__pycache__", ignore_errors=True)
