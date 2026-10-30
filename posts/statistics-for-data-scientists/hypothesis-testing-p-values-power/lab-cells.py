# %% after: Run
import json
import subprocess
import sys


def run(*args):
    """Run a lab entry point with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", *args], check=True)  # -u: each stage prints as it runs


run("testing.py", "all", "--quick", "--out", "mine.json")  # never overwrite the shipped captures

# %% after: E1
with open("mine.json", encoding="utf-8") as handle:
    mine = json.load(handle)
with open("captures-quick.json", encoding="utf-8") as handle:
    author = json.load(handle)
for name, cap in (("yours", mine), ("author's quick run", author)):
    ex = cap["retrodesign"]["cases"]["durante_2"]["exact"]
    eq, ns = cap["fpr"]["equals"]["0.03"], cap["replication"]["nonsig"]
    print(f"{name:20s} power {ex['power']:.4f} type S {ex['typeS']:.4f} exaggeration {ex['exaggeration']:.4f}; "
          f"p = .03: FPR {eq['fpr_prior05']:.4f} and {eq['fpr_prior01']:.4f}; equivalent {ns['equivalent_0.1']} and "
          f"{ns['equivalent_0.2']}; test-at-20-add-10 {cap['stopping']['simmons']['alpha']:.4f}")

# %% after: E2
d = mine["retrodesign"]["cases"]["durante_2"]
print("bar:", round(1.959964 * 8.1, 4))  # write your prediction down before the next two lines
print("smallest significant magnitude:", d["min_abs_sig"])
print("share of significant estimates below zero:", d["share_sig_negative"], "against the exact", d["exact"]["typeS"])

# %% after: E3
run("testing.py", "retrodesign", "--quick", "--se", "5.7276", "--out", "e3.json")

# %% after: E4
run("testing.py", "retrodesign", "--quick", "--fault", "--out", "fault.json")

# %% after: E5  [skip-build]
# Write pocock_constant(K) above this cell, returning the constant bar c for K looks, then run it.
import testing

for K, target in ((1, 1.960), (2, 2.178), (5, 2.413)):
    c = pocock_constant(K)
    print(f"K = {K}: c = {c:.4f}; overall rate at c {testing.stopping_exact(K, c=c)[-1]:.5f}")
    assert abs(c - target) < 0.005

# %% after: Safety and cleanup
import pathlib

for name in ("mine.json", "full.json", "e3.json", "fault.json"):
    pathlib.Path(name).unlink(missing_ok=True)
