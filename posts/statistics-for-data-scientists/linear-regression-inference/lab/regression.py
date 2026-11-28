#!/usr/bin/env python3
"""Lab for "Linear Regression by Hand: Every Number in the Summary" (Statistics for Data Scientists, part 13).

Every number the article calls computed or measured comes from a run of this file. Each stage prints its numbers and
writes them under its own key in the capture file.

    python regression.py all --out mine.json                  # every stage, the article's budget (about a minute)
    python regression.py all --quick --out quick.json         # the reader's budget: fewer simulated replications
    python regression.py nist --out mine.json                 # one stage
    python regression.py nist --quick --year-origin 1954 --out e3.json    # E3: Longley's year measured from 1954
    python regression.py summary --quick --fault --out e4.json            # E4: an earlier draft of the summary stage

Stages:
    example      Part 8's tests rebuilt as regressions: the sleep data with a drug dummy (Student's t) and with patient
                 dummies added (the paired t); PlantGrowth's factor and the nested-model F that one-way ANOVA is
    nist         NIST's Statistical Reference Datasets: exact rational least squares against the certified values, then
                 QR, the normal equations, SVD solvers and the library defaults scored in log relative error (LRE);
                 condition numbers; Filip's failures; the data's own rounding (Beaton, Rubin and Barone)
    summary      every number in statsmodels' and R's summary of Longley's regression, recomputed from the design
                 matrix and matched to both; joint F tests and the joint confidence region for GNP and Year
    meaning      what a coefficient measures: partialling out (Frisch-Waugh-Lovell), omitted-variable bias as an exact
                 identity, variance inflation factors, and condition numbers before and after centring
    interaction  ToothGrowth: an interaction of supplement and dose, and how the supplement coefficient moves with the
                 dose's origin while the interaction does not
    intervals    the confidence interval for a mean response against the prediction interval for a new animal, and how
                 often each covers, simulated from the fitted model
    conditions   the guarantee measured: coverage of the slope's 95% interval under six conditions and six sample sizes,
                 and the prediction interval's two tails under skewed errors

NIST's files are downloaded once into .nist/ beside this script and checked against SHA-256 hashes; they are not
redistributed. Simulated rates print with their Monte Carlo standard error (MCSE). Each simulation draws from its own
stream, SeedSequence([stage, sub-stream, seed]).
"""

import argparse
import datetime
import hashlib
import json
import math
import pathlib
import platform
import re
import time
import urllib.request
import warnings
from decimal import ROUND_HALF_UP, Decimal, getcontext
from fractions import Fraction

import numpy as np
import scipy
import scipy.linalg as sla
from scipy import stats

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "data"
NIST_DIR = HERE / ".nist"
R_CSV = HERE / "crosscheck-R.csv"
STAGES = ("example", "nist", "summary", "meaning", "interaction", "intervals", "conditions")

# Budgets. The article quotes FULL; --quick is the reader's first run. Exact quantities ignore the budget.
FULL = dict(cond_reps=20000, pi_reps=20000, cover_reps=20000, rounding_reps=20000)
QUICK = dict(cond_reps=2000, pi_reps=2000, cover_reps=2000, rounding_reps=2000)
CHUNK = 2000                    # simulated replications per block, to keep memory small at n = 1,000
LEVEL = 0.95

NIST_URL = "https://www.itl.nist.gov/div898/strd/lls/data/LINKS/DATA/{}.dat"
NIST_SHA256 = {
    "Norris": "5ab6906c68a9c4b2eb1661c0cd7d2a09f5a469a6d4e05b6b691f190f5f7b944f",
    "Pontius": "de60baa5dc66fd804f9316f895bc5aa2b8f791c09d1ecc1ec39f8b199b8c15c7",
    "NoInt1": "d8234c428dedaa9de23b67df7d04aeee83befae73ceb6b38321b224955a9b667",
    "NoInt2": "a71c2810b1edcef8fec6b864c20c5f9d9908e530282a174772ce610999ca7c69",
    "Filip": "403b34689e401d915cb28bd69311d3ca5c3007d88d3b670b00e3203042315072",
    "Longley": "fc4b0c824f8f0b834eb8e7d1c4c7e0b3cebdd7987bcb085e8f5e1007582480ea",
    "Wampler1": "8bcd6f00dbe8c307ebc5c971e12b950eb3cdb75afbc2b38573082b5fcb0d7fbc",
    "Wampler2": "01ba5f08b5b9f84431f3754216e006939a80264a1caa69fe08b3cbc543f9ee3e",
    "Wampler3": "c5b025f6ebf0365de92d80e478ad826b01a6dfdafb71964ea8bae7eec993ce53",
    "Wampler4": "dcff32075a52ecf31af70dad340776237544b1a29b5034a40f8b3e6b607cf9c1",
    "Wampler5": "c4e260a6638db61287bfea75a2dd3b324c86c5d40931ddc6d8fab0c0305ffa39",
}
# (kind, degree, intercept): the model each file certifies.
NIST_MODEL = {"Norris": ("poly", 1, True), "Pontius": ("poly", 2, True), "NoInt1": ("poly", 1, False),
              "NoInt2": ("poly", 1, False), "Filip": ("poly", 10, True), "Longley": ("multi", 6, True),
              "Wampler1": ("poly", 5, True), "Wampler2": ("poly", 5, True), "Wampler3": ("poly", 5, True),
              "Wampler4": ("poly", 5, True), "Wampler5": ("poly", 5, True)}
LONGLEY_NAMES = ["const", "Deflator", "GNP", "Unemployed", "Armed", "Population", "Year"]
WAMPLER_LONGLEY_CONDITION = 2.361e19   # Wampler (1969), the eigenvalue ratio of Longley's X'X, as printed
# Half a unit in the last printed digit of each Longley column (deflator to 0.1, the counts to 1; the year is exact).
LONGLEY_HALF_UNIT = np.array([0.0, 0.05, 0.5, 0.5, 0.5, 0.5, 0.0])
TG_NEW_DOSE = 1.5               # mg/day, the new animal of the intervals stage


# ------------------------------------------------------------------------------- small helpers
def stream(seed, stage, sub=0):
    """An independent generator for (stage, sub-stream): varying ids first, the root seed last."""
    return np.random.default_rng(np.random.SeedSequence([STAGES.index(stage), sub, seed]))


def r6(x):
    """Round for the capture file: floats to six significant digits, recursively (exact checks keep full digits)."""
    if isinstance(x, dict):
        return {str(k): r6(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, np.ndarray)):
        return [r6(v) for v in x]
    if isinstance(x, (float, np.floating)):
        x = float(x)
        return x if not math.isfinite(x) or x == 0 else float(f"{x:.6g}")
    if isinstance(x, (np.integer, np.bool_)):
        return int(x)
    return x


def full(x):
    """Mark a float to be kept at full precision in the capture (r6 leaves strings alone)."""
    return repr(float(x))


def sha1(path):
    return hashlib.sha1(path.read_bytes()).hexdigest()[:12]


def hu(x, nd=4):
    """A number rounded half up from its decimal value."""
    return str(Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def pc(share, nd=1):
    """A share as a percentage, rounded half up from its decimal value."""
    return str((Decimal(repr(float(share))) * 100).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def mcse_share(p, reps):
    return math.sqrt(max(p * (1 - p), 0.0) / reps)


def lre(x, c, cap=15.0):
    """Log relative error: correct significant digits of x against certified c (absolute error when c = 0)."""
    if x is None or not math.isfinite(x):
        return float("nan")
    if x == c:
        return cap
    err = abs(x - c) / abs(c) if c != 0 else abs(x)
    return min(cap, -math.log10(err))


def kappa(X):
    s = np.linalg.svd(X, compute_uv=False)
    return float(s[0] / s[-1])


def kappa_scaled(X):
    return kappa(X / np.linalg.norm(X, axis=0))


def read_csv(path):
    rows = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    head = rows[0].split(",")
    return [dict(zip(head, ln.split(","))) for ln in rows[1:]]


def r_values():
    """The private R check (crosscheck.R) as {key: float}, or {} when it has not been run."""
    if not R_CSV.exists():
        return {}
    out = {}
    for row in read_csv(R_CSV):
        v = row["value"].strip()
        out[row["key"]] = float(v) if v not in ("NA", "") else float("nan")
    return out


def max_rel(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.max(np.abs(a - b) / np.maximum(np.abs(b), 1e-300)))


# ------------------------------------------------------------------------------- least squares, from the design matrix
def ols(X, y, names=None, intercept=True):
    """Ordinary least squares by Householder QR, with every number a regression summary prints.

    X is n x p and includes the column of ones when intercept is True. Coefficients solve R b = Q'y; the variance
    estimate divides the residual sum of squares by n - p; standard errors are sqrt(diag(s^2 (X'X)^-1)), with
    (X'X)^-1 = R^-1 R^-T so that X'X is never formed.
    """
    n, p = X.shape
    Q, R = np.linalg.qr(X)
    b = sla.solve_triangular(R, Q.T @ y)
    fitted = X @ b
    e = y - fitted
    rss = float(e @ e)
    df_resid = n - p
    s2 = rss / df_resid
    Rinv = sla.solve_triangular(R, np.eye(p))
    XtXi = Rinv @ Rinv.T
    se = np.sqrt(s2 * np.diag(XtXi))
    t = b / se
    pval = 2 * stats.t.sf(np.abs(t), df_resid)
    tq = stats.t.ppf(0.5 + LEVEL / 2, df_resid)
    ybar = float(y.mean())
    tss = float(((y - ybar) ** 2).sum()) if intercept else float(y @ y)
    k_slopes = p - 1 if intercept else p
    r2 = 1 - rss / tss
    adj = 1 - (1 - r2) * (n - (1 if intercept else 0)) / df_resid
    fval = ((tss - rss) / k_slopes) / s2 if k_slopes > 0 else float("nan")
    fp = float(stats.f.sf(fval, k_slopes, df_resid)) if k_slopes > 0 else float("nan")
    llf = -n / 2 * (math.log(2 * math.pi) + math.log(rss / n) + 1)      # Gaussian log-likelihood at the MLE
    lev = np.einsum("ij,ij->i", X @ XtXi, X)                             # diagonal of the hat matrix
    return dict(n=n, p=p, names=names or [f"x{j}" for j in range(p)], b=b, se=se, t=t, p_value=pval,
                ci_lo=b - tq * se, ci_hi=b + tq * se, t_quantile=tq, fitted=fitted, resid=e, rss=rss, tss=tss,
                ess=tss - rss, df_resid=df_resid, df_model=k_slopes, s2=s2, sigma=math.sqrt(s2), r2=r2, adj_r2=adj,
                F=fval, F_p=fp, llf=llf, aic_mean_only=-2 * llf + 2 * p, bic_mean_only=-2 * llf + math.log(n) * p,
                aic_with_sigma=-2 * llf + 2 * (p + 1), bic_with_sigma=-2 * llf + math.log(n) * (p + 1),
                XtXi=XtXi, leverage=lev, kappa=kappa(X))


def nested_F(rss_r, df_r, rss_f, df_f):
    """F for a restricted model (rss_r on df_r residual df) against a full one (rss_f on df_f)."""
    q = df_r - df_f
    F = ((rss_r - rss_f) / q) / (rss_f / df_f)
    return F, q, float(stats.f.sf(F, q, df_f))


def residual_diagnostics(e, X):
    """The block under statsmodels' coefficient table, by hand (Omnibus via SciPy's normaltest, as statsmodels does)."""
    n = len(e)
    m2 = float(np.mean((e - e.mean()) ** 2))
    skew = float(np.mean((e - e.mean()) ** 3)) / m2 ** 1.5
    kurt = float(np.mean((e - e.mean()) ** 4)) / m2 ** 2            # not excess: a normal sample gives about 3
    jb = n / 6 * (skew ** 2 + (kurt - 3) ** 2 / 4)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")                              # SciPy warns that kurtosistest wants n >= 20
        omni = stats.normaltest(e)
    dw = float(np.sum(np.diff(e) ** 2) / np.sum(e ** 2))
    return dict(skew=skew, kurtosis=kurt, jb=jb, jb_p=float(stats.chi2.sf(jb, 2)), omnibus=float(omni.statistic),
                omnibus_p=float(omni.pvalue), durbin_watson=dw, condition_number=kappa(X))


# ------------------------------------------------------------------------------- data
def read_sleep():
    rows = read_csv(DATA / "student1908_sleep.csv")
    d1 = np.array([float(r["drug_1"]) for r in rows])
    d2 = np.array([float(r["drug_2"]) for r in rows])
    return d1, d2


def read_plants():
    rows = read_csv(DATA / "plant_growth.csv")
    return [r["group"] for r in rows], np.array([float(r["weight"]) for r in rows])


def read_teeth():
    rows = read_csv(DATA / "toothgrowth.csv")
    return (np.array([float(r["len"]) for r in rows]), np.array([r["supp"] for r in rows]),
            np.array([float(r["dose"]) for r in rows]))


def nist_file(name):
    """NIST's file, downloaded once into .nist/ and checked against its SHA-256 hash."""
    NIST_DIR.mkdir(exist_ok=True)
    path = NIST_DIR / f"{name}.dat"
    if not path.exists():
        # NIST's server refuses urllib's default user agent; a plain client name is accepted.
        req = urllib.request.Request(NIST_URL.format(name), headers={"User-Agent": "regression-lab/1.0 (Python urllib)"})
        with urllib.request.urlopen(req, timeout=60) as r:
            path.write_bytes(r.read())
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != NIST_SHA256[name]:
        path.unlink()
        raise SystemExit(f"{name}.dat does not match its SHA-256 hash; deleted it, run again to download it afresh")
    return path


def read_nist(name):
    """Certified values (as exact decimal strings) and the data rows of one StRD linear regression file."""
    lines = nist_file(name).read_text(encoding="ascii").splitlines()
    cert = {"b": [], "se": []}
    for ln in lines[:60]:
        m = re.match(r"\s+B(\d+)\s+(\S+)\s+(\S+)\s*$", ln)
        if m:
            cert["b"].append(m.group(2))
            cert["se"].append(m.group(3))
        m = re.match(r"\s+Standard Deviation\s+(\S+)", ln)
        if m:
            cert["rsd"] = m.group(1)
        m = re.match(r"\s+R-Squared\s+(\S+)", ln)
        if m:
            cert["r2"] = m.group(1)
    data = [ln.split() for ln in lines[60:] if ln.split()]
    return cert, data


def nist_design(name, data, exact=False):
    """The certified model's design matrix and response, as floats or as exact Fractions."""
    kind, deg, icpt = NIST_MODEL[name]
    num = Fraction if exact else float
    y = [num(r[0]) for r in data]
    if kind == "multi":
        X = [[num(1)] + [num(v) for v in r[1:]] for r in data]
    else:
        lo = 0 if icpt else 1
        X = [[num(r[1]) ** j for j in range(lo, deg + 1)] for r in data]
    if exact:
        return X, y
    return np.array(X), np.array(y)


def exact_least_squares(X, y):
    """Least squares in exact rational arithmetic: Gauss-Jordan on the normal equations, which is exact here."""
    n, p = len(X), len(X[0])
    A = [[sum(X[k][i] * X[k][j] for k in range(n)) for j in range(p)] for i in range(p)]
    rhs = [sum(X[k][i] * y[k] for k in range(n)) for i in range(p)]
    M = [A[i][:] + [rhs[i]] + [Fraction(int(i == j)) for j in range(p)] for i in range(p)]
    for c in range(p):
        piv = next(r for r in range(c, p) if M[r][c] != 0)
        M[c], M[piv] = M[piv], M[c]
        pv = M[c][c]
        M[c] = [v / pv for v in M[c]]
        for r in range(p):
            if r != c and M[r][c] != 0:
                f = M[r][c]
                M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    b = [M[i][p] for i in range(p)]
    inv_diag = [M[i][p + 1 + i] for i in range(p)]
    resid = [y[k] - sum(X[k][j] * b[j] for j in range(p)) for k in range(n)]
    rss = sum(r * r for r in resid)
    return b, inv_diag, rss, n - p


def to15(q):
    """An exact rational rounded half-even to 15 significant digits, as a Decimal (NIST prints 15)."""
    getcontext().prec = 80
    d = Decimal(q.numerator) / Decimal(q.denominator)
    if d == 0:
        return Decimal(0)
    return Decimal(f"{d:.14E}")


def sqrt15(q):
    getcontext().prec = 80
    d = (Decimal(q.numerator) / Decimal(q.denominator)).sqrt()
    return Decimal(0) if d == 0 else Decimal(f"{d:.14E}")


# ------------------------------------------------------------------------------- stage: example
def stage_example(cfg, args):
    import statsmodels.api as sm
    rv = r_values()
    out = {}
    d1, d2 = read_sleep()
    y = np.concatenate([d1, d2])
    drug = np.r_[np.zeros(10), np.ones(10)]
    patient = np.r_[np.arange(10), np.arange(10)]
    X1 = np.column_stack([np.ones(20), drug])
    f1 = ols(X1, y, ["const", "drug2"])
    print("Sleep data as a regression of extra hours on a drug-2 dummy (Student's ten patients, both drugs):")
    xtx, xty = X1.T @ X1, X1.T @ y
    print(f"  X'X = [[{xtx[0, 0]:g}, {xtx[0, 1]:g}], [{xtx[1, 0]:g}, {xtx[1, 1]:g}]]; X'y = [{hu(xty[0], 1)}, {hu(xty[1], 1)}]")
    print(f"  coefficients {hu(f1['b'][0])} (drug-1 mean) and {hu(f1['b'][1])} (difference in means)")
    print(f"  RSS {hu(f1['rss'])} on {f1['df_resid']} df; sigma^2 {hu(f1['s2'])}; sigma {hu(f1['sigma'])}; "
          f"(X'X)^-1 diagonal {np.round(np.diag(f1['XtXi']), 4)}")
    print(f"  SE {hu(f1['se'][1])}; t {hu(f1['t'][1])}; p {hu(f1['p_value'][1], 5)}; 95% CI {hu(f1['ci_lo'][1])} to "
          f"{hu(f1['ci_hi'][1])}; R^2 {hu(f1['r2'])}; F {hu(f1['F'])} = t^2")
    tt = stats.ttest_ind(d2, d1)                                     # SciPy's default is Student's pooled test
    print(f"  SciPy ttest_ind (Student): t {hu(tt.statistic)}, p {hu(tt.pvalue, 5)}")
    Xp = np.column_stack([np.ones(20), drug] + [(patient == k).astype(float) for k in range(1, 10)])
    f2 = ols(Xp, y, ["const", "drug2"] + [f"patient{k + 1}" for k in range(1, 10)])
    tr = stats.ttest_rel(d2, d1)
    print("Adding nine patient dummies (the paired design as a regression):")
    print(f"  coefficient {hu(f2['b'][1])}; SE {hu(f2['se'][1])}; t {hu(f2['t'][1])} on {f2['df_resid']} df; "
          f"p {hu(f2['p_value'][1], 6)}; sigma {hu(f2['sigma'])}; R^2 {hu(f2['r2'])}")
    print(f"  SciPy ttest_rel (paired): t {hu(tr.statistic)}, p {hu(tr.pvalue, 6)}")
    m1 = sm.OLS(y, X1).fit()
    m2 = sm.OLS(y, Xp).fit()
    out["sleep"] = dict(
        y=y.tolist(), drug=drug.tolist(), patient=patient.tolist(), means=[float(d1.mean()), float(d2.mean())],
        sd=[float(d1.std(ddof=1)), float(d2.std(ddof=1))], XtX=(X1.T @ X1).tolist(), Xty=(X1.T @ y).tolist(),
        XtXi=f1["XtXi"].tolist(),
        unpaired=dict(b=f1["b"].tolist(), se=f1["se"].tolist(), t=f1["t"].tolist(), p=f1["p_value"].tolist(),
                      ci=[float(f1["ci_lo"][1]), float(f1["ci_hi"][1])], rss=f1["rss"], tss=f1["tss"], ess=f1["ess"],
                      df=f1["df_resid"], s2=f1["s2"], sigma=f1["sigma"], r2=f1["r2"], adj_r2=f1["adj_r2"], F=f1["F"],
                      F_p=f1["F_p"], fitted=f1["fitted"].tolist(), resid=f1["resid"].tolist(), tq=f1["t_quantile"]),
        paired=dict(b=float(f2["b"][1]), se=float(f2["se"][1]), t=float(f2["t"][1]), p=float(f2["p_value"][1]),
                    df=f2["df_resid"], sigma=f2["sigma"], r2=f2["r2"], rss=f2["rss"], patient_effects=f2["b"][2:].tolist(),
                    intercept=float(f2["b"][0]), resid=f2["resid"].tolist()),
        scipy=dict(student_t=float(tt.statistic), student_p=float(tt.pvalue), paired_t=float(tr.statistic),
                   paired_p=float(tr.pvalue)),
        statsmodels_maxrel=dict(unpaired=max_rel(np.r_[f1["b"], f1["se"]], np.r_[m1.params, m1.bse]),
                                paired=max_rel(np.r_[f2["b"], f2["se"]], np.r_[m2.params, m2.bse])))
    # Within-patient deviations (each value minus its patient's mean), for the figure's right panel.
    pm = (d1 + d2) / 2
    out["sleep"]["within"] = (y - np.r_[pm, pm]).tolist()

    groups, w = read_plants()
    levels = ["ctrl", "trt1", "trt2"]
    g = np.array([levels.index(v) for v in groups])
    Xg = np.column_stack([np.ones(len(w)), (g == 1).astype(float), (g == 2).astype(float)])
    fg = ols(Xg, w, ["const", "trt1", "trt2"])
    f0 = ols(np.ones((len(w), 1)), w, ["const"])
    F, q, Fp = nested_F(f0["rss"], f0["df_resid"], fg["rss"], fg["df_resid"])
    ow = stats.f_oneway(*[w[g == k] for k in range(3)])
    print("PlantGrowth with a three-level factor (control as the reference level):")
    print(f"  coefficients {hu(fg['b'][0])} (control mean), {hu(fg['b'][1])} and {hu(fg['b'][2])} (differences)")
    print(f"  RSS intercept-only {hu(f0['rss'])} on {f0['df_resid']} df; with the factor {hu(fg['rss'])} on "
          f"{fg['df_resid']} df; nested F {hu(F)} on {q} and {fg['df_resid']} df, p {hu(Fp, 5)}")
    print(f"  SciPy f_oneway: F {hu(ow.statistic)}, p {hu(ow.pvalue, 5)}")
    out["plants"] = dict(b=fg["b"].tolist(), se=fg["se"].tolist(), t=fg["t"].tolist(), p=fg["p_value"].tolist(),
                         rss_full=fg["rss"], rss_null=f0["rss"], df_full=fg["df_resid"], df_null=f0["df_resid"],
                         F=F, q=q, F_p=Fp, scipy_F=float(ow.statistic), scipy_p=float(ow.pvalue),
                         means=[float(w[g == k].mean()) for k in range(3)], r2=fg["r2"])
    if rv:
        rc = dict(unpaired_t=rv.get("sleep_unpaired_t"), paired_t=rv.get("sleep_paired_t"), plants_F=rv.get("plants_F"))
        out["r_check"] = dict(values=rc, maxrel=max_rel([f1["t"][1], f2["t"][1], F], list(rc.values())))
        print(f"  R lm/anova agree to {out['r_check']['maxrel']:.1e} relative")
    return out


# ------------------------------------------------------------------------------- stage: nist
def float_solvers():
    import statsmodels.api as sm

    def householder(X, y):
        Q, R = np.linalg.qr(X)
        return sla.solve_triangular(R, Q.T @ y)

    def normal_solve(X, y):
        return np.linalg.solve(X.T @ X, X.T @ y)

    def normal_cholesky(X, y):
        return sla.cho_solve(sla.cho_factor(X.T @ X), X.T @ y)

    def normal_inverse(X, y):
        return np.linalg.inv(X.T @ X) @ (X.T @ y)

    def numpy_lstsq(X, y):
        return np.linalg.lstsq(X, y, rcond=None)[0]

    def numpy_lstsq_eps(X, y):
        return np.linalg.lstsq(X, y, rcond=-1)[0]

    def scipy_gelsd(X, y):
        return sla.lstsq(X, y)[0]

    def scipy_gelsy(X, y):
        return sla.lstsq(X, y, lapack_driver="gelsy")[0]

    def sm_default(X, y):
        return sm.OLS(y, X).fit().params

    def sm_qr(X, y):
        return sm.OLS(y, X).fit(method="qr").params

    return {"Householder QR": householder, "normal equations (LU)": normal_solve,
            "normal equations (Cholesky)": normal_cholesky, "normal equations (inverse)": normal_inverse,
            "NumPy lstsq, default rcond": numpy_lstsq, "NumPy lstsq, rcond=-1": numpy_lstsq_eps,
            "SciPy lstsq (gelsd)": scipy_gelsd, "SciPy lstsq (gelsy)": scipy_gelsy,
            "statsmodels OLS().fit()": sm_default, "statsmodels fit(method='qr')": sm_qr}


def solve_and_score(f, X, y, cert_b):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            b = np.asarray(f(X, y), float)
            err = None
        except Exception as exc:                                   # Cholesky refuses a matrix it finds indefinite
            b, err = None, f"{type(exc).__name__}: {str(exc)[:80]}"
    msgs = sorted({str(w.message)[:90] for w in caught})
    if b is None:
        return dict(lre=[float("nan")] * len(cert_b), error=err, warnings=msgs)
    r = y - X @ b
    return dict(b=[full(v) for v in b], lre=[lre(float(v), float(c)) for v, c in zip(b, cert_b)], rss=float(r @ r),
                warnings=msgs)


def stage_nist(cfg, args):
    out = {"datasets": {}}
    rv = r_values()
    # 1. Exact rational arithmetic against every certified coefficient, standard error and residual SD.
    print("Exact rational least squares against NIST's certified values (15 significant digits):")
    t0 = time.perf_counter()
    total = matched = 0
    for name in NIST_MODEL:
        cert, data = read_nist(name)
        Xq, yq = nist_design(name, data, exact=True)
        b, inv_diag, rss, dfr = exact_least_squares(Xq, yq)
        s2 = rss / dfr
        ok_b = [to15(v) == Decimal(c) for v, c in zip(b, cert["b"])]
        ok_se = [sqrt15(s2 * d) == Decimal(c) for d, c in zip(inv_diag, cert["se"])]
        ok_rsd = sqrt15(s2) == Decimal(cert["rsd"])
        n_ok = sum(ok_b) + sum(ok_se) + int(ok_rsd)
        n_all = len(ok_b) + len(ok_se) + 1
        total += n_all
        matched += n_ok
        out["datasets"][name] = dict(exact_matches=n_ok, exact_values=n_all, n=len(data), p=len(b))
        print(f"  {name:9s} n={len(data):3d} p={len(b):2d}: {n_ok}/{n_all} certified values reproduced digit for digit")
    out["exact"] = dict(matched=matched, total=total, seconds=round(time.perf_counter() - t0, 2))
    print(f"  all datasets: {matched}/{total} ({out['exact']['seconds']} s)")

    # 2. Floating-point solvers, scored in LRE, on Longley and Filip.
    solvers = float_solvers()
    for name in ("Longley", "Filip"):
        cert, data = read_nist(name)
        X, y = nist_design(name, data)
        cb = [float(c) for c in cert["b"]]
        res = {k: solve_and_score(f, X, y, cb) for k, f in solvers.items()}
        cert_rss = float(Decimal(cert["rsd"]) ** 2 * (len(y) - X.shape[1]))
        s = np.linalg.svd(X, compute_uv=False)
        d = out["datasets"][name]
        d.update(kappa=float(s[0] / s[-1]), kappa_XtX=float((s[0] / s[-1]) ** 2), kappa_scaled=kappa_scaled(X),
                 sv_ratio=float(s[-1] / s[0]), numpy_cutoff=float(np.finfo(float).eps * max(X.shape)),
                 statsmodels_cutoff=1e-15, certified_rss=cert_rss, solvers=res)
        print(f"{name}: kappa(X) {d['kappa']:.4e}, kappa(X'X) {d['kappa_XtX']:.4e}, column-scaled kappa "
              f"{d['kappa_scaled']:.4e}; smallest/largest singular value {d['sv_ratio']:.3e}")
        for k, r in res.items():
            L = r["lre"]
            extra = f" RSS/certified {r['rss'] / cert_rss:.4f}" if "rss" in r else ""
            note = f" [{r.get('error') or '; '.join(r['warnings'])}]" if (r.get("error") or r["warnings"]) else ""
            print(f"  {k:30s} digits min {np.nanmin(L) if not all(np.isnan(L)) else float('nan'):6.2f} "
                  f"max {np.nanmax(L) if not all(np.isnan(L)) else float('nan'):6.2f}{extra}{note}")
    lo = out["datasets"]["Longley"]
    print(f"  Longley kappa(X'X) = {lo['kappa_XtX']:.4e}; Wampler (1969) printed {WAMPLER_LONGLEY_CONDITION:.3e}")

    # 3. R's lm, from the private R check, when it has been run.
    if rv:
        for name, p in (("Longley", 7), ("Filip", 11)):
            cert, _ = read_nist(name)
            for tag in ("default", "tol1e10"):
                vals = [rv.get(f"{name}_{tag}_b{j}") for j in range(p)]
                if all(v is None for v in vals):
                    continue
                L = [lre(v, float(c)) if v is not None and math.isfinite(v) else float("nan")
                     for v, c in zip(vals, cert["b"])]
                out["datasets"][name].setdefault("r_lm", {})[tag] = dict(lre=L, rank=rv.get(f"{name}_{tag}_rank"))
                print(f"  R lm ({tag}) on {name}: rank {rv.get(f'{name}_{tag}_rank'):.0f} of {p}; digits min "
                      f"{np.nanmin(L):.2f}; NA coefficients {sum(math.isnan(v) for v in L)}")

    # 4. Filip's failures, looked at closely: which singular value was dropped, and what the dropped term costs.
    cert, data = read_nist("Filip")
    X, y = nist_design("Filip", data)
    cert_rss = out["datasets"]["Filip"]["certified_rss"]
    b9 = np.linalg.lstsq(X[:, :10], y, rcond=-1)[0]
    rss9 = float(np.sum((y - X[:, :10] @ b9) ** 2))
    F9, q9, p9 = nested_F(rss9, len(y) - 10, cert_rss, len(y) - 11)
    out["datasets"]["Filip"]["degree9"] = dict(rss=rss9, rss_ratio=rss9 / cert_rss, F=F9, F_p=p9)
    print(f"Filip without x^10 (what R's lm fits): RSS {rss9 / cert_rss:.4f} x the minimum; F for x^10 {hu(F9, 2)} "
          f"on 1 and {len(y) - 11} df, p {p9:.2e}")

    # 5. All eleven datasets: digits against the column-scaled condition number, and LAPACK's bound.
    eps = np.finfo(float).eps
    rows = []
    for name in NIST_MODEL:
        cert, data = read_nist(name)
        X, y = nist_design(name, data)
        cb = [float(c) for c in cert["b"]]
        bq = solvers["Householder QR"](X, y)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            bn = solvers["normal equations (LU)"](X, y)
        r = y - X @ bq
        sin_t = float(np.linalg.norm(r) / np.linalg.norm(y))
        tan_t = sin_t / math.sqrt(max(1 - sin_t ** 2, 1e-300))
        ks = kappa_scaled(X)
        row = dict(name=name, kappa=kappa(X), kappa_scaled=ks, tan_theta=tan_t,
                   qr_min=min(lre(v, c) for v, c in zip(bq, cb)), ne_min=min(lre(v, c) for v, c in zip(bn, cb)),
                   bound_qr=-math.log10(eps * (2 * ks + tan_t * ks ** 2)), bound_ne=-math.log10(eps * ks ** 2))
        rows.append(row)
    out["all"] = rows
    print("All eleven datasets: fewest correct digits over the coefficients")
    print(f"  {'dataset':9s} {'kappa':>9s} {'scaled':>9s} {'tan':>9s} {'QR':>6s} {'normal':>6s}")
    for r in rows:
        print(f"  {r['name']:9s} {r['kappa']:9.2e} {r['kappa_scaled']:9.2e} {r['tan_theta']:9.2e} {r['qr_min']:6.2f} "
              f"{r['ne_min']:6.2f}")

    # 6. Longley re-expressed: GNP in other units; with --year-origin (E3), the year measured from that origin.
    cert, data = read_nist("Longley")
    X, y = nist_design("Longley", data)
    cb = [float(c) for c in cert["b"]]
    Xg = X.copy()
    Xg[:, 2] /= 1000
    bg = solvers["normal equations (LU)"](Xg, y)
    rescale = dict(kappa=kappa(Xg), kappa_scaled=kappa_scaled(Xg),
                   ne_min=min(lre(v, c) for v, c in zip(np.r_[bg[:2], bg[2] / 1000, bg[3:]], cb)))
    out["longley_gnp_thousands"] = rescale
    print(f"Longley with GNP in thousands: kappa {rescale['kappa']:.3e}, scaled {rescale['kappa_scaled']:.3e}; "
          f"normal equations {rescale['ne_min']:.2f} digits (GNP as printed: {min(lo['solvers']['normal equations (LU)']['lre']):.2f})")
    if args.year_origin is not None:
        origin = args.year_origin
        Xs = X.copy()
        Xs[:, 6] -= origin
        bq = solvers["Householder QR"](Xs, y)
        bn = solvers["normal equations (LU)"](Xs, y)
        back = lambda b: np.r_[b[0] - origin * b[6], b[1:]]         # the intercept back at year 0
        shift = dict(origin=origin, kappa=kappa(Xs), kappa_scaled=kappa_scaled(Xs),
                     qr_min=min(lre(v, c) for v, c in zip(back(bq), cb)),
                     ne_min=min(lre(v, c) for v, c in zip(back(bn), cb)))
        out["longley_year_origin"] = shift
        print(f"Longley with the year measured from {origin:g}: kappa {shift['kappa']:.3e}, scaled "
              f"{shift['kappa_scaled']:.3e}; digits QR {shift['qr_min']:.2f}, normal equations {shift['ne_min']:.2f} "
              f"(year as printed: QR {min(lo['solvers']['Householder QR']['lre']):.2f}, normal equations "
              f"{min(lo['solvers']['normal equations (LU)']['lre']):.2f})")

    # 7. How precise are Longley's data? Perturb each value within half a unit of its last printed digit.
    rng = stream(args.seed, "nist", 1)
    b0 = solvers["Householder QR"](X, y)
    reps = cfg["rounding_reps"]
    B = np.empty((reps, 7))
    for i in range(reps):
        B[i] = solvers["Householder QR"](X + rng.uniform(-1, 1, X.shape) * LONGLEY_HALF_UNIT, y)
    fit = ols(X, y, LONGLEY_NAMES)
    sd = B.std(axis=0, ddof=1)
    out["rounding"] = dict(reps=reps, sd=sd.tolist(), rel=(sd / np.abs(b0)).tolist(), sd_over_se=(sd / fit["se"]).tolist(),
                           digits=(-np.log10(sd / np.abs(b0))).tolist())
    print(f"Longley's data perturbed within their printed precision ({reps} refits):")
    for j, nm in enumerate(LONGLEY_NAMES):
        print(f"  {nm:11s} coefficient moves by SD {sd[j]:.3e} = {sd[j] / abs(b0[j]):.2e} of itself "
              f"(about {-math.log10(sd[j] / abs(b0[j])):.1f} stable digits), {sd[j] / fit['se'][j]:.3f} of its SE")
    return out


# ------------------------------------------------------------------------------- stage: summary
def longley_frame():
    cert, data = read_nist("Longley")
    X, y = nist_design("Longley", data)
    return X, y


def stage_summary(cfg, args):
    import statsmodels.api as sm
    rv = r_values()
    X, y = longley_frame()
    names = LONGLEY_NAMES[:]
    if args.year_origin is not None:
        X = X.copy()
        X[:, 6] -= args.year_origin
        names[6] = f"Year-{args.year_origin:g}"
    if args.fault:
        # The earlier draft built X without the column of ones, as sm.OLS(y, X) does when add_constant is forgotten.
        X, names = X[:, 1:], names[1:]
    fit = ols(X, y, names, intercept=not args.fault)
    dg = residual_diagnostics(fit["resid"], X)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sm_fit = sm.OLS(y, X).fit()
    print(sm_fit.summary(yname="Employed", xname=names))
    print("\nThe same numbers from the design matrix (QR), and the largest relative difference from statsmodels:")
    rows = []
    for j, nm in enumerate(names):
        print(f"  {nm:11s} coef {fit['b'][j]: .6e}  SE {fit['se'][j]:.6e}  t {fit['t'][j]: .4f}  p {fit['p_value'][j]:.6f}"
              f"  95% CI {fit['ci_lo'][j]: .5e} to {fit['ci_hi'][j]: .5e}")
        rows.append(dict(name=nm, b=fit["b"][j], se=fit["se"][j], t=fit["t"][j], p=fit["p_value"][j],
                         ci=[fit["ci_lo"][j], fit["ci_hi"][j]]))
    print(f"  sigma {fit['sigma']:.6f} on {fit['df_resid']} df; RSS {fit['rss']:.6f}; TSS {fit['tss']:.6f}; "
          f"R^2 {fit['r2']:.6f}; adjusted {fit['adj_r2']:.6f}")
    print(f"  F {fit['F']:.4f} on {fit['df_model']} and {fit['df_resid']} df, p {fit['F_p']:.4e}; log-likelihood "
          f"{fit['llf']:.4f}; AIC {fit['aic_mean_only']:.4f} (statsmodels) or {fit['aic_with_sigma']:.4f} (R, counting sigma)")
    print(f"  Omnibus {dg['omnibus']:.4f} (p {dg['omnibus_p']:.4f}); skew {dg['skew']:.4f}; kurtosis {dg['kurtosis']:.4f}; "
          f"Jarque-Bera {dg['jb']:.4f} (p {dg['jb_p']:.4f}); Durbin-Watson {dg['durbin_watson']:.4f}; "
          f"condition number {dg['condition_number']:.4e}")
    ours = np.r_[fit["b"], fit["se"], fit["t"], fit["p_value"], fit["r2"], fit["adj_r2"], fit["F"], fit["F_p"],
                 fit["llf"], fit["aic_mean_only"], fit["bic_mean_only"], dg["omnibus"], dg["jb"], dg["durbin_watson"],
                 dg["condition_number"]]
    theirs = np.r_[sm_fit.params, sm_fit.bse, sm_fit.tvalues, sm_fit.pvalues, sm_fit.rsquared, sm_fit.rsquared_adj,
                   sm_fit.fvalue, sm_fit.f_pvalue, sm_fit.llf, sm_fit.aic, sm_fit.bic, *_sm_diag(sm_fit)]
    mr = max_rel(ours, theirs)
    print(f"  largest relative difference from statsmodels over {len(ours)} numbers: {mr:.1e}")
    out = dict(rows=rows, names=names, sigma=fit["sigma"], df_resid=fit["df_resid"], df_model=fit["df_model"],
               rss=fit["rss"], tss=fit["tss"], rss_full=full(fit["rss"]), tss_full=full(fit["tss"]),
               r2=fit["r2"], adj_r2=fit["adj_r2"], F=fit["F"], F_p=fit["F_p"],
               llf=fit["llf"], aic_statsmodels=fit["aic_mean_only"], bic_statsmodels=fit["bic_mean_only"],
               aic_R=fit["aic_with_sigma"], bic_R=fit["bic_with_sigma"], diagnostics=dg, statsmodels_maxrel=mr,
               n=fit["n"], t_quantile=fit["t_quantile"], resid=fit["resid"].tolist(),
               flags=dict(fault=args.fault, year_origin=args.year_origin))
    if args.fault or args.year_origin is not None:
        return out
    if rv:
        keys = ([f"Longley_default_b{j}" for j in range(7)] + [f"Longley_se{j}" for j in range(7)] +
                ["Longley_sigma", "Longley_r2", "Longley_adj_r2", "Longley_F", "Longley_F_p", "Longley_logLik",
                 "Longley_AIC", "Longley_BIC"])
        rvals = [rv.get(k) for k in keys]
        mine = list(fit["b"]) + list(fit["se"]) + [fit["sigma"], fit["r2"], fit["adj_r2"], fit["F"], fit["F_p"],
                                                    fit["llf"], fit["aic_with_sigma"], fit["bic_with_sigma"]]
        out["r_check"] = dict(maxrel=max_rel(mine, rvals), aic_R=rv.get("Longley_AIC"))
        print(f"  R's summary(lm) and AIC agree to {out['r_check']['maxrel']:.1e} relative (R's AIC {rv.get('Longley_AIC'):.4f})")
    # Joint tests and the joint region of GNP and Year.
    joint = {}
    for drop in (("GNP", "Population"), ("Deflator", "GNP", "Population"), ("GNP", "Year")):
        keep = [j for j, nm in enumerate(names) if nm not in drop]
        fr = ols(X[:, keep], y, [names[j] for j in keep])
        F, q, Fp = nested_F(fr["rss"], fr["df_resid"], fit["rss"], fit["df_resid"])
        joint["+".join(drop)] = dict(F=F, q=q, p=Fp)
        print(f"  joint test that {', '.join(drop)} are all zero: F {F:.4f} on {q} and {fit['df_resid']} df, p {Fp:.4g}")
    out["joint"] = joint
    ig, iy = names.index("GNP"), names.index("Year")
    C = fit["s2"] * fit["XtXi"][np.ix_([ig, iy], [ig, iy])]
    corr = float(C[0, 1] / math.sqrt(C[0, 0] * C[1, 1]))
    fq = float(stats.f.ppf(LEVEL, 2, fit["df_resid"]))
    w, V = np.linalg.eigh(C)
    ang = np.linspace(0, 2 * np.pi, 181)
    circle = np.vstack([np.cos(ang), np.sin(ang)])
    ell = (V @ (np.sqrt(2 * fq * w)[:, None] * circle)).T + np.array([fit["b"][ig], fit["b"][iy]])
    out["ellipse"] = dict(center=[fit["b"][ig], fit["b"][iy]], cov=C.tolist(), corr=corr, f_quantile=fq,
                          points=ell.tolist(), ci_gnp=[fit["ci_lo"][ig], fit["ci_hi"][ig]],
                          ci_year=[fit["ci_lo"][iy], fit["ci_hi"][iy]])
    print(f"  GNP and Year estimates correlate {corr:.4f}; their joint 95% region is an ellipse with axes ratio "
          f"{math.sqrt(w.max() / w.min()):.1f}")
    return out


def _sm_diag(sm_fit):
    from statsmodels.stats.stattools import durbin_watson, jarque_bera, omni_normtest
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        omni = omni_normtest(sm_fit.wresid)[0]
    return [omni, jarque_bera(sm_fit.wresid)[0], durbin_watson(sm_fit.wresid), sm_fit.condition_number]


# ------------------------------------------------------------------------------- stage: meaning
def partial_out(X, j):
    """Residuals of every column of X on the others except column j, and of column j on the others."""
    others = [k for k in range(X.shape[1]) if k != j]
    Q, _ = np.linalg.qr(X[:, others])
    return lambda v: v - Q @ (Q.T @ v)


def stage_meaning(cfg, args):
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    X, y = longley_frame()
    names = LONGLEY_NAMES
    fit = ols(X, y, names)
    out = {"fwl": {}, "vif": {}}
    print("Frisch-Waugh-Lovell: each slope equals the slope of y's residuals on the predictor's residuals")
    for j in range(1, 7):
        res = partial_out(X, j)
        xr, yr = res(X[:, j]), res(y)
        slope = float(xr @ yr / (xr @ xr))
        r2j = 1 - float(xr @ xr) / float(((X[:, j] - X[:, j].mean()) ** 2).sum())
        se_fwl = fit["sigma"] / math.sqrt(float(xr @ xr))
        out["fwl"][names[j]] = dict(slope=slope, coef=float(fit["b"][j]), rel_diff=abs(slope - fit["b"][j]) / abs(fit["b"][j]),
                                    se_from_partial=se_fwl, se=float(fit["se"][j]), r2_on_others=r2j,
                                    vif=1 / (1 - r2j), sd_raw=float(X[:, j].std(ddof=1)), sd_partial=float(xr.std(ddof=1)))
        print(f"  {names[j]:11s} slope on residuals {slope: .6e} vs coefficient {fit['b'][j]: .6e}; R^2 on the others "
              f"{r2j:.6f}; VIF {1 / (1 - r2j):9.2f}; residual SD {xr.std(ddof=1):.4g} of raw SD {X[:, j].std(ddof=1):.4g}")
    jg = names.index("GNP")
    res = partial_out(X, jg)
    simple = ols(X[:, [0, jg]], y, ["const", "GNP"])
    out["fwl_points"] = dict(x_raw=X[:, jg].tolist(), y_raw=y.tolist(), x_partial=res(X[:, jg]).tolist(),
                             y_partial=res(y).tolist(), simple_slope=float(simple["b"][1]))
    print(f"  GNP alone (employment on GNP and a constant): slope {simple['b'][1]:.6f}; with the other five: "
          f"{fit['b'][jg]:.6f}")
    vif_sm = [variance_inflation_factor(X, j) for j in range(1, 7)]
    out["vif_statsmodels"] = vif_sm
    print(f"  statsmodels variance_inflation_factor agrees to "
          f"{max_rel([out['fwl'][names[j]]['vif'] for j in range(1, 7)], vif_sm):.1e} relative")
    # Omitted-variable bias: leave Year out; the short coefficients equal long + (Year's coefficient) x (auxiliary slopes).
    iy = names.index("Year")
    keep = [k for k in range(7) if k != iy]
    short = ols(X[:, keep], y, [names[k] for k in keep])
    aux = ols(X[:, keep], X[:, iy], [names[k] for k in keep])
    implied = fit["b"][keep] + fit["b"][iy] * aux["b"]
    out["ovb"] = dict(omitted="Year", names=[names[k] for k in keep], long=fit["b"][keep].tolist(),
                      short=short["b"].tolist(), aux=aux["b"].tolist(), gamma=float(fit["b"][iy]),
                      bias=(fit["b"][iy] * aux["b"]).tolist(), identity_maxrel=max_rel(implied, short["b"]),
                      short_se=short["se"].tolist(), long_se=fit["se"][keep].tolist(), short_r2=short["r2"])
    print("Omitted-variable bias, leaving Year out (short = long + Year's coefficient x auxiliary slope):")
    for k, nm in enumerate(out["ovb"]["names"]):
        print(f"  {nm:11s} long {fit['b'][keep][k]: .5e}  short {short['b'][k]: .5e}  = long + {fit['b'][iy]:.2f} x "
              f"{aux['b'][k]: .5e}")
    print(f"  identity holds to {out['ovb']['identity_maxrel']:.1e} relative; short-model R^2 {short['r2']:.6f}")
    # Condition numbers: centring and scaling change kappa, not the VIFs.
    Xc = np.column_stack([np.ones(16), X[:, 1:] - X[:, 1:].mean(0)])
    Xz = np.column_stack([np.ones(16), (X[:, 1:] - X[:, 1:].mean(0)) / X[:, 1:].std(0, ddof=1)])
    vif_z = [variance_inflation_factor(Xz, j) for j in range(1, 7)]
    out["kappa"] = dict(raw=kappa(X), centred=kappa(Xc), standardised=kappa(Xz), scaled=kappa_scaled(X),
                        vif_unchanged_maxrel=max_rel(vif_z, vif_sm))
    out["corr"] = np.corrcoef(X[:, 1:].T).tolist()
    print(f"Condition number of X: raw {out['kappa']['raw']:.4e}, centred {out['kappa']['centred']:.4e}, standardised "
          f"{out['kappa']['standardised']:.4f}; the VIFs move by {out['kappa']['vif_unchanged_maxrel']:.1e}")
    print(f"  correlation of GNP and Year {out['corr'][1][5]:.4f}; of Deflator and GNP {out['corr'][0][1]:.4f}")
    return out


# ------------------------------------------------------------------------------- stage: interaction
def stage_interaction(cfg, args):
    import statsmodels.api as sm
    rv = r_values()
    y, supp, dose = read_teeth()
    oj = (supp == "OJ").astype(float)
    out = {"cells": {}}
    for s in ("OJ", "VC"):
        for d in (0.5, 1.0, 2.0):
            v = y[(supp == s) & (dose == d)]
            out["cells"][f"{s}_{d:g}"] = dict(mean=float(v.mean()), sd=float(v.std(ddof=1)), n=len(v))
    print("ToothGrowth cell means (10 animals each):")
    for s in ("OJ", "VC"):
        print(f"  {s}: " + ", ".join(f"{d:g} mg {out['cells'][f'{s}_{d:g}']['mean']:.2f}" for d in (0.5, 1.0, 2.0)))
    print("  OJ - VC: " + ", ".join(f"{d:g} mg {out['cells'][f'OJ_{d:g}']['mean'] - out['cells'][f'VC_{d:g}']['mean']:.2f}"
                                     for d in (0.5, 1.0, 2.0)))
    fits = {}
    for origin in (0.5, 1.0, 2.0):
        z = np.log2(dose / origin)
        X = np.column_stack([np.ones(len(y)), oj, z, oj * z])
        f = ols(X, y, ["const", "OJ", "doublings", "OJ:doublings"])
        fits[origin] = f
        print(f"len ~ OJ * log2(dose/{origin:g}): OJ {f['b'][1]:.4f} (SE {f['se'][1]:.4f}, t {f['t'][1]:.3f}, "
              f"p {f['p_value'][1]:.4g}); interaction {f['b'][3]:.4f} (SE {f['se'][3]:.4f}); slope for VC {f['b'][2]:.4f}; "
              f"R^2 {f['r2']:.5f}")
    out["fits"] = {f"{o:g}": dict(b=f["b"].tolist(), se=f["se"].tolist(), t=f["t"].tolist(), p=f["p_value"].tolist(),
                                  ci_lo=f["ci_lo"].tolist(), ci_hi=f["ci_hi"].tolist(), r2=f["r2"], sigma=f["sigma"],
                                  rss=f["rss"], df=f["df_resid"]) for o, f in fits.items()}
    # Lack of fit against the six cell means, and the interaction F with dose as a factor.
    cells = np.array([(s, d) for s, d in zip(supp, dose)], dtype=object)
    keys = sorted({(s, d) for s, d in cells})
    Xcell = np.column_stack([np.array([(s, d) == k for s, d in cells], float) for k in keys])
    fcell = ols(Xcell, y, [f"{k[0]}{k[1]}" for k in keys], intercept=False)
    F, q, Fp = nested_F(fits[1.0]["rss"], fits[1.0]["df_resid"], fcell["rss"], fcell["df_resid"])
    d1, d2 = (dose == 1.0).astype(float), (dose == 2.0).astype(float)
    Xadd = np.column_stack([np.ones(len(y)), oj, d1, d2])
    fadd = ols(Xadd, y)
    Fi, qi, pi = nested_F(fadd["rss"], fadd["df_resid"], fcell["rss"], fcell["df_resid"])
    out["lack_of_fit"] = dict(F=F, q=q, df=fcell["df_resid"], p=Fp)
    out["factor_interaction"] = dict(F=Fi, q=qi, df=fcell["df_resid"], p=pi)
    print(f"  lack of fit of the log-dose lines against the six cell means: F {F:.4f} on {q} and {fcell['df_resid']} df, "
          f"p {Fp:.4f}")
    print(f"  supplement x dose interaction with dose as a factor: F {Fi:.4f} on {qi} and {fcell['df_resid']} df, p {pi:.4f}")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = sm.OLS(y, np.column_stack([np.ones(len(y)), oj, np.log2(dose), oj * np.log2(dose)])).fit()
    out["statsmodels_maxrel"] = max_rel(np.r_[fits[1.0]["b"], fits[1.0]["se"]], np.r_[m.params, m.bse])
    if rv:
        rr = [rv.get("teeth_OJ"), rv.get("teeth_OJ_se"), rv.get("teeth_inter"), rv.get("teeth_lof_F")]
        out["r_check"] = max_rel([fits[1.0]["b"][1], fits[1.0]["se"][1], fits[1.0]["b"][3], F], rr)
        print(f"  R lm agrees to {out['r_check']:.1e} relative")
    return out


# ------------------------------------------------------------------------------- stage: intervals
def stage_intervals(cfg, args):
    y, supp, dose = read_teeth()
    vc = supp == "VC"
    z, yv = np.log2(dose[vc]), y[vc]
    X = np.column_stack([np.ones(vc.sum()), z])
    f = ols(X, yv, ["const", "doublings"])
    z0 = math.log2(TG_NEW_DOSE)
    x0 = np.array([1.0, z0])
    h0 = float(x0 @ f["XtXi"] @ x0)
    mu0 = float(x0 @ f["b"])
    tq = f["t_quantile"]
    ci = (mu0 - tq * f["sigma"] * math.sqrt(h0), mu0 + tq * f["sigma"] * math.sqrt(h0))
    pi = (mu0 - tq * f["sigma"] * math.sqrt(1 + h0), mu0 + tq * f["sigma"] * math.sqrt(1 + h0))
    grid = np.linspace(-1.2, 1.2, 97)
    G = np.column_stack([np.ones_like(grid), grid])
    hg = np.einsum("ij,jk,ik->i", G, f["XtXi"], G)
    mg = G @ f["b"]
    out = dict(b=f["b"].tolist(), se=f["se"].tolist(), sigma=f["sigma"], df=f["df_resid"], tq=tq, x0_dose=TG_NEW_DOSE,
               leverage0=h0, mean0=mu0, ci=list(ci), pi=list(pi), ratio=math.sqrt((1 + h0) / h0),
               grid=grid.tolist(), band_mean=mg.tolist(), ci_half=(tq * f["sigma"] * np.sqrt(hg)).tolist(),
               pi_half=(tq * f["sigma"] * np.sqrt(1 + hg)).tolist(), z=z.tolist(), y=yv.tolist())
    print(f"VC arm: length = {f['b'][0]:.4f} + {f['b'][1]:.4f} x doublings of dose from 1 mg; sigma {f['sigma']:.4f} on "
          f"{f['df_resid']} df")
    print(f"  at {TG_NEW_DOSE} mg: mean {mu0:.4f}; leverage {h0:.5f}; 95% CI for the mean {ci[0]:.3f} to {ci[1]:.3f}; "
          f"95% prediction interval {pi[0]:.3f} to {pi[1]:.3f} ({out['ratio']:.2f} times wider)")
    # How often each interval covers a new animal's length, simulated from the fitted VC model.
    reps = cfg["cover_reps"]
    rows = []
    for k, m in enumerate((2, 5, 10, 20, 50, 200)):
        rng = stream(args.seed, "intervals", k)
        zz = np.repeat([-1.0, 0.0, 1.0], m)
        n = len(zz)
        Xd = np.column_stack([np.ones(n), zz])
        XtXi = np.linalg.inv(Xd.T @ Xd)
        hh = float(x0 @ XtXi @ x0)
        tqq = stats.t.ppf(0.5 + LEVEL / 2, n - 2)
        hits_ci_mean = hits_pi = hits_ci_new = 0
        for start in range(0, reps, CHUNK):
            r = min(CHUNK, reps - start)
            Y = f["b"][0] + f["b"][1] * zz + f["sigma"] * rng.standard_normal((r, n))
            B = Y @ Xd @ XtXi
            E = Y - B @ Xd.T
            s = np.sqrt((E ** 2).sum(1) / (n - 2))
            mu = B @ x0
            ynew = mu0 + f["sigma"] * rng.standard_normal(r)
            hits_ci_mean += int(np.sum(np.abs(mu - mu0) <= tqq * s * math.sqrt(hh)))
            hits_ci_new += int(np.sum(np.abs(ynew - mu) <= tqq * s * math.sqrt(hh)))
            hits_pi += int(np.sum(np.abs(ynew - mu) <= tqq * s * math.sqrt(1 + hh)))
        rows.append(dict(n=n, ci_covers_mean=hits_ci_mean / reps, ci_covers_new=hits_ci_new / reps, pi_covers_new=hits_pi / reps))
        print(f"  n = {n:4d}: CI covers the mean {pc(hits_ci_mean / reps)}%; PI covers a new animal {pc(hits_pi / reps)}%; "
              f"the CI used as a PI covers {pc(hits_ci_new / reps)}% (MCSE <= {pc(mcse_share(0.5, reps), 2)} points)")
    out["coverage"] = dict(reps=reps, rows=rows)
    return out


# ------------------------------------------------------------------------------- stage: conditions
def _slope_cover(rng, n, reps, gen):
    """Coverage of the slope's 95% t-interval for y = 1 + 2x + error, with x and errors drawn by gen."""
    hit = hi = lo = 0
    tq = stats.t.ppf(0.5 + LEVEL / 2, n - 2)
    for start in range(0, reps, CHUNK):
        r = min(CHUNK, reps - start)
        x, e = gen(rng, r, n)
        Y = 1 + 2 * x + e
        xb = x.mean(1, keepdims=True)
        sxx = ((x - xb) ** 2).sum(1)
        b = ((x - xb) * (Y - Y.mean(1, keepdims=True))).sum(1) / sxx
        a = Y.mean(1) - b * xb[:, 0]
        res = Y - a[:, None] - b[:, None] * x
        se = np.sqrt((res ** 2).sum(1) / (n - 2) / sxx)
        hit += int(np.sum(np.abs(b - 2) <= tq * se))
        hi += int(np.sum(b - 2 > tq * se))
        lo += int(np.sum(b - 2 < -tq * se))
    return hit / reps, hi / reps, lo / reps


def _lognormal_std(rng, shape):
    """Lognormal(0, 1) errors centred and scaled to mean 0, variance 1 (skewness about 6.2)."""
    return (rng.lognormal(0.0, 1.0, shape) - math.exp(0.5)) / math.sqrt((math.e - 1) * math.e)


def _ar1(rng, r, n, phi=0.7):
    z = rng.standard_normal((r, n))
    e = np.empty_like(z)
    e[:, 0] = z[:, 0]
    for t in range(1, n):
        e[:, t] = phi * e[:, t - 1] + math.sqrt(1 - phi ** 2) * z[:, t]
    return e


CONDITIONS = {
    "normal": lambda rng, r, n: (rng.standard_normal((r, n)), rng.standard_normal((r, n))),
    "skewed predictor": lambda rng, r, n: (rng.lognormal(0, 1, (r, n)), rng.standard_normal((r, n))),
    "skewed errors": lambda rng, r, n: (rng.lognormal(0, 1, (r, n)), _lognormal_std(rng, (r, n))),
    "heavy-tailed errors": lambda rng, r, n: (rng.standard_normal((r, n)), rng.standard_t(3, (r, n)) / math.sqrt(3)),
    "non-constant variance": lambda rng, r, n: (lambda x: (x, rng.standard_normal((r, n)) * np.exp(x / 2)))(rng.standard_normal((r, n))),
    "dependent errors": lambda rng, r, n: (np.broadcast_to(np.linspace(-1, 1, n), (r, n)).copy(), _ar1(rng, r, n)),
}
SIZES = (5, 10, 20, 50, 200, 1000)


def stage_conditions(cfg, args):
    reps = cfg["cond_reps"]
    out = {"reps": reps, "sizes": list(SIZES), "slope": {}}
    print(f"Coverage of the slope's 95% interval, {reps} simulated datasets per cell (MCSE about "
          f"{pc(mcse_share(0.95, reps), 2)} points at 95%):")
    print("  " + " " * 22 + "".join(f"n={n:<6d}" for n in SIZES))
    for ci, (name, gen) in enumerate(CONDITIONS.items()):
        vals = []
        for si, n in enumerate(SIZES):
            cov, hi, lo = _slope_cover(stream(args.seed, "conditions", 100 * ci + si), n, reps, gen)
            vals.append(dict(n=n, cover=cov, mcse=mcse_share(cov, reps), above=hi, below=lo))
        out["slope"][name] = vals
        print(f"  {name:22s}" + "".join(f"{pc(v['cover']):>8s}" for v in vals))
    sk = out["slope"]["skewed errors"]
    print("  skewed errors, misses above / below the interval: " +
          ", ".join(f"n={v['n']} {pc(v['above'])}/{pc(v['below'])}" for v in sk))
    # The prediction interval's two tails, normal against skewed errors.
    reps_pi = cfg["pi_reps"]
    out["pi"] = {"reps": reps_pi}
    for ki, (name, egen) in enumerate((("normal", lambda rng, s: rng.standard_normal(s)),
                                       ("skewed", lambda rng, s: rng.exponential(1.0, s) - 1.0))):
        rows = []
        for si, n in enumerate((10, 30, 100, 1000)):
            rng = stream(args.seed, "conditions", 1000 + 10 * ki + si)
            tq = stats.t.ppf(0.5 + LEVEL / 2, n - 2)
            below = above = 0
            for start in range(0, reps_pi, CHUNK):
                r = min(CHUNK, reps_pi - start)
                x = rng.standard_normal((r, n))
                Y = 1 + 2 * x + egen(rng, (r, n))
                xb = x.mean(1, keepdims=True)
                sxx = ((x - xb) ** 2).sum(1)
                b = ((x - xb) * (Y - Y.mean(1, keepdims=True))).sum(1) / sxx
                a = Y.mean(1) - b * xb[:, 0]
                s = np.sqrt(((Y - a[:, None] - b[:, None] * x) ** 2).sum(1) / (n - 2))
                x0 = rng.standard_normal(r)
                y0 = 1 + 2 * x0 + egen(rng, r)
                half = tq * s * np.sqrt(1 + 1 / n + (x0 - xb[:, 0]) ** 2 / sxx)
                mu = a + b * x0
                below += int(np.sum(y0 < mu - half))
                above += int(np.sum(y0 > mu + half))
            rows.append(dict(n=n, below=below / reps_pi, above=above / reps_pi, cover=1 - (below + above) / reps_pi))
        out["pi"][name] = rows
        print(f"Prediction interval with {name} errors, misses below / above: " +
              ", ".join(f"n={r['n']} {pc(r['below'], 2)}/{pc(r['above'], 2)}" for r in rows))
    out["pi"]["exact_exponential_upper"] = math.exp(-(1 + stats.norm.ppf(0.975)))
    print(f"  large-n limit for the skewed errors: P(error > 1.96 SD) = exp(-2.96) = {pc(out['pi']['exact_exponential_upper'], 2)}%"
          f", none below")
    return out


# ------------------------------------------------------------------------------- driver
def provenance(args, budget):
    cpu = platform.processor() or platform.machine()
    try:
        for line in pathlib.Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    except OSError:
        pass
    import statsmodels
    data_files = sorted(DATA.glob("*.csv"))
    return {"captured_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "os": f"{platform.system()} {platform.release()} {platform.machine()}", "cpu": cpu,
            "python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "statsmodels": statsmodels.__version__, "regression_py_sha1": sha1(pathlib.Path(__file__)),
            "data_sha1": {p.name: sha1(p) for p in data_files}, "nist_sha256": NIST_SHA256,
            "r_crosscheck": R_CSV.name if R_CSV.exists() else "not run", "budget": budget, "seed": args.seed,
            "budget_values": QUICK if args.quick else FULL,
            "flags": {"fault": args.fault, "year_origin": args.year_origin}}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("stage", choices=STAGES + ("all",))
    parser.add_argument("--quick", action="store_true", help="fewer simulated replications")
    parser.add_argument("--out", default="captures.json", help="capture file to write (default captures.json)")
    parser.add_argument("--seed", type=int, default=20261128)
    parser.add_argument("--year-origin", type=float, help="nist, summary: measure Longley's year from this origin (E3)")
    parser.add_argument("--fault", action="store_true", help="summary: E4, an earlier draft of the summary stage")
    args = parser.parse_args()
    cfg = QUICK if args.quick else FULL
    budget = "quick" if args.quick else "full"
    prov = provenance(args, budget)
    print(f"Captured {prov['captured_utc']} on {prov['os']}, {prov['cpu']}; Python {prov['python']}, NumPy {prov['numpy']}, "
          f"SciPy {prov['scipy']}, statsmodels {prov['statsmodels']}; regression.py {prov['regression_py_sha1']}; "
          f"budget {budget}, seed {args.seed}; R check: {prov['r_crosscheck']}.")
    out_path = pathlib.Path(args.out)
    captures = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {}
    captures["provenance"] = prov
    timings = captures.setdefault("seconds", {})
    stages = STAGES if args.stage == "all" else (args.stage,)
    funcs = {"example": stage_example, "nist": stage_nist, "summary": stage_summary, "meaning": stage_meaning,
             "interaction": stage_interaction, "intervals": stage_intervals, "conditions": stage_conditions}
    for name in stages:
        t0 = time.perf_counter()
        print(f"\n== {name}")
        key = name if not (args.fault or args.year_origin is not None) else f"{name}_variant"
        captures[key] = r6(funcs[name](cfg, args))
        timings[name] = round(time.perf_counter() - t0, 1)
    out_path.write_text(json.dumps(captures, indent=1) + "\n", encoding="utf-8")
    print(f"\nwrote {out_path.name}: " + ", ".join(f"{k} {v} s" for k, v in timings.items() if k in stages))


if __name__ == "__main__":
    main()
