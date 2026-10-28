# %% after: Run
import json
import subprocess
import sys


def run(*args):
    """Run a lab entry point with this kernel's interpreter; a non-zero exit fails the cell."""
    subprocess.run([sys.executable, "-u", *args], check=True)  # -u: each stage prints as it runs


run("estimators.py", "all", "--quick", "--out", "mine.json")  # never overwrite the shipped captures

# %% after: E1
with open("mine.json", encoding="utf-8") as handle:
    mine = json.load(handle)
with open("captures-quick.json", encoding="utf-8") as handle:
    author = json.load(handle)
for name, cap in (("yours", mine), ("author's quick run", author)):
    t = cap["tanks"]
    print(f"{name:20s} " + "; ".join(
        f"{e} bias {t['sim'][e]['bias']:.2f} +- {t['sim'][e]['bias_mcse']:.2f} (exact {t['exact'][e]['bias']:.2f}), "
        f"MSE {t['sim'][e]['mse']:,.0f}" for e in ("mle", "mvue", "minmse")))

# %% after: E2
replay, players = mine["baseball"]["replay"], mine["baseball"]["players"]
print("players hurt on average:", replay["players_hurt"] or "none")  # write your prediction down before this line
for ratio, name in sorted(((z / y, p) for z, y, p in zip(replay["mse_z"], replay["mse_y"], players)), reverse=True):
    print(f"  {name:13s} James-Stein MSE / own-average MSE = {ratio:.3f}")

# %% after: E3
run("estimators.py", "tanks", "--quick", "--k", "20", "--out", "k20.json")
run("estimators.py", "divisors", "--quick", "--n", "30", "--out", "n30.json")

# %% after: E4
run("estimators.py", "tanks", "--quick", "--fault", "--out", "fault.json")

# %% after: Safety and cleanup
import pathlib

for name in ("mine.json", "full.json", "k20.json", "n30.json", "fault.json"):
    pathlib.Path(name).unlink(missing_ok=True)
