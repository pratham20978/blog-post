# lab-cells.py — the code cells of lab/notebook.ipynb (blog-forge). Private: never uploaded.
# build_lab_notebook.py places each cell at the end of the README section its marker names,
# before that section's first <details> answer.

# %% after: Run
import subprocess
import sys


def run(*args):
    """Run the lab's entry point with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", "distill.py", *args], check=True)   # -u: progress lines arrive as they print


run("all", "--quick", "--out", "mine.json")   # never overwrite the shipped captures.json; the full run is "all"

# %% after: E1
run("worked", "--out", "mine.json")

# %% after: E2
import json

with open("captures.json", encoding="utf-8") as handle:   # the author's run
    shipped = json.load(handle)
print("margin_bins ", shipped["margin_bins"])
print("margin_share", shipped["margin_share"])
for seed, student in shipped["students"]["regression"].items():
    print(f"seed {seed} flip_by_margin", student["steps"]["1"]["flip_by_margin"])

# %% after: E3
run("worked", "--x", "1.6", "--out", "mine.json")

# %% after: E4
run("dmd", "--quick", "--ratio", "1", "--warm", "0", "--steps", "300", "--out", "mine.json")

# %% after: E4  [skip-build]
FLAGS = ["--ratio", "1", "--warm", "0", "--steps", "300"]   # your fix: change the flags you think repair it, then run this cell
run("dmd", "--quick", *FLAGS, "--out", "mine.json")

# %% after: Safety and cleanup
import pathlib
import shutil

pathlib.Path("mine.json").unlink(missing_ok=True)
shutil.rmtree(".cache", ignore_errors=True)
