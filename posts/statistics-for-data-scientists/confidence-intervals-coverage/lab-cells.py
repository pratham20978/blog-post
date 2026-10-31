# %% after: Run
import json
import subprocess
import sys


def run(*args):
    """Run a lab entry point with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", *args], check=True)  # -u: each stage prints as it runs


run("intervals.py", "all", "--quick", "--out", "mine.json")  # never overwrite the shipped captures

# %% after: E1
with open("mine.json", encoding="utf-8") as handle:
    mine = json.load(handle)
with open("captures-quick.json", encoding="utf-8") as handle:
    author = json.load(handle)
for name, cap in (("yours", mine), ("author's quick run", author)):
    m = cap["enumerate"]["methods"]
    ve = cap["pfizer"]["primary"]["methods"]["clopper_pearson"]["ve"]
    t30 = cap["tcoverage"]["by_n"]["30"]
    print(f"{name:20s} coverage Wald {m['wald']['coverage']:.4f}, Wilson {m['wilson']['coverage']:.4f}, "
          f"Clopper-Pearson {m['clopper_pearson']['coverage']:.4f}; efficacy {100 * ve[0]:.1f}% to {100 * ve[1]:.1f}%; "
          f"overlap rule {cap['overlap']['alpha_at']['1']:.5f}; t-interval at n = 30 {100 * t30['coverage']:.2f}% "
          f"+- {100 * t30['mcse']:.2f}")

# %% after: E2
# Write down which rows you expect to be most sensitive to the rounding before running this cell.
rows = [r for r in mine["pfizer"]["rows"] if r["interval"] == "clopper_pearson"]
for r in rows:
    if not r["matches_printed"]:
        print(f"{r['subgroup']:28s} lab {100 * r['ve']:.1f} ({100 * r['ci'][0]:.1f}, {100 * r['ci'][1]:.1f})  "
              f"printed {r['published']}  within rounding: {r['within_rounding']}")

# %% after: E3
run("intervals.py", "pfizer", "--quick", "--split", "4", "81", "--out", "e3.json")

# %% after: E4
run("intervals.py", "coverage", "--quick", "--fault", "--out", "fault.json")

# %% after: Safety and cleanup
import pathlib

for name in ("mine.json", "full.json", "e3.json", "fault.json"):
    pathlib.Path(name).unlink(missing_ok=True)
