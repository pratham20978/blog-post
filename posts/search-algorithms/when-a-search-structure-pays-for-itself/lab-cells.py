# lab-cells.py — the code cells of lab/notebook.ipynb (blog-forge). Private: never uploaded.
# build_lab_notebook.py places each cell at the end of the README section its marker names,
# before that section's first <details> answer.

# %% after: Run
import subprocess
import sys


def run(*args):
    """Run the lab's entry point with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", "pays_for_itself.py", *args], check=True)


run("all", "--out", "mine.json")  # never overwrite the shipped captures.json

# %% after: E1
run("worked", "--out", "mine.json")

# %% after: E2
import json

import pays_for_itself as lab

with open("mine.json", encoding="utf-8") as handle:
    colliding = json.load(handle)["flood"]["colliding"]
print("insert_eq_calls", colliding["insert_eq_calls"])
print("extra_vs_model ", colliding["extra_vs_model"])
print("replay_probes  ", lab.replay_probes(16))

# %% after: E3 — Predict: the break-even
run("scale", "--max-exp", "24", "--out", "mine.json")

# %% after: E3 — Predict: a cheaper shift
run("writes", "--write-price", "0.25", "--out", "mine.json")

# %% after: Safety and cleanup
import pathlib

pathlib.Path("mine.json").unlink(missing_ok=True)
