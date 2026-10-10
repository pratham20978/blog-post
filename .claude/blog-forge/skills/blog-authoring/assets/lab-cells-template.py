# lab-cells.py — the code cells of lab/notebook.ipynb (blog-forge). Private: never uploaded.
#
# Copy to posts/<series-slug>/<slug>/lab-cells.py; the rules are in references/labs.md under
# "The notebook". build_lab_notebook.py builds the notebook from lab/README.md, verbatim, and puts
# each cell below at the end of the README section its marker names, before that section's first
# <details> answer. A python fence in the README outside an answer is already a cell, so do not
# repeat it here. Replace every <...>, delete the cells this lab does not need, and delete this
# comment.

# %% after: Run
import subprocess
import sys


def run(*args):
    """Run a lab entry point with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", *args], check=True)  # -u: progress lines arrive as they print


# (G2) Start the disposable service here instead: its data in a scratch directory inside this
# folder, and its stop registered with atexit, so a failed run or a restarted kernel never leaves
# it running.
run("<run.py>", "--out", "mine.json")  # never overwrite the shipped capture

# %% after: E1
run("<run.py>", "<stage>", "--out", "mine.json")

# %% after: E2
import json

with open("mine.json", encoding="utf-8") as handle:
    mine = json.load(handle)
print(sorted(mine))  # the keys the README's E2 names; the reader reads the intermediate from here

# %% after: E4  [skip-build]
run("<check.py>", "e4", "--verify")  # needs the reader's repair, so the build does not run it

# %% after: E5  [skip-build]
run("<check.py>", "e5")  # the acceptance test runs the reader's build

# %% after: Safety and cleanup
# (G2) Stop the service, delete the scratch directory, and raise if anything is still running.
import pathlib

pathlib.Path("mine.json").unlink(missing_ok=True)
