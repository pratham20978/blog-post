# lab-cells.py — the code cells of lab/notebook.ipynb. Private build file: never uploaded.

# %% after: Run
import json
import subprocess
import sys


def run(*args):
    """Run the lab with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", "tokens.py", *args], check=True)  # -u: each line arrives as it prints


run("all", "--out", "mine.json")  # never overwrite the shipped captures.json

# %% after: E1
run("decode", "--out", "mine.json")
with open("mine.json", encoding="utf-8") as handle:
    D = json.load(handle)["decode"]
for name, res in (("one per step", D["one_per_step"]["random"]), ("two per step", D["parallel"]["random_2"])):
    print(f"{name:>12}: valid {res['valid']}, images {res['images_found']}, brightness sd {res['brightness_sd']}")

# %% after: E2
run("world", "--out", "mine.json")
with open("mine.json", encoding="utf-8") as handle:
    print(json.load(handle)["world"]["decided_after"])

# %% after: E3
run("decode", "--levels", "1", "--out", "mine.json")

# %% after: E4
run("decode", "--fault", "--out", "mine.json")  # the diagnosis run: compare the position line with the others

# %% after: E4  [skip-build]
run("decode", "--fault", "--out", "mine.json")  # after your fix: the position line shows 72 images again

# %% after: Safety and cleanup
import pathlib

pathlib.Path("mine.json").unlink(missing_ok=True)
