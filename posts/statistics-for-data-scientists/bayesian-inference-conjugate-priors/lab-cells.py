# %% after: Run
import json
import subprocess
import sys


def run(*args):
    """Run a lab entry point with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", *args], check=True)  # -u: each stage prints as it runs


run("bayes.py", "all", "--quick", "--out", "mine.json")  # never overwrite the shipped captures

# %% after: E1
with open("mine.json", encoding="utf-8") as handle:
    mine = json.load(handle)
with open("captures-quick.json", encoding="utf-8") as handle:
    author = json.load(handle)
for name, cap in (("yours", mine), ("author's quick run", author)):
    row = next(r for r in cap["pfizer"]["rows"] if r["split"] == [8, 162])
    cov = cap["intervals"]["primary"]["coverage"]
    print(f"{name:20s} P(x <= 1/2) {cap['laplace']['tail_beta_cdf']:.6e}; VE {100 * row['lower']:.3f} to "
          f"{100 * row['upper']:.3f}%; P(VE <= 30%) {row['p_ve_le_30']:.3e}; 1782 BF01 "
          f"{cap['lindley']['years']['1782']['bf01']:.3f}, p {cap['lindley']['years']['1782']['p_exact']:.4f}; "
          f"prior-averaged coverage {100 * cov['prior_average_mc']:.2f}% +- {100 * cov['prior_average_mcse']:.2f}")

# %% after: E2
# Write down the two boundaries at 62 cases before running this cell.
success, pos = mine["pfizer"]["success_curves"]["62"], mine["pfizer"]["pos_curves"]["62"]
for x in (14, 15, 16, 24, 25, 26, 27):
    print(f"x = {x:2d}: P(VE > 30% | data) {success[x]:.4f}   predictive P(final success) {pos[x]:.4f}")

# %% after: E3
run("bayes.py", "priors", "--quick", "--split", "0", "5", "--times", "0.102", "0.106", "--out", "e3.json")

# %% after: E4
run("bayes.py", "pfizer", "--quick", "--fault", "--out", "fault.json")

# %% after: Safety and cleanup
import pathlib

for name in ("mine.json", "full.json", "e3.json", "fault.json"):
    pathlib.Path(name).unlink(missing_ok=True)
