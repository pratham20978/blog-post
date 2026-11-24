# %% after: Run
import json
import subprocess
import sys


def run(*args):
    """Run a lab entry point with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", *args], check=True)  # -u: each stage prints as it runs


run("permutation.py", "all", "--quick", "--out", "mine.json")  # never overwrite the shipped captures

# %% after: E1
with open("mine.json", encoding="utf-8") as handle:
    mine = json.load(handle)
with open("captures-quick.json", encoding="utf-8") as handle:
    author = json.load(handle)
for name, cap in (("yours", mine), ("author's quick run", author)):
    ex, hl = cap["example"], cap["example"]["hodges_lehmann"]
    at2 = cap["twosample"]["designs"]["10,40"]["2"]
    print(f"{name:20s} at least 314: {ex['perm']['ge']} of {ex['perm']['n_assign']}, p {ex['perm']['p']:.6f}; "
          f"t-test p {ex['p_t']:.6f}; signed-rank p {ex['signed_rank']['p']:.6f}; "
          f"Hodges-Lehmann {hl['estimate']} ({hl['lower']} to {hl['upper']}); at 10 vs 40, SD x 2: raw "
          f"{100 * at2['perm_diff']:.2f}% +- {100 * at2['mcse'][0]:.2f}, studentised {100 * at2['perm_studentised']:.2f}% "
          f"+- {100 * at2['mcse'][1]:.2f}")

# %% after: E2
# Work out the two boundary totals before running this cell.
print("negatives, above 314, equal to 314, below 314, assignments")
for row in mine["example"]["table4"]:
    print(row)

# %% after: E3
run("permutation.py", "twosample", "--quick", "--n1", "25", "--n2", "25", "--ratio", "4", "--out", "e3.json")

# %% after: E4
run("permutation.py", "example", "--quick", "--fault", "--out", "fault.json")

# %% after: Safety and cleanup
import pathlib

for name in ("mine.json", "full.json", "e3.json", "fault.json"):
    pathlib.Path(name).unlink(missing_ok=True)
