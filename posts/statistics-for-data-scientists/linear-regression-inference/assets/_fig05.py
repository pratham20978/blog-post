#!/usr/bin/env python3
"""Figure 05: how every number in a regression summary is computed from the design matrix and the response.

A mermaid figure: 18 nodes on four branching paths (coefficients, fit statistics, likelihood, residual diagnostics),
past the route gate's limit for hand placement. This script writes the .mmd with Longley's numbers read from
../lab/captures.json, then renders it with _mermaid.py.  Run:  python3 _fig05.py
"""
import json
import pathlib

import _mermaid

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
S = CAP["summary"]
D = S["diagnostics"]
G = {r["name"]: r for r in S["rows"]}["GNP"]
STEM = "fig-05-how-each-number-is-computed-linear-regression-inference"
assert S["n"] == 16 and S["df_resid"] == 9 and S["df_model"] == 6

src = f"""---
config:
  flowchart:
    curve: basis
---
flowchart TB
  x["X: n × p design matrix, with a column of ones<br/>y: n responses · Longley: n = 16, p = 7"]
  qr["QR factorisation: X = QR<br/>Q orthonormal, R upper triangular"]
  cn["condition number of X<br/>σ_max / σ_min = {D['condition_number']:.3e}"]
  b["coefficients b: solve R b = Qᵀy<br/>GNP: {G['b']:.6f}"]
  e["residuals e = y − Xb"]
  ss["sums of squares<br/>RSS = Σe² = {float(S['rss_full']):,.0f}<br/>TSS = Σ(y − ȳ)² = {float(S['tss_full']):,.0f}"]
  dg["residual diagnostics: skew {D['skew']:.3f}, kurtosis {D['kurtosis']:.3f},<br/>Jarque–Bera {D['jb']:.3f}, Omnibus {D['omnibus']:.3f}, Durbin–Watson {D['durbin_watson']:.3f}"]
  s2["s² = RSS / (n − p)<br/>s = {S['sigma']:.3f} on {S['df_resid']} df"]
  r2["R² = 1 − RSS/TSS = {S['r2']:.6f}<br/>adjusted: 1 − (1 − R²)(n − 1)/(n − p) = {S['adj_r2']:.6f}"]
  ll["log-likelihood at the Gaussian MLE<br/>ℓ = −(n/2)[log(2π · RSS/n) + 1] = {S['llf']:.2f}"]
  se["standard errors: s √ of the diagonal<br/>of (XᵀX)⁻¹ = R⁻¹R⁻ᵀ · GNP: {G['se']:.6f}"]
  f["F = [(TSS − RSS)/(p − 1)] / [RSS/(n − p)]<br/>= {S['F']:.2f} on 6 and 9 df, p = {S['F_p']:.2e}"]
  aic["AIC = −2ℓ + 2k, BIC = −2ℓ + k log n<br/>statsmodels k = p: {S['aic_statsmodels']:.1f}, {S['bic_statsmodels']:.1f}<br/>R k = p + 1: {S['aic_R']:.1f}, {S['bic_R']:.1f}"]
  t["t = b / SE on n − p df<br/>p-value, b ± t(0.975) × SE<br/>GNP: t = {G['t']:.3f}, p = {G['p']:.3f}"]

  x -->|"Householder reflections"| qr
  x -->|"singular values"| cn
  qr -->|"back substitution"| b
  b -->|"fitted values Xb"| e
  e -->|"square and sum"| ss
  e -->|"moments, lag-1 differences"| dg
  ss -->|"RSS over the residual df"| s2
  ss -->|"RSS and TSS"| r2
  ss -->|"RSS / n, the MLE of σ²"| ll
  qr -->|"R inverted"| se
  s2 -->|"scale"| se
  ss -->|"TSS − RSS and RSS,<br/>each over its df"| f
  ll -->|"penalise k parameters"| aic
  se -->|"divide b by SE"| t

  classDef out fill:#fdf1eb,stroke:#eb6c36,color:#2d3142
  classDef step fill:#ffffff,stroke:#2e5aa8,color:#2d3142
  class b,se,t,r2,f,aic,dg,cn out
  class qr,e,ss,s2,ll step
"""
(HERE / f"{STEM}.mmd").write_text(src, encoding="utf-8")
_mermaid.render(STEM)
