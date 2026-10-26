# lab-cells.py — the code cells of lab/notebook.ipynb. Private build file: never uploaded.

# %% after: Run
import json
import subprocess
import sys


def run(*args):
    """Run the lab with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", "beyond.py", *args], check=True)  # -u: each line arrives as it prints


run("all", "--out", "mine.json")  # never overwrite the shipped captures.json

# %% after: E1
run("video", "--out", "mine.json")
with open("mine.json", encoding="utf-8") as handle:
    S = json.load(handle)["video"]["schemes"]
for key in ("independent", "shared", "warped", "joint", "data"):
    print(f"{key:>11}: coherent {S[key]['coherent_clips']:.4f}, flicker {S[key]['flicker']:.3f}")

# %% after: E2
with open("mine.json", encoding="utf-8") as handle:
    S = json.load(handle)["video"]["schemes"]
for key in ["independent"] + [k for k in S if k.startswith("mixed")]:
    print(f"{key:>11}: motion_clips {S[key]['motion_clips']:.4f}, frozen_clips {S[key]['frozen_clips']:.4f}")

# %% after: E3
run("video", "--warp-variance", "0.5", "--out", "mine.json")

# %% after: E4
run("video", "--fault", "--out", "mine.json")  # the diagnosis run: read the warped line and the last line

# %% after: E4  [skip-build]
run("video", "--fault", "--out", "mine.json")  # after your fix: warped coherent above 0.99, period 4

# %% after: Safety and cleanup
import pathlib

pathlib.Path("mine.json").unlink(missing_ok=True)
