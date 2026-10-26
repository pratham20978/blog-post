# lab-cells.py — the code cells of lab/notebook.ipynb (blog-forge). Private: never uploaded.
# build_lab_notebook.py places each cell at the end of the README section its marker names,
# before that section's first <details> answer.

# %% after: Run
import json
import subprocess
import sys


def run(*args):
    """Run the lab's entry point with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", "evaluate.py", *args], check=True)   # -u: progress lines arrive as they print


def mine():
    with open("mine.json", encoding="utf-8") as handle:
        return json.load(handle)


run("all", "--out", "mine.json")   # never overwrite the shipped captures.json; about 45 s

# %% after: E1
run("failures", "--out", "mine.json")
sets = mine()["failures"]["sets"]
for name in ("drops faint", "grainy"):
    print(name, {k: round(sets[name][k], 4) for k in ("fd", "precision", "recall", "coverage")})

# %% after: E2
with open("captures.json", encoding="utf-8") as handle:   # the author's run
    weights = json.load(handle)["guidance"]["weights"]
for w in ("5.0", "7.5"):
    print("w =", w, {k: weights[w][k] for k in ("faint", "faint_holders", "faint_holder_radius_median",
                                                "fake_radius_median", "recall_faint", "coverage_faint")})

# %% after: E3 — Predict: a little grain
run("failures", "--grain", "0.05", "--out", "mine.json")
grainy = mine()["failures"]["sets"]["grainy"]
print({k: round(grainy[k], 4) for k in ("fd", "precision", "recall", "density", "coverage")})

# %% after: E3 — Predict: the sample count
run("bias", "--out", "mine.json")
perfect = mine()["bias"]["gens"]["perfect"]
print(dict(zip(mine()["bias"]["ns"], perfect["fd_mean"])), "prediction at 2,000:", round(0.0007 + 59.9 / 2000, 4))

# %% after: Safety and cleanup
import pathlib

pathlib.Path("mine.json").unlink(missing_ok=True)
