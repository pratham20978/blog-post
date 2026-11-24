# lab-cells.py — the code cells of lab/notebook.ipynb (blog-forge). Private: never uploaded.

# %% after: Run
import subprocess
import sys


def run(*args, check=True):
    """Run the lab's entry point with this kernel's interpreter; a non-zero exit fails the cell
    unless check=False, which returns the exit status instead."""
    status = subprocess.run([sys.executable, "-u", "multiplicity.py", *args], check=check).returncode
    return None if check else status


run("--quick", "--out", "mine.json")  # never overwrite the shipped captures

# %% after: E1
run("procedures")

# %% after: E3
import json

run("dependence", "--quick", "--out", "mine-e3.json")
with open("mine-e3.json", encoding="utf-8") as handle:
    rho = json.load(handle)["dependence"]["by_rho"]["0.3"]
for rule in ("BH", "Storey q"):
    r = rho[rule]
    print(f"{rule:9s} FDR {r['FDR']:.4f} ± {r['FDR_se']:.4f}   P(FDP > 10%) {r['P_FDP_gt_10']:.4f}")

# %% after: E4
status = run("procedures", "--fault", "stepdown", check=False)
print("exit status with the fault:", status)  # 1: the reconciliation caught it

# %% after: Safety and cleanup
import pathlib

for name in ("mine.json", "mine-e3.json"):
    pathlib.Path(name).unlink(missing_ok=True)
