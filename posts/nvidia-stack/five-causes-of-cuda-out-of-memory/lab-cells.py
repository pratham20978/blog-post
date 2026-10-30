# lab-cells.py — the code cells of lab/notebook.ipynb (blog-forge). Private: never uploaded.
#
# build_lab_notebook.py builds the notebook from lab/README.md, verbatim, and puts each cell below at
# the end of the README section its marker names. The E2 code is a python fence in the README, so it
# is not repeated here. Cells that need the GPU are [skip-build]: the build machine has none, so they
# are syntax-checked and shipped, not run.

# %% after: Run
import subprocess
import sys


def run(*args):
    """Run a lab entry point with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", *args], check=True)  # -u: progress lines arrive as they print

# %% after: Run  [skip-build]
run("oom_lab.py", "run", "--out", "mine.json")  # needs one NVIDIA GPU; about 2.5 minutes on the GB10
run("diagnose.py", "mine.json")

# %% after: E1
run("diagnose.py", "captures.json")

# %% after: E3  [skip-build]
run("oom_lab.py", "run", "--case", "retained", "--val-batch", "768", "--out", "e3.json")

# %% after: E4  [skip-build]
run("oom_lab.py", "mystery", "--seed", "5")
run("oom_lab.py", "mystery", "--seed", "5", "--fix", "non-pytorch")  # put your own diagnosis here
run("oom_lab.py", "mystery", "--seed", "5", "--reveal")

# %% after: Safety and cleanup
import pathlib

for name in ("mine.json", "e3.json"):
    pathlib.Path(name).unlink(missing_ok=True)  # your runs; the shipped captures.json stays
