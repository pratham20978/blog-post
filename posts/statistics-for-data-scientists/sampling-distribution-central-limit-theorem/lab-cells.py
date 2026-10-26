# %% after: Run
import json
import subprocess
import sys


def run(*args):
    """Run a lab entry point with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", *args], check=True)  # -u: each stage prints as it runs


run("sampling.py", "all", "--quick", "--out", "mine.json")  # never overwrite the shipped captures

# %% after: E1
with open("mine.json", encoding="utf-8") as handle:
    mine = json.load(handle)
with open("captures-quick.json", encoding="utf-8") as handle:
    author = json.load(handle)
pop = mine["population"]
print("population:", round(pop["mean"], 2), round(pop["sd"], 2), round(pop["skewness"], 3))
for name, cap in (("yours", mine), ("author's quick run", author)):
    r = cap["sampling"]["by_n"]["30"]
    print(f"{name:20s} n = 30: lower {100 * r['lower']['p']:.2f}% +- {100 * r['lower']['mcse']:.2f}, "
          f"upper {100 * r['upper']['p']:.2f}%, two-sided {100 * r['two_sided']['p']:.2f}%")

# %% after: E2
r30 = mine["sampling"]["by_n"]["30"]
print(sorted(r30))  # write your two predictions down, then read the four keys the exercise names

# %% after: E3
run("sampling.py", "population", "--cap", "0.99", "--out", "capped.json")
run("sampling.py", "sampling", "--quick", "--cap", "0.99", "--out", "capped.json")

# %% after: E4
run("sampling.py", "sampling", "--quick", "--fault", "--out", "fault.json")

# %% after: Safety and cleanup
import pathlib

for name in ("mine.json", "full.json", "capped.json", "fault.json", "check.csv"):
    pathlib.Path(name).unlink(missing_ok=True)
