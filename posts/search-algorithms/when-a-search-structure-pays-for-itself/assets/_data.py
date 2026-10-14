"""Every value the figures and social cards draw, read from the lab's shipped captures.json.

The asserts hold each number to the one the article prints, so a figure that disagrees with the
text fails to build. Nothing here computes a count of its own; the lab does that.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))

W, SCALE, WRITES, FLOOD = CAP["worked"], CAP["scale"], CAP["writes"], CAP["flood"]
KEYS = W["keys"]
LOOK, SORT, BE = W["lookup"], W["sort"], W["breakeven"]
TM, PLAIN, OQ, INS = W["treemap"], W["plain_bst"], W["ordered_queries"], W["sorted_array_insert_50"]

# ---------------------------------------------------------------- the worked example
SCAN_HIT, SCAN_MISS = LOOK["scan_hit_avg"], LOOK["scan_miss"]
BIN_HIT, BIN_MISS = LOOK["binary_hit_avg"], LOOK["binary_miss_avg"]
SORT_WORST, SORT_MEAN = SORT["merge_worst"], SORT["merge_mean_exact"]
Q_WORST = BE["hits_worst_sort"]["q_star"]
Q_MEAN = BE["hits_mean_sort"]["q_star"]
Q_MISS = BE["misses_worst_sort"]["q_star"]
CUM = BE["cumulative"]
assert KEYS == [3, 9, 14, 21, 28, 35, 42, 47, 53, 61, 68, 74, 79, 85, 91, 97]
assert (SCAN_HIT, SCAN_MISS, BIN_HIT, LOOK["binary_hit_max"]) == (8.5, 16, 3.375, 5)
assert round(BIN_MISS, 2) == 4.12 and LOOK["find_61_binary_probes"] == [47, 74, 61]
assert SORT_WORST == 49 and SORT["merge_mean_exact_fraction"] == "2056/45" and SORT["information_floor"] == 45
assert (round(Q_WORST, 2), round(Q_MEAN, 2), round(Q_MISS, 2)) == (9.56, 8.91, 4.12)
assert BE["hits_worst_sort"]["first_q_ahead"] == 10 and BE["hits_mean_sort"]["first_q_ahead"] == 9
assert BE["hits_best_possible_sort_46"]["first_q_ahead"] == 9 and BE["misses_worst_sort"]["first_q_ahead"] == 5

# ---------------------------------------------------------------- inserts and the trees
assert (INS["slot"], INS["comparisons"], INS["shifts"]) == (8, 4, 8)
assert INS["shifted"] == [53, 61, 68, 74, 79, 85, 91, 97]
assert (TM["build_comparisons"], TM["build_rotations"], TM["build_flips"], TM["height"]) == (60, 10, 9, 6)
assert TM["find_61_comparisons"] == 4 and round(TM["hit_avg"], 2) == 3.69
assert TM["insert_50"] == {"comparisons": 5, "rotations": 0, "flips": 0, "shifts": 0, "height_after": 6}
assert (TM["floor_60"], TM["floor_60_comparisons"]) == (53, 5)
assert (TM["range_40_70"], TM["range_40_70_comparisons"]) == ([42, 47, 53, 61, 68], 11)
assert (PLAIN["build_comparisons"], PLAIN["height"], PLAIN["find_61_comparisons"]) == (120, 16, 10)
TREE_AFTER = TM["shape_after_50"]   # [key, colour, left, right]
PATH_50 = [21, 47, 74, 61, 53]

# ---------------------------------------------------------------- ordered queries
assert OQ["range_keys"] == [42, 47, 53, 61, 68] and OQ["range_comparisons_sorted"] == 8
assert (OQ["range_scan_visits"], OQ["range_scan_comparisons"], OQ["range_integer_probes"]) == (16, 26, 31)
assert (OQ["floor"], OQ["floor_comparisons_sorted"], OQ["floor_integer_probes"], OQ["nearest_to_60"]) == (53, 4, 8, 61)
BUCKETS = 16                         # Figure 4's labelled model: bucket = key mod 16

# ---------------------------------------------------------------- scale and writes
SCALE_ROWS = SCALE["rows"]
assert [round(r["q_hits"], 2) for r in SCALE_ROWS][:: 2] == [9.56, 11.73, 14.76, 18.31, 22.11, 26.04, 30.01, 34.0, 38.0]
assert round(SCALE_ROWS[-1]["q_misses"], 2) == 19.0 and SCALE_ROWS[-1]["n"] == 1 << 20
WRITE_ROWS = WRITES["rows"]


def writes(price, kind):
    """(n, writes per read at break-even) for 'array' or 'tree' at one write price."""
    return [(r["n"], r[f"{kind}_writes_per_read"]) for r in WRITE_ROWS if r["write_price"] == price]


assert [round(v, 2) for _, v in writes(1.0, "array")] == [0.42, 0.72, 0.89, 0.96, 0.99, 1.0, 1.0]
assert [round(v, 1) for _, v in writes(1.0, "tree")] == [0.9, 3.3, 11.6, 40.3, 140.6, 495.8, 1770.5]
assert round(writes(0.1, "array")[-1][1], 2) == 9.95
assert round(next(r for r in WRITE_ROWS if r["n"] == 16 and r["write_price"] == 1.0)["array_w_star"], 3) == 0.297

# ---------------------------------------------------------------- flooding
COLL, SPREAD = FLOOD["colliding"], FLOOD["spread"]
assert COLL["insert_eq_calls"] == [0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 11, 12, 13, 14, 15]
assert (COLL["insert_total"], sum(COLL["one_list_model"]), SPREAD["insert_total"]) == (128, 120, 0)
assert (COLL["lookup_97_eq_calls"], SPREAD["lookup_97_eq_calls"]) == (16, 1)
assert (COLL["lookup_61_eq_calls"], SPREAD["lookup_61_eq_calls"]) == (10, 1)
assert FLOOD["replay_matches_cpython"] and FLOOD["growth"][-1]["eq_calls"] == 524600


def cumulative(xs):
    out, t = [], 0
    for x in xs:
        t += x
        out.append(t)
    return out

# ---------------------------------------------------------------- cited, not counted
BEST_SORT_16 = 46        # S(16): Stober & Weiß, ALENEX 2023 (ledger L01); the lab prices it, it cannot count it
assert BE["hits_best_possible_sort_46"]["first_q_ahead"] == 9 and SORT["information_floor"] == BEST_SORT_16 - 1
