#!/usr/bin/env python3
"""Figure 09: how R-hat, bulk ESS, tail ESS and the MCSE are computed from the draws (Vehtari et al. 2021).

A mermaid figure: 12 nodes and four parallel paths, past the route gate's limit for hand placement. This script writes
the .mmd with the worked example's numbers read from ../lab/captures.json, then renders it with _mermaid.py.
Run:  python3 _fig09.py
"""
import json
import pathlib

import _mermaid

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
D = CAP["diagnostics"]["pfizer_theta"]["mine"]
P = CAP["diagnostics"]["pieces"]
STEM = "fig-09-how-rhat-and-ess-are-computed-mcmc-diagnostics-metropolis-nuts"
assert P["split_chains"] == 8 and P["n"] == 2500 and P["S"] == 20000

src = f"""---
config:
  flowchart:
    curve: basis
---
flowchart TB
  d["draws of one quantity, θ<br/>M = 4 chains × N = 5,000"]
  s["split every chain in half<br/>8 half-chains × {P['n']:,}"]
  r["rank all S = {P['S']:,} draws together,<br/>then normal scores<br/>z = inverse normal of (r − 3/8)/(S + 1/4)"]
  f["fold: |θ − median of θ|,<br/>then rank and normal scores"]
  i["indicators: is θ at or below<br/>its 5% point? its 95% point?"]
  m["the half-chains' raw values"]
  rb["bulk R-hat = √(var+ / W)<br/>var+ = (n − 1)/n · W + B/n<br/>trial: {D['bulk']:.5f}"]
  rf["folded R-hat, the same<br/>formula on the folded scores<br/>trial: {D['folded']:.5f}"]
  rh["reported R-hat:<br/>the larger of the two<br/>trial: {D['rank']:.5f}; use if below 1.01"]
  eb["bulk ESS = S / τ on the scores<br/>trial: {D['ess_bulk']:,.0f}; want above 400"]
  et["tail ESS: the smaller ESS<br/>of the two indicators<br/>trial: {D['ess_tail']:,.0f}; want above 400"]
  em["ESS for the mean = S / τ on θ;<br/>MCSE = SD / √ESS<br/>trial: {D['ess_mean']:,.0f}; {D['mcse_mean']:.6f}"]

  d -->|"a trend shows as<br/>halves that disagree"| s
  s -->|"pooled ranks:<br/>tails cannot dominate"| r
  s -->|"distance from<br/>the median"| f
  s -->|"0 or 1 at each<br/>tail quantile"| i
  s -->|"values as drawn"| m
  r -->|"between B, within W"| rb
  r -->|"autocorrelations,<br/>Geyer's truncation"| eb
  f -->|"between B, within W"| rf
  rb -->|"compare"| rh
  rf -->|"compare"| rh
  i -->|"autocorrelations<br/>of each indicator"| et
  m -->|"autocorrelations,<br/>then SD / √ESS"| em

  classDef out fill:#fdf1eb,stroke:#eb6c36,color:#2d3142
  classDef step fill:#ffffff,stroke:#2e5aa8,color:#2d3142
  class rh,eb,et,em out
  class s,r,f,i,m step
"""
(HERE / f"{STEM}.mmd").write_text(src, encoding="utf-8")
_mermaid.render(STEM)
