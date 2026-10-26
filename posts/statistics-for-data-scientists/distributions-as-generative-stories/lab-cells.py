# %% after: Run
import subprocess
import sys


def run(*args):
    """Run a lab entry point with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", *args], check=True)  # -u: each stage prints as it runs


run("stories.py", "all", "--out", "mine.json")  # never overwrite the shipped capture

# %% after: E1
import json

with open("mine.json", encoding="utf-8") as handle:
    mine = json.load(handle)
clarke = mine["worked"]["clarke"]
print("Clarke, Poisson row:", [round(v, 3) for v in clarke["expected_poisson"]])
print("chi-square:", round(clarke["chi2"], 4), " P:", round(clarke["chi2_p"], 4))
nb = mine["accidents"]["negative_binomial"]
print("moment fit k:", round(nb["k"], 4), " negative binomial chi-square:", round(nb["chi2"], 2))

# %% after: E2
simulated = mine["accidents"]["proneness_simulation"]
print(sorted(simulated))  # write your two predictions down, then read within_part and between_part

# %% after: E3 — Predict: one effect
run("stories.py", "sums", "--dominant", "--out", "dominant.json")

# %% after: E3 — Predict: heavier
run("stories.py", "tails", "--df", "3", "--out", "t3.json")

# %% after: E4
run("stories.py", "accidents", "--fault", "--out", "fault.json")

# %% after: Safety and cleanup
import pathlib

for name in ("mine.json", "dominant.json", "t3.json", "fault.json"):
    pathlib.Path(name).unlink(missing_ok=True)
