#!/usr/bin/env python3
"""Count what a sorted array, a red-black tree and a hash table cost on 16 keys, and when each pays.

Lab for "Hash Map, Sorted Array or Tree? When Each Pays for Itself", part 2 of Search
Algorithms: The Price of the Skip. Standard library only; every count is deterministic.

    python pays_for_itself.py worked     # the 16-key worked example: scan, sort, tree, hash
    python pays_for_itself.py scale      # lookups that repay a sort, 16 keys to 2**20 (--max-exp)
    python pays_for_itself.py writes     # the write share past which keeping keys sorted loses
    python pays_for_itself.py flood      # 16 keys with one shared hash, in CPython's own dict
    python pays_for_itself.py all        # all four, rewriting captures.json (or --out FILE)

The unit is one comparison: one call to the key comparison function, whatever it returns. A shift
moves one existing array element one slot. Every count that depends on a convention says which.
"""

import argparse
import json
import math
import platform
import random
import sys
from datetime import datetime, timezone
from fractions import Fraction
from functools import cache
from itertools import combinations
from pathlib import Path

KEYS = [3, 9, 14, 21, 28, 35, 42, 47, 53, 61, 68, 74, 79, 85, 91, 97]  # part 1's 16 keys
TARGET = 61
NEW_KEY = 50
RANGE = (40, 70)
FLOOR_OF = 60


class Counter:
    """The one unit of cost: a call to cmp, which returns -1, 0 or 1 like compareTo."""

    def __init__(self):
        self.n = 0

    def cmp(self, a, b):
        self.n += 1
        return (a > b) - (a < b)


def counted(fn, *args):
    """Run fn with a fresh counter and return (result, comparisons)."""
    c = Counter()
    return fn(*args, c), c.n


# ---------------------------------------------------------------- scan and binary search

def scan(a, x, c):
    """Linear scan: probe each slot in turn until one equals x."""
    for i, v in enumerate(a):
        if c.cmp(v, x) == 0:
            return i
    return None


def closed_search(a, x, c):
    """Part 1's prose procedure: closed interval, floor midpoint, three-way test per probe."""
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        r = c.cmp(a[mid], x)
        if r == 0:
            return mid
        if r < 0:
            lo = mid + 1
        else:
            hi = mid - 1
    return None


def lower_bound(a, x, c):
    """First index whose value is >= x (bisect_left); two-way, no equality exit."""
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if c.cmp(a[mid], x) < 0:
            lo = mid + 1
        else:
            hi = mid
    return lo


def upper_bound(a, x, c):
    """First index whose value is > x (bisect_right)."""
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if c.cmp(x, a[mid]) < 0:
            hi = mid
        else:
            lo = mid + 1
    return lo


def gap_probes(a):
    """One absent value per gap: below the first key, between neighbours, above the last."""
    return [a[0] - 1] + [(a[i] + a[i + 1]) // 2 for i in range(len(a) - 1)] + [a[-1] + 1]


# ---------------------------------------------------------------- merge sort

def merge_sort(a, c):
    """Top-down merge sort: split at len // 2, merge stably (the left run wins ties)."""
    if len(a) <= 1:
        return list(a)
    mid = len(a) // 2
    left, right = merge_sort(a[:mid], c), merge_sort(a[mid:], c)
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if c.cmp(right[j], left[i]) < 0:
            out.append(right[j])
            j += 1
        else:
            out.append(left[i])
            i += 1
    return out + left[i:] + right[j:]


def unmerge(a):
    """An order that makes every merge alternate to its last element: merge sort's worst case."""
    if len(a) <= 1:
        return list(a)
    mid = len(a) // 2
    evens, odds = a[0::2], a[1::2]  # sizes mid and len - mid when len is even or odd
    left, right = (evens, odds) if len(evens) == mid else (odds, evens)
    return unmerge(left) + unmerge(right)


def merge_worst(n):
    """Flajolet & Golin's Theorem 1 at integer lg n: n*ceil(lg n) - 2**ceil(lg n) + 1."""
    k = (n - 1).bit_length()
    return n * k - (1 << k) + 1


def merge_expected(p, v):
    """Exact mean comparisons to merge two sorted runs of p and v keys, every interleaving equally likely."""
    total = 0
    for spots in combinations(range(p + v), p):  # positions of the left run in the merged order
        left_at = set(spots)
        last_left, last_right = max(spots), max(set(range(p + v)) - left_at)
        # The merge stops comparing when one run is empty: after the earlier of the two runs' last keys.
        total += min(last_left, last_right) + 1
    return Fraction(total, math.comb(p + v, p))


@cache
def merge_sort_expected(n):
    """Exact mean comparisons of merge_sort over all n! orders, merge by merge."""
    if n <= 1:
        return Fraction(0)
    mid = n // 2
    return merge_sort_expected(mid) + merge_sort_expected(n - mid) + merge_expected(mid, n - mid)


@cache
def binary_totals(s):
    """(comparisons summed over the s keys, summed over the s + 1 gaps) for closed_search on s keys."""
    if s == 0:
        return (0, 0)
    lh, lm = binary_totals((s - 1) // 2)
    rh, rm = binary_totals(s // 2)
    return (s + lh + rh, s + 1 + lm + rm)  # every target pays the middle probe, then recurses


# ---------------------------------------------------------------- java.util.TreeMap, transliterated

RED, BLACK = False, True  # TreeMap's own encoding


class Entry:
    __slots__ = ("key", "left", "right", "parent", "color")

    def __init__(self, key, parent):
        self.key, self.left, self.right, self.parent, self.color = key, None, None, parent, BLACK


def color_of(p):
    return BLACK if p is None else p.color


def parent_of(p):
    return None if p is None else p.parent


def left_of(p):
    return None if p is None else p.left


def right_of(p):
    return None if p is None else p.right


class TreeMapPort:
    """put, get, ceiling, higher, floor and subMap iteration from OpenJDK 25's TreeMap.java.

    Rebalancing is the CLR algorithm TreeMap uses. The counters record what one insert costs
    beyond its search: rotations, and colour flips (a red uncle: three nodes change colour and
    the violation moves two levels up).
    """

    def __init__(self, c):
        self.c, self.root = c, None
        self.rotations = self.flips = 0

    def put(self, key):
        t = self.root
        if t is None:
            self.c.cmp(key, key)  # addEntryToEmptyMap: compare(key, key) as a type and null check
            self.root = Entry(key, None)
            return
        while True:
            parent = t
            r = self.c.cmp(key, t.key)
            if r < 0:
                t = t.left
            elif r > 0:
                t = t.right
            else:
                return  # key present: TreeMap replaces the value, nothing moves
            if t is None:
                break
        e = Entry(key, parent)
        if r < 0:
            parent.left = e
        else:
            parent.right = e
        self._fix_after_insertion(e)

    def _rotate_left(self, p):
        self.rotations += 1
        r = p.right
        p.right = r.left
        if r.left is not None:
            r.left.parent = p
        r.parent = p.parent
        if p.parent is None:
            self.root = r
        elif p.parent.left is p:
            p.parent.left = r
        else:
            p.parent.right = r
        r.left, p.parent = p, r

    def _rotate_right(self, p):
        self.rotations += 1
        l = p.left
        p.left = l.right
        if l.right is not None:
            l.right.parent = p
        l.parent = p.parent
        if p.parent is None:
            self.root = l
        elif p.parent.right is p:
            p.parent.right = l
        else:
            p.parent.left = l
        l.right, p.parent = p, l

    def _fix_after_insertion(self, x):
        x.color = RED
        while x is not None and x is not self.root and x.parent.color == RED:
            gp = parent_of(parent_of(x))
            if parent_of(x) is left_of(gp):
                y = right_of(gp)
                if color_of(y) == RED:  # red uncle: colour flip, continue two levels up
                    self.flips += 1
                    parent_of(x).color, y.color, gp.color = BLACK, BLACK, RED
                    x = gp
                else:
                    if x is right_of(parent_of(x)):
                        x = parent_of(x)
                        self._rotate_left(x)
                    parent_of(x).color = BLACK
                    parent_of(parent_of(x)).color = RED
                    self._rotate_right(parent_of(parent_of(x)))
            else:
                y = left_of(gp)
                if color_of(y) == RED:
                    self.flips += 1
                    parent_of(x).color, y.color, gp.color = BLACK, BLACK, RED
                    x = gp
                else:
                    if x is left_of(parent_of(x)):
                        x = parent_of(x)
                        self._rotate_right(x)
                    parent_of(x).color = BLACK
                    parent_of(parent_of(x)).color = RED
                    self._rotate_left(parent_of(parent_of(x)))
        self.root.color = BLACK

    def get(self, key):
        p = self.root
        while p is not None:
            r = self.c.cmp(key, p.key)
            if r < 0:
                p = p.left
            elif r > 0:
                p = p.right
            else:
                return p
        return None

    def ceiling(self, key):
        p = self.root
        while p is not None:
            r = self.c.cmp(key, p.key)
            if r < 0:
                if p.left is None:
                    return p
                p = p.left
            elif r > 0:
                if p.right is None:
                    return self._up_from_right(p)
                p = p.right
            else:
                return p
        return None

    def higher(self, key):
        p = self.root
        while p is not None:
            if self.c.cmp(key, p.key) < 0:
                if p.left is None:
                    return p
                p = p.left
            else:
                if p.right is None:
                    return self._up_from_right(p)
                p = p.right
        return None

    def floor(self, key):
        p = self.root
        while p is not None:
            r = self.c.cmp(key, p.key)
            if r > 0:
                if p.right is None:
                    return p
                p = p.right
            elif r < 0:
                if p.left is None:
                    parent, ch = p.parent, p
                    while parent is not None and ch is parent.left:
                        ch, parent = parent, parent.parent
                    return parent
                p = p.left
            else:
                return p
        return None

    @staticmethod
    def _up_from_right(p):
        parent, ch = p.parent, p
        while parent is not None and ch is parent.right:
            ch, parent = parent, parent.parent
        return parent

    @staticmethod
    def successor(t):
        if t.right is not None:
            p = t.right
            while p.left is not None:
                p = p.left
            return p
        return TreeMapPort._up_from_right(t)

    def sub_map(self, lo, hi):
        """Iterate subMap(lo, true, hi, true): the constructor's check, absLowest, absHighFence."""
        if self.c.cmp(lo, hi) > 0:
            raise ValueError("fromKey > toKey")
        e = self.ceiling(lo)  # absLowest()
        if e is not None and self.c.cmp(e.key, hi) > 0:  # tooHigh(e.key)
            e = None
        fence = self.higher(hi)  # absHighFence(); the iterator then stops by reference, no compare
        out = []
        while e is not None and e is not fence:
            out.append(e.key)
            e = self.successor(e)
        return out

    def depth_of(self, key):
        d, p = 1, self.root
        while p.key != key:
            p = p.left if key < p.key else p.right
            d += 1
        return d

    def height(self, p="root"):
        p = self.root if p == "root" else p
        return 0 if p is None else 1 + max(self.height(p.left), self.height(p.right))

    def snapshot(self):
        """The tree as nested lists [key, colour, left, right], for the figures."""
        def walk(p):
            if p is None:
                return None
            return [p.key, "black" if p.color == BLACK else "red", walk(p.left), walk(p.right)]
        return walk(self.root)


class PlainBST:
    """A binary search tree with no balancing, for the same keys in the same order."""

    def __init__(self, c):
        self.c, self.root = c, None

    def put(self, key):
        if self.root is None:
            self.root = [key, None, None]
            return
        p = self.root
        while True:
            side = 1 if self.c.cmp(key, p[0]) < 0 else 2
            if p[side] is None:
                p[side] = [key, None, None]
                return
            p = p[side]

    def get(self, key):
        p = self.root
        while p is not None:
            r = self.c.cmp(key, p[0])
            if r == 0:
                return p
            p = p[1] if r < 0 else p[2]
        return None

    def height(self):
        def h(p):
            return 0 if p is None else 1 + max(h(p[1]), h(p[2]))
        return h(self.root)


def build_treemap(keys):
    c = Counter()
    tree = TreeMapPort(c)
    per_insert = []
    for k in keys:
        before = (c.n, tree.rotations, tree.flips)
        tree.put(k)
        per_insert.append({"key": k, "comparisons": c.n - before[0],
                           "rotations": tree.rotations - before[1], "flips": tree.flips - before[2]})
    return tree, c, per_insert


# ---------------------------------------------------------------- CPython's dict, flooded

class EqCalls:
    n = 0


class CollidingKey:
    """Every instance hashes to the same value, so every key lands on one probe sequence."""

    __slots__ = ("v",)

    def __init__(self, v):
        self.v = v

    def __hash__(self):
        return 42

    def __eq__(self, other):
        EqCalls.n += 1
        return isinstance(other, CollidingKey) and self.v == other.v


class SpreadKey(CollidingKey):
    """Same keys with their ordinary integer hash: the control."""

    __slots__ = ()

    def __hash__(self):
        return hash(self.v)

    def __eq__(self, other):
        EqCalls.n += 1
        return isinstance(other, SpreadKey) and self.v == other.v


def dict_inserts(cls, values):
    d, per_insert = {}, []
    for v in values:
        before = EqCalls.n
        d[cls(v)] = v
        per_insert.append(EqCalls.n - before)
    return d, per_insert


def dict_lookup(d, cls, v):
    before = EqCalls.n
    found = cls(v) in d  # a new, equal object: identity cannot short-circuit the comparison
    return found, EqCalls.n - before


def replay_probes(n, h=42):
    """Predict __eq__ calls per insert of n keys sharing hash h, from CPython 3.14's dictobject.c.

    A table of s slots holds (2s) // 3 entries (USABLE_FRACTION); a full table grows to the next
    power of two >= 3 * used (GROWTH_RATE); the first table has 8 slots (PyDict_MINSIZE). insertdict
    looks the key up in the current table, then grows, then places it. Each lookup step is
    i = (5i + perturb + 1) mod s with perturb >>= 5 (PERTURB_SHIFT) first, so the sequence can
    return to a slot it already tested and compare that key again.
    """
    def probe(size):
        mask, perturb, i = size - 1, h, h & (size - 1)
        while True:
            yield i
            perturb >>= 5
            i = (i * 5 + perturb + 1) & mask

    def place(slots, size, entry):
        for i in probe(size):
            if i not in slots:
                slots[i] = entry
                return

    size, slots, calls = 8, {}, []
    for k in range(n):
        tested = 0
        if k:  # an empty dict takes its first key without a lookup
            for i in probe(size):
                if i not in slots:
                    break
                tested += 1
        calls.append(tested)
        if k >= (2 * size) // 3:
            size = 1 << (max(8, 3 * k) - 1).bit_length()
            slots = {}
            for entry in range(k):
                place(slots, size, entry)
        place(slots, size, k)
    return calls


# ---------------------------------------------------------------- stages

def stage_worked():
    a, n = KEYS, len(KEYS)
    out = {"keys": a, "conventions": {
        "comparison": "one call to the compare function, whatever it returns",
        "binary_search": "closed interval [lo, hi], mid = (lo + hi) // 2, three-way test per probe",
        "merge_sort": "top-down, split at n // 2, stable merge",
        "tree": "java.util.TreeMap's algorithm, keys inserted in ascending order",
        "shift": "one existing element moved one slot"}}

    # Lookups. A successful scan costs the key's position + 1 in whatever order the array is in,
    # so its average over all 16 keys is (n + 1) / 2 for every order.
    scan_hits = [counted(scan, a, k)[1] for k in a]
    gaps = gap_probes(a)
    bin_hits = [counted(closed_search, a, k)[1] for k in a]
    bin_misses = [counted(closed_search, a, g)[1] for g in gaps]
    assert binary_totals(n) == (sum(bin_hits), sum(bin_misses))
    out["lookup"] = {
        "scan_hit_avg": sum(scan_hits) / n, "scan_miss": n,
        "binary_hit_avg": sum(bin_hits) / n, "binary_hit_max": max(bin_hits),
        "binary_hit_counts": dict(zip(a, bin_hits)),
        "binary_miss_avg": sum(bin_misses) / len(gaps), "binary_miss_max": max(bin_misses),
        "find_61_binary_probes": [a[i] for i in _probe_trace(a, TARGET)],
    }

    # Sorting. Worst case by construction, exact mean over all 16! orders, and a seeded sample.
    worst_order = unmerge(a)
    worst_sorted, worst = counted(merge_sort, worst_order)
    assert worst_sorted == a and worst == merge_worst(n) == 49
    exact = merge_sort_expected(n)
    rng = random.Random(2026)
    sample = []
    for _ in range(20000):
        order = a[:]
        rng.shuffle(order)
        sample.append(counted(merge_sort, order)[1])
    floor_bits = (math.factorial(n) - 1).bit_length()  # ceil(log2 16!) without floating point
    out["sort"] = {
        "merge_worst": worst, "merge_worst_order": worst_order,
        "merge_mean_exact": float(exact), "merge_mean_exact_fraction": str(exact),
        "merge_sample_mean": sum(sample) / len(sample), "merge_sample_min": min(sample),
        "merge_sample_max": max(sample), "merge_sample_size": len(sample), "sample_seed": 2026,
        "information_floor": floor_bits, "log2_n_factorial": math.log2(math.factorial(n)),
    }

    # Break-even: the first lookup count q with sort + q * binary <= q * scan.
    def breakeven(sort_cost, scan_cost, bin_cost):
        q = sort_cost / (scan_cost - bin_cost)
        return {"q_star": q, "first_q_ahead": math.ceil(q)}

    lk = out["lookup"]
    out["breakeven"] = {
        "hits_worst_sort": breakeven(worst, lk["scan_hit_avg"], lk["binary_hit_avg"]),
        "hits_mean_sort": breakeven(float(exact), lk["scan_hit_avg"], lk["binary_hit_avg"]),
        "hits_best_possible_sort_46": breakeven(46, lk["scan_hit_avg"], lk["binary_hit_avg"]),
        "misses_worst_sort": breakeven(worst, lk["scan_miss"], lk["binary_miss_avg"]),
        "misses_mean_sort": breakeven(float(exact), lk["scan_miss"], lk["binary_miss_avg"]),
        "cumulative": [{"q": q, "scan": q * lk["scan_hit_avg"],
                        "sorted_worst": worst + q * lk["binary_hit_avg"],
                        "sorted_mean": float(exact) + q * lk["binary_hit_avg"]} for q in range(0, 21)],
    }

    # Writes into the sorted array: find the slot, then shift everything after it.
    slot, find_slot = counted(upper_bound, a, NEW_KEY)
    lb_gaps = [counted(lower_bound, a, g)[1] for g in gaps]
    out["sorted_array_insert_50"] = {
        "slot": slot, "comparisons": find_slot, "shifts": n - slot,
        "shifted": a[slot:], "avg_shifts_over_gaps": sum(n - i for i in range(n + 1)) / (n + 1),
        "lower_bound_avg_over_gaps": sum(lb_gaps) / len(lb_gaps)}

    # The red-black tree TreeMap builds when the same keys arrive in ascending order.
    tree, c, per_insert = build_treemap(a)
    build_cmp, build_rot, build_flips = c.n, tree.rotations, tree.flips
    depths = {k: tree.depth_of(k) for k in a}
    shape_before = tree.snapshot()
    c.n = 0
    assert tree.get(TARGET).key == TARGET
    find_61 = c.n
    tree_hits = []
    for k in a:
        c.n = 0
        tree.get(k)
        tree_hits.append(c.n)
    c.n = 0
    floor_60 = tree.floor(FLOOR_OF).key
    floor_cmp = c.n
    c.n = 0
    in_range = tree.sub_map(*RANGE)
    range_cmp = c.n
    tree_misses = []
    for g in gaps:
        c.n = 0
        assert tree.get(g) is None
        tree_misses.append(c.n)
    c.n, r0, f0 = 0, tree.rotations, tree.flips
    tree.put(NEW_KEY)
    out["treemap"] = {
        "build_comparisons": build_cmp, "build_rotations": build_rot, "build_flips": build_flips,
        "per_insert": per_insert, "height": max(depths.values()), "depths": depths,
        "find_61_comparisons": find_61, "hit_avg": sum(tree_hits) / n, "hit_max": max(tree_hits),
        "miss_avg": sum(tree_misses) / len(tree_misses), "miss_max": max(tree_misses),
        "floor_60": floor_60, "floor_60_comparisons": floor_cmp,
        "range_40_70": in_range, "range_40_70_comparisons": range_cmp,
        "insert_50": {"comparisons": c.n, "rotations": tree.rotations - r0,
                      "flips": tree.flips - f0, "shifts": 0, "height_after": tree.height()},
        "shape": shape_before, "shape_after_50": tree.snapshot(),
    }

    # The same order with no balancing: every key becomes the right child of the last.
    plain_c = Counter()
    plain = PlainBST(plain_c)
    for k in a:
        plain.put(k)
    plain_build = plain_c.n
    plain_c.n = 0
    plain.get(TARGET)
    out["plain_bst"] = {"build_comparisons": plain_build, "height": plain.height(),
                        "find_61_comparisons": plain_c.n}

    # Ordered queries on the sorted array, against what a hash set can do.
    lo_i, lo_cmp = counted(lower_bound, a, RANGE[0])
    hi_i, hi_cmp = counted(upper_bound, a, RANGE[1])
    fl_i, fl_cmp = counted(upper_bound, a, FLOOR_OF)
    scan_range = Counter()
    hits = [v for v in a if scan_range.cmp(v, RANGE[0]) >= 0 and scan_range.cmp(v, RANGE[1]) <= 0]
    out["ordered_queries"] = {
        "range": list(RANGE), "range_keys": a[lo_i:hi_i], "range_reads": hi_i - lo_i,
        "range_comparisons_sorted": lo_cmp + hi_cmp,
        "range_scan_visits": n, "range_scan_comparisons": scan_range.n, "range_scan_keys": hits,
        "range_integer_probes": RANGE[1] - RANGE[0] + 1,
        "floor_of": FLOOR_OF, "floor": a[fl_i - 1], "floor_comparisons_sorted": fl_cmp,
        "floor_integer_probes": FLOOR_OF - a[fl_i - 1] + 1,
        "nearest_to_60": min(a[fl_i - 1], a[fl_i], key=lambda v: abs(v - FLOOR_OF)),
    }
    return out


def _probe_trace(a, x):
    trace, lo, hi = [], 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        trace.append(mid)
        if a[mid] == x:
            return trace
        lo, hi = (mid + 1, hi) if a[mid] < x else (lo, mid - 1)
    return trace


def stage_scale(max_exp=20):
    """Break-even lookups per sort as n grows: measured where cheap, closed forms checked against them."""
    rows, rng = [], random.Random(1987)
    for k in range(4, max_exp + 1):
        n = 1 << k
        hit_total, miss_total = binary_totals(n)
        row = {"n": n, "sort_worst": merge_worst(n),
               "scan_hit_avg": (n + 1) / 2, "scan_miss": n,
               "binary_hit_avg": hit_total / n, "binary_miss_avg": miss_total / (n + 1)}
        if n <= 1 << 12:  # count every lookup and the worst-case sort directly; they must agree
            a = list(range(0, 2 * n, 2))
            assert sum(counted(closed_search, a, x)[1] for x in a) == hit_total
            assert sum(counted(closed_search, a, x)[1] for x in range(-1, 2 * n, 2)) == miss_total
            assert counted(merge_sort, unmerge(a))[1] == row["sort_worst"]
        if n <= 1 << 16:
            order = list(range(n))
            rng.shuffle(order)
            row["sort_one_random_order"] = counted(merge_sort, order)[1]
        row["q_hits"] = row["sort_worst"] / (row["scan_hit_avg"] - row["binary_hit_avg"])
        row["q_misses"] = row["sort_worst"] / (row["scan_miss"] - row["binary_miss_avg"])
        row["two_log2_n_minus_2"] = 2 * k - 2
        rows.append(row)
    return {"rows": rows, "sort": "merge sort worst case (Flajolet & Golin Theorem 1), counted directly to n = 4096",
            "random_order_seed": 1987}


def stage_writes(write_prices=(1.0, 0.1)):
    """The share of writes past which keeping keys sorted loses to append-and-scan, in counted units.

    Comparisons cost 1. A write (an array element moved or stored, or one tree rebalancing step:
    a new node, a rotation, a colour flip) costs write_price. Lookups are hits.
    """
    rows = []
    for n, write_price in [(1 << k, w) for k in range(4, 17, 2) for w in write_prices]:
        hit_total, _ = binary_totals(n)
        bin_hit, lb, scan_hit = hit_total / n, _mean_lower_bound(n), (n + 1) / 2
        if n == len(KEYS):
            assert lb == sum(counted(lower_bound, KEYS, g)[1] for g in gap_probes(KEYS)) / (n + 1)
        append = write_price  # store the new element at the end
        sorted_insert = lb + write_price * (n / 2 + 1)  # find the slot, shift n/2 on average, store

        tree, c, _ = build_treemap(list(range(0, 2 * n, 2)))  # ascending, as in the worked example
        c.n = 0
        for k in range(0, 2 * n, 2):
            tree.get(k)
        tree_hit = c.n / n
        c.n = 0
        for g in range(-1, 2 * n, 2):  # an insert searches exactly as a miss does, then adds a node
            tree.get(g)
        tree_path = c.n / (n + 1)
        # Rebalancing per insert, averaged over the whole build: Tarjan's O(1) amortised bound, counted.
        tree_insert = tree_path + write_price * (1 + (tree.rotations + tree.flips) / n)

        def w_star(gain, loss):  # keep-sorted wins while (1 - w) * gain > w * loss
            return gain / (gain + loss)

        array_w = w_star(scan_hit - bin_hit, sorted_insert - append)
        tree_w = w_star(scan_hit - tree_hit, tree_insert - append)
        rows.append({"n": n, "write_price": write_price,
                     "scan_hit_avg": scan_hit, "binary_hit_avg": bin_hit, "lower_bound_avg": lb,
                     "sorted_insert_cost": sorted_insert, "tree_hit_avg": tree_hit,
                     "tree_insert_path": tree_path, "tree_insert_cost": tree_insert,
                     "tree_rotations_per_insert": tree.rotations / n, "tree_flips_per_insert": tree.flips / n,
                     "array_w_star": array_w, "array_writes_per_read": array_w / (1 - array_w),
                     "tree_w_star": tree_w, "tree_writes_per_read": tree_w / (1 - tree_w)})
    return {"rows": rows, "model": "append-and-scan against keep-sorted (array or TreeMap, ascending inserts); "
                                   "hits only; comparisons cost 1, each write costs write_price"}


def _mean_lower_bound(n):
    """Mean comparisons of lower_bound over the n + 1 gaps of an n-key array (exact, by size recursion)."""
    memo = {}

    def total(s):  # comparisons summed over the s + 1 insertion points of a range of s keys
        if s == 0:
            return 0
        if s not in memo:
            left, right = s // 2, s - s // 2 - 1  # [lo, mid) keeps s // 2 keys; [mid + 1, hi) the rest
            # Gaps at or left of mid go left (s // 2 + 1 of them), the rest go right.
            memo[s] = (s + 1) + total(left) + total(right)
        return memo[s]

    return total(n) / (n + 1)


def stage_flood():
    out = {}
    for name, cls in (("colliding", CollidingKey), ("spread", SpreadKey)):
        EqCalls.n = 0
        d, per_insert = dict_inserts(cls, KEYS)
        hit, hit_eq = dict_lookup(d, cls, KEYS[-1])
        _, target_eq = dict_lookup(d, cls, TARGET)
        miss, miss_eq = dict_lookup(d, cls, 100)
        out[name] = {"insert_eq_calls": per_insert, "insert_total": sum(per_insert),
                     "lookup_61_eq_calls": target_eq, "lookup_97_eq_calls": hit_eq,
                     "lookup_absent_eq_calls": miss_eq, "found": hit, "absent_found": miss}
    out["colliding"]["one_list_model"] = list(range(len(KEYS)))  # 0, 1, ..., 15: each key meets every earlier one
    out["colliding"]["replayed"] = replay_probes(len(KEYS))
    out["colliding"]["extra_vs_model"] = [m - k for k, m in enumerate(out["colliding"]["insert_eq_calls"])]
    growth = []
    for n in (16, 64, 256, 1024):
        EqCalls.n = 0
        _, per_insert = dict_inserts(CollidingKey, range(n))
        replayed = replay_probes(n)
        growth.append({"n": n, "eq_calls": EqCalls.n, "n_n_minus_1_over_2": n * (n - 1) // 2,
                       "replay_matches": per_insert == replayed})
    out["growth"] = growth
    out["replay_matches_cpython"] = (all(g["replay_matches"] for g in growth)
                                     and out["colliding"]["replayed"] == out["colliding"]["insert_eq_calls"])
    out["python_hash_of_61"] = hash(61)
    out["hash_info_algorithm"] = sys.hash_info.algorithm
    return out


def provenance():
    cpu = "unknown CPU"
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    except OSError:
        cpu = platform.processor() or cpu
    when = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (f"Captured {when} on {cpu}, {platform.system()} {platform.release()}, "
            f"{platform.python_implementation()} {platform.python_version()}")


def report(stage, data):
    """Print the lines the article quotes."""
    if stage == "worked":
        lk, so, be = data["lookup"], data["sort"], data["breakeven"]
        print(f"worked: scan hit avg {lk['scan_hit_avg']} (miss {lk['scan_miss']}); binary hit avg "
              f"{lk['binary_hit_avg']} max {lk['binary_hit_max']}, miss avg {lk['binary_miss_avg']:.3f} "
              f"max {lk['binary_miss_max']}; 61 probes {lk['find_61_binary_probes']}")
        print(f"worked: merge sort worst {so['merge_worst']} (order {so['merge_worst_order']}), exact mean "
              f"{so['merge_mean_exact']:.4f}, sample mean {so['merge_sample_mean']:.3f} "
              f"[{so['merge_sample_min']}..{so['merge_sample_max']}] over {so['merge_sample_size']}; "
              f"floor ceil(log2 16!) = {so['information_floor']} (log2 16! = {so['log2_n_factorial']:.3f})")
        for key in ("hits_worst_sort", "hits_mean_sort", "hits_best_possible_sort_46",
                    "misses_worst_sort", "misses_mean_sort"):
            print(f"worked: break-even {key:27s} q* = {be[key]['q_star']:.3f} -> ahead from lookup "
                  f"{be[key]['first_q_ahead']}")
        ins = data["sorted_array_insert_50"]
        print(f"worked: sorted array insert 50 -> slot {ins['slot']}, {ins['comparisons']} comparisons, "
              f"{ins['shifts']} shifts {ins['shifted']}; mean shifts over gaps {ins['avg_shifts_over_gaps']}, "
              f"mean lower_bound {ins['lower_bound_avg_over_gaps']:.3f}")
        tm = data["treemap"]
        print(f"worked: TreeMap ascending build {tm['build_comparisons']} comparisons, "
              f"{tm['build_rotations']} rotations, {tm['build_flips']} flips; height {tm['height']}; "
              f"find 61 {tm['find_61_comparisons']}; hit avg {tm['hit_avg']} max {tm['hit_max']}; "
              f"miss avg {tm['miss_avg']:.3f} max {tm['miss_max']}")
        i50 = tm["insert_50"]
        print(f"worked: TreeMap insert 50 -> {i50['comparisons']} comparisons, {i50['rotations']} rotations, "
              f"{i50['flips']} flips, 0 shifts, height after {i50['height_after']}; floor(60) = "
              f"{tm['floor_60']} in {tm['floor_60_comparisons']}; subMap[40,70] {tm['range_40_70']} in "
              f"{tm['range_40_70_comparisons']} comparisons")
        pb = data["plain_bst"]
        print(f"worked: plain BST ascending build {pb['build_comparisons']} comparisons, height "
              f"{pb['height']}, find 61 {pb['find_61_comparisons']}")
        oq = data["ordered_queries"]
        print(f"worked: range {oq['range']} -> {oq['range_keys']} with {oq['range_comparisons_sorted']} "
              f"comparisons + {oq['range_reads']} reads; scan visits {oq['range_scan_visits']} "
              f"({oq['range_scan_comparisons']} comparisons); integer probes {oq['range_integer_probes']}")
        print(f"worked: largest <= {oq['floor_of']} is {oq['floor']} in {oq['floor_comparisons_sorted']} "
              f"comparisons; integer probes {oq['floor_integer_probes']}; nearest to 60 {oq['nearest_to_60']}")
    elif stage == "scale":
        for r in data["rows"]:
            rnd = r.get("sort_one_random_order", "-")
            print(f"scale: n={r['n']:>8} sort worst {r['sort_worst']:>9} (random {rnd!s:>8}) "
                  f"binary hit {r['binary_hit_avg']:6.3f} miss {r['binary_miss_avg']:6.3f} "
                  f"q* hits {r['q_hits']:6.2f} misses {r['q_misses']:5.2f} (2 lg n - 2 = {r['two_log2_n_minus_2']})")
    elif stage == "writes":
        for r in data["rows"]:
            print(f"writes: n={r['n']:>6} write price {r['write_price']}: array insert "
                  f"{r['sorted_insert_cost']:.1f}, lookup {r['binary_hit_avg']:.2f} -> wins below "
                  f"{100 * r['array_w_star']:.1f}% writes ({r['array_writes_per_read']:.2f} per read); "
                  f"TreeMap insert {r['tree_insert_cost']:.2f} ({r['tree_rotations_per_insert']:.2f} rot, "
                  f"{r['tree_flips_per_insert']:.2f} flips), lookup {r['tree_hit_avg']:.2f} -> wins below "
                  f"{100 * r['tree_w_star']:.2f}% writes ({r['tree_writes_per_read']:.1f} per read); "
                  f"scan {r['scan_hit_avg']}")
    elif stage == "flood":
        for name in ("colliding", "spread"):
            f = data[name]
            print(f"flood: {name:9s} insert __eq__ calls {f['insert_eq_calls']} total {f['insert_total']}; "
                  f"lookup 61 {f['lookup_61_eq_calls']}, 97 {f['lookup_97_eq_calls']}, "
                  f"absent {f['lookup_absent_eq_calls']}")
        print(f"flood: extra over the one-list model {data['colliding']['extra_vs_model']}; probe replay "
              f"matches CPython: {data['replay_matches_cpython']}")
        print("flood: growth " + ", ".join(f"n={g['n']} {g['eq_calls']} (n(n-1)/2 {g['n_n_minus_1_over_2']})"
                                            for g in data["growth"]))
        print(f"flood: hash(61) = {data['python_hash_of_61']}; str/bytes hash = {data['hash_info_algorithm']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("stage", choices=("worked", "scale", "writes", "flood", "all"))
    ap.add_argument("--out", default="captures.json", help="where to write (default: captures.json)")
    ap.add_argument("--write-price", type=float, default=None,
                    help="writes stage: price one write (a shift, a store, a rotation) at this many comparisons "
                         "instead of the default pair 1 and 0.1")
    ap.add_argument("--max-exp", type=int, default=20, help="scale stage: run n up to 2**MAX_EXP (default 20)")
    args = ap.parse_args()

    line = provenance()
    print(line)
    out_path = Path(args.out)
    data = {}
    if args.stage != "all" and out_path.exists():
        data = json.loads(out_path.read_text())  # one stage updates its own section only
    data["provenance"] = line
    prices = (1.0, 0.1) if args.write_price is None else (args.write_price,)
    stages = {"worked": stage_worked, "scale": lambda: stage_scale(args.max_exp),
              "writes": lambda: stage_writes(prices), "flood": stage_flood}
    for name in (stages if args.stage == "all" else [args.stage]):
        data[name] = stages[name]()
        report(name, data[name])
    out_path.write_text(json.dumps(data, indent=1) + "\n")
    print(f"wrote {out_path.name}")


if __name__ == "__main__":
    main()
