# %% after: Run
import json
import subprocess
import sys


def run(*args):
    """Run a lab entry point with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", *args], check=True)  # -u: each stage prints as it runs


run("choosing.py", "all", "--quick", "--out", "mine.json")  # never overwrite the shipped captures

# %% after: E1
with open("mine.json", encoding="utf-8") as handle:
    mine = json.load(handle)
with open("captures-quick.json", encoding="utf-8") as handle:
    author = json.load(handle)
for name, cap in (("yours", mine), ("author's quick run", author)):
    ex, an = cap["example"], cap["anova"]
    student = cap["twosample"]["designs"]["10,40"]["exact"]["2"]["student"]
    fisher = cap["tables"]["designs"]["malocclusion"]["size"]["fisher"]["max"]
    levene = cap["pretest"]["by_ratio"]["2"]["levene_rule"]
    print(f"{name:20s} paired p {ex['paired']['p']:.6f}, Student p {ex['student']['p']:.6f}, Welch p {ex['welch']['p']:.6f}; "
          f"Student's error at 10 vs 40, SD x 2: {100 * student:.2f}%; Fisher's largest size {100 * fisher:.2f}%; "
          f"F {an['F']:.4f}, W {an['W']:.4f}; Levene decides at 2: {100 * levene['rate']:.2f}% +- {100 * levene['mcse']:.2f}")

# %% after: E2
# Write down your prediction of Fisher's p for these tables before running this cell.
for normal_20, normal_22, p_fisher, p_boschloo in mine["tables"]["boschloo_not_fisher"]:
    print(f"{normal_20:2d} of 20 against {normal_22:2d} of 22: Fisher {p_fisher:.4f}, Boschloo {p_boschloo:.4f}")
print("with groups of 10 and 40, Fisher rejects and Boschloo does not:", mine["tables"]["unbalanced_fisher_not_boschloo"])

# %% after: E3
run("choosing.py", "twosample", "--quick", "--n1", "40", "--n2", "10", "--ratio", "2", "--out", "e3.json")

# %% after: E4
run("choosing.py", "example", "--quick", "--fault", "--out", "fault.json")

# %% after: Safety and cleanup
import pathlib

for name in ("mine.json", "full.json", "e3.json", "fault.json"):
    pathlib.Path(name).unlink(missing_ok=True)
