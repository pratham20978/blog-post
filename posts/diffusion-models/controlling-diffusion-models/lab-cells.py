# lab-cells.py — the code cells of lab/notebook.ipynb (blog-forge). Private: never uploaded.
# build_lab_notebook.py places each cell at the end of the README section its marker names,
# before that section's first <details> answer.

# %% after: Run
import subprocess
import sys


def run(*args):
    """Run the lab's entry point with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", "control.py", *args], check=True)   # -u: progress lines arrive as they print


run("all", "--quick", "--out", "mine.json")   # never overwrite the shipped captures.json; the full run is "all"

# %% after: E1
run("worked", "--out", "mine.json")

# %% after: E2
import json

with open("captures.json", encoding="utf-8") as handle:   # the author's run
    exact = json.load(handle)["exact"]
print("full guidance, w = 3:", exact["weights"]["3.0"]["faint"])
print("guidance only at or below sigma:", {k: round(v["faint"], 2) for k, v in exact["below"].items()})
print("guidance only above sigma:      ", {k: round(v["faint"], 2) for k, v in exact["above"].items()})

# %% after: E3
run("edit", "--out", "mine.json")

# %% after: E4
run("personal", "--quick", "--method", "full", "--steps", "1000", "--out", "mine.json")

# %% after: E4  [skip-build]
METHOD = "full"   # your fix: the method you think repairs it (see the stage's --method choices), then run this cell
run("personal", "--quick", "--method", METHOD, "--steps", "1000", "--out", "mine.json")

# %% after: E5  [skip-build]
import importlib
import numpy as np
import control

importlib.reload(control)                       # picks up your replacement_jump
src, _, _ = control.sample_data(np.random.default_rng(11), 2048)
y = src[:, control.KNOWN]
assert np.array_equal(control.replacement_jump(y, 64, 1, 1), control.replacement(y, 64, 1))   # acceptance test 1
pm = control.posterior_mean(y)
for j in (1, 2, 5):
    print("jump", j, control.coherence(control.replacement_jump(y, 64, 5, j), pm))

# %% after: Safety and cleanup
import pathlib
import shutil

pathlib.Path("mine.json").unlink(missing_ok=True)
shutil.rmtree(".cache", ignore_errors=True)
