"""Write social.md for Part 9 (private build script, never uploaded).

The copy and the per-card fields are written here by hand; each card's visible-text transcript is
read back from its rendered SVG, so the transcript always matches what the card shows.
Usage: python3 assets/_social_md.py   (after _social.py and render_social.py)
"""
import html
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
POST = HERE.parent
CANON = "https://canery.in/blogs/multiple-comparisons-fwer-fdr"


def transcript(stem):
    svg = (HERE / "social" / f"{stem}.svg").read_text()
    svg = re.sub(r"<defs>.*?</defs>", "", svg, flags=re.S)
    runs = []
    for m in re.finditer(r"<text\b[^>]*>(.*?)</text>", svg, re.S):
        parts = re.findall(r"<tspan\b[^>]*>(.*?)</tspan>", m.group(1), re.S) or [m.group(1)]
        runs.append(" ".join(html.unescape(re.sub(r"<[^>]+>", "", p)).strip() for p in parts))
    return " | ".join(r for r in runs if r)


CARDS = [
    dict(stem="feed-01-cover", role="cover",
         title="Same genes, same 5%: 2, 94 or 162 discoveries",
         order="the same 5% level finds 2, 94 or 162 genes depending on the promise",
         beat="On one dataset at one 5% level, the corrections find 2, 94, 162 or 0 genes because each bounds a different error rate",
         source="Four corrections on 3,170 breast-cancer genes (worked example and its counts table); ledger L28",
         structure="Locked feed shell: lockup and counter, a two-line serif headline and a setup line; the panel holds three columns, each with its error-rate eyebrow, a large count, the rule's name and its promise, an accent bar under 94, then a footer band for Benjamini–Yekutieli; the takeaway closes the card",
         alt="Three large counts, 2, 94 and 162, for Bonferroni and Holm, Benjamini–Hochberg and Storey q-values at 5% on 3,170 genes; BY finds 0",
         long="Hedenfalk's 3,170 breast-cancer genes, one two-sample test each, corrected five ways at the same 5% level. Bonferroni and Holm, which keep the family-wise error rate at or below 0.05, reject 2 genes. Benjamini–Hochberg, which keeps the false discovery rate at or below 0.05 under independence or positive dependence, rejects 94. Storey's q-values, which make the same promise with an estimated null share of 0.670, reject 162. Benjamini–Yekutieli, valid under any dependence, runs BH at 0.05 divided by the harmonic number 8.64 and rejects none. The takeaway: choose the error rate from the claim you will make, then the rule from what you know about the dependence.",
         keywords="multiple comparisons, Bonferroni, Holm, Benjamini-Hochberg, Benjamini-Yekutieli, Storey q-value, FWER, FDR, Hedenfalk breast cancer data"),
    dict(stem="feed-02-two-promises", role="technical",
         title="Two promises about one unseen count",
         order="FWER and FDR bound different summaries of the false rejections V",
         beat="FWER bounds the chance of any false rejection, FDR the expected false share, and both are about V, which no study observes",
         source="Which error rate a correction promises to hold (the outcome table and both definitions); ledger L02",
         structure="Locked feed shell: one-line serif headline and a two-line setup; the panel holds the outcome table of m tests with the V cell highlighted in tangerine, then two definition boxes side by side for FWER and FDR with the rules that control each; the takeaway closes the card",
         alt="Outcome table of m tests with V, the false rejections, highlighted, beside the definitions FWER = P(V ≥ 1) and FDR = E[V / max(R, 1)]",
         long="The outcome table of m tests: true nulls split into U not rejected and V rejected, false nulls into T and S, with totals m − R, R and m. V, the number of false rejections, is highlighted because no study ever observes it. The family-wise error rate is P(V ≥ 1), the chance of even one false discovery, controlled by Bonferroni and Holm. The false discovery rate is E[V / max(R, 1)], the expected false share of the list over repeated studies, controlled by Benjamini–Hochberg, Benjamini–Yekutieli and Storey's q-values. The takeaway: a finding that stands alone needs FWER control; a list that feeds follow-up work needs FDR control.",
         keywords="family-wise error rate, false discovery rate, false discovery proportion, outcome table, type I error, multiple testing"),
    dict(stem="feed-03-step-up-line", role="technical",
         title="BH keeps every gene up to rank 94",
         order="BH's step-up line keeps every gene up to rank 94",
         beat="BH compares each sorted p-value with a line that rises with its rank and keeps everything up to the last one under the line",
         source="Four corrections on 3,170 breast-cancer genes, Figure 2 (the rules as lines through the sorted p-values); ledger L28",
         structure="Locked feed shell: one-line serif headline and a two-line setup; the panel holds a log-scale chart of the 200 smallest sorted p-values against rank, with the BH line solid, Storey's line dashed and Bonferroni's flat dotted line, each labelled with its count; rank 94 is circled in tangerine with a callout giving its p-value and threshold; the takeaway closes the card",
         alt="Sorted Hedenfalk p-values on a log axis with Bonferroni, BH and Storey lines; rank 94 is circled as the last p-value under BH's line",
         long="The 200 smallest of the 3,170 Hedenfalk p-values, sorted and plotted against their rank on a log scale from 1e-6 to 1e-2. Bonferroni's threshold is flat at 0.05/3,170 and only ranks 1 and 2 reach it, so Bonferroni and Holm reject 2 genes. The Benjamini–Hochberg line rises as k × 0.05/3,170, and rank 94 is the last p-value under it: 1.4700e-3 ≤ 1.4826e-3, so BH rejects ranks 1 to 94. Storey's line is the BH line divided by π0 = 0.670 and reaches rank 162. The takeaway: BH's threshold at rank k is k times Bonferroni's, which is how it keeps 94 genes instead of 2.",
         keywords="Benjamini-Hochberg, step-up procedure, sorted p-values, rejection line, Bonferroni threshold, Storey q-value, Hedenfalk"),
    dict(stem="feed-04-fdp-spread", role="technical",
         title="Same FDR, very different lists",
         order="the same FDR hides very different lists once the tests correlate",
         beat="An FDR is an average over studies; with correlated tests most BH lists are clean or empty and some are badly wrong",
         source="What does \"FDR 5%\" promise about the one list you have?, Figure 6; ledger L29",
         structure="Locked feed shell: one-line serif headline and a two-line setup; the panel holds two stacked histograms of BH's false discovery proportion on a shared 0 to 0.5 axis, independent tests above and tests correlated at 0.5 below, with the bars past 10% and a dashed 10% line in tangerine and each panel's statistics in a text block; the takeaway closes the card",
         alt="Two histograms of BH's false discovery proportion: tight below 0.1 for independent tests, a spike at 0 and a long tail at correlation 0.5",
         long="Benjamini–Hochberg at q = 0.05 on 3,170 one-sided tests, 20,000 simulated studies per setting. With independent tests the false discovery proportion of each study's list stays tight around its mean: FDR 0.0335 and only 0.18% of lists more than 10% false. With every pair of tests correlated at 0.5 the FDR is still 0.0260, but 8.20% of studies have a list more than 10% false; 58.7% of studies find nothing at all, which counts as a false share of 0, and 19.8% of the non-empty lists are more than 10% false. The takeaway: an FDR is an average over studies you did not run, and one list can be far dirtier than 5%.",
         keywords="false discovery proportion, false discovery rate, Benjamini-Hochberg, correlated tests, equicorrelation, Monte Carlo simulation, FDP distribution"),
    dict(stem="feed-05-storey-correlation", role="technical",
         title="Storey's q-values overshoot when the tests correlate",
         order="Storey's q-values overshoot their target as correlation rises",
         beat="Adaptive FDR control estimates the null share from the same p-values, so correlation pushes Storey's FDR far past its target while BH holds",
         source="Does Benjamini–Hochberg keep 5% when the tests are correlated?, Figure 5; ledger L29",
         structure="Locked feed shell: two-line serif headline and a setup line; the panel holds a line chart of false discovery rate against the correlation between every pair of tests, with Storey's q-values in tangerine and labelled at each point, BH in ink, BY dotted and a dashed target line at 0.05; three notes sit in the empty upper left; the takeaway closes the card",
         alt="Line chart of FDR against correlation: Storey q-values climb from 0.050 to 0.272 while BH stays near 0.03 and BY near 0.003",
         long="False discovery rate of three rules at a 0.05 target, each point 20,000 simulated studies of 3,170 one-sided tests with every pair correlated at the same level. Storey's q-values are on target with independent tests, 0.050, then rise to 0.092 at correlation 0.1, 0.141 at 0.2, 0.189 at 0.3 and 0.272 at 0.5, about 5.4 times the target. Benjamini–Hochberg falls from 0.034 to 0.026 and Benjamini–Yekutieli stays near 0.003. The ±2 Monte Carlo standard errors are smaller than the dots. The takeaway: with correlated tests use plain BH, because the q-values reached an FDR of 0.27.",
         keywords="Storey q-value, adaptive FDR, pi0 estimation, correlated tests, Benjamini-Hochberg, Benjamini-Yekutieli, simulation"),
    dict(stem="feed-06-forking-paths", role="technical",
         title="One reported test, 96 underneath",
         order="four ordinary analysis choices hide 96 tests behind one reported result",
         beat="Choices made inside one planned analysis multiply into many uncounted tests and push a 5% test to a 61% false-positive rate",
         source="How many tests did a one-analysis study run?, Figures 8 and 9; ledger L21 and L31",
         structure="Locked feed shell: one-line serif headline and a two-line setup; the panel's left column stacks the four choices with their multipliers and the product 3 × 2 × 4 × 4 = 96, and its right column is a bar chart of false-positive rates with the all-four bar in tangerine and the paper's 60.7% marked; the takeaway closes the card",
         alt="Four layers of analysis choices multiplying to 96 tests, beside bars of false-positive rates from 4.9% for one test to 61.4% for all four",
         long="Simmons, Nelson and Simonsohn's four researcher degrees of freedom, rerun on 100,000 samples with no effect anywhere: the outcome (DV1, DV2 or their mean, × 3), the stopping point (20 per cell, or 10 more, × 2), the conditions compared (three pairs or a trend, × 4) and the model (plain, with gender, or with a gender interaction that gives two tests, × 4) make 96 p-values behind one reported result. A single t-test is significant at p < .05 in 4.9% of samples; each choice alone gives 7.7% to 12.6%; all four together give 61.4% ± 0.15%, against the paper's 60.7%. The takeaway: a correction needs the number of tests m, and forks hide m, so pre-specify the analysis or count every fork.",
         keywords="forking paths, researcher degrees of freedom, p-hacking, false positive rate, Simmons Nelson Simonsohn, multiple comparisons"),
    dict(stem="feed-07-read-the-article", role="cta",
         title="Check which rule your library runs",
         order="library defaults differ, and the full article is on Canery",
         beat="R, statsmodels and SciPy agree on the adjusted values but default to different rules, so name the method in every call",
         source="The five rules in thirty lines of NumPy (the library defaults table); ledger L18, L19 and L20",
         structure="Locked feed shell: one-line serif headline and a setup line; the panel holds a three-row table of library, call and default with a note under each call, then a tangerine-outlined call-to-action box; the takeaway line gives the article address",
         alt="Table of default multiple-testing methods: R p.adjust uses holm, statsmodels multipletests uses hs, SciPy uses bh; link to the article",
         long="The libraries agree on the adjusted p-values and disagree on the defaults. R 4.5's p.adjust(p, method) defaults to \"holm\", and \"fdr\" is an alias for \"BH\". statsmodels 0.15's multipletests(p, alpha, method) defaults to 'hs', Holm–Šidák, and returns the rejections and the adjusted values. SciPy 1.18's false_discovery_control(ps, method) defaults to 'bh' and returns adjusted p-values only, with no FWER methods. The card closes with a call to read the full article on Canery, which builds the five rules by hand, runs four simulations and ships a lab, at canery.in/blogs/multiple-comparisons-fwer-fdr.",
         keywords="p.adjust, statsmodels multipletests, scipy false_discovery_control, library defaults, Holm, Holm-Sidak, Benjamini-Hochberg"),
]

LINKEDIN = """Same 3,170 genes. Same 5% level. Bonferroni finds 2 genes, Benjamini–Hochberg finds 94, Storey's q-values find 162.

The rules don't disagree about the data. They promise different things:
• Bonferroni and Holm bound the chance of even one false finding, the family-wise error rate.
• Benjamini–Hochberg bounds the expected false share of the list, the false discovery rate, and only under a condition on how the tests depend on each other.

What the simulations showed, 20,000 studies per setting:
1. "FDR 5%" is an average over studies, not a property of your list. With every pair of tests correlated at 0.5, BH's FDR was 0.026, yet 19.8% of the non-empty lists were more than 10% false.
2. Storey's q-values estimate the null share from the same p-values. Under correlation their FDR climbed from 0.050 to 0.272 against a 0.05 target. If your tests are strongly correlated, use plain BH.
3. The tests nobody counted matter most. Four ordinary analysis choices put 96 tests behind one reported p-value; with no effect anywhere, 61.4% of 100,000 samples produced something significant.

Part 9 of Statistics for Data Scientists: the five rules by hand in NumPy, matched to statsmodels and SciPy, with a lab you can rerun. Link in the first comment.

#statistics #datascience #hypothesistesting #falsediscoveryrate #multipletesting"""

FIRST_COMMENT = f"""An FDR is an average over studies you did not run; the one list you have can be far dirtier than 5%.

Read the full article on Canery: {CANON}"""

INSTAGRAM = """Same 3,170 genes, same 5% level: 2, 94 or 162 discoveries. The corrections don't disagree about the data; they promise different things. Swipe for the two error rates, BH's step-up line, why "FDR 5%" says little about your one list, how q-values overshoot when tests correlate, and the 96 tests hiding behind one reported p-value.

Read the full article on Canery, link in bio: Multiple Comparisons: FWER, FDR, and Tests You Didn't Count.

#statistics #datascience #hypothesistesting #falsediscoveryrate #pvalues #multipletesting"""


def main():
    out = ["---", "social_schema: 2", f'canonical_url: "{CANON}"', "---",
           "# Social publishing package — multiple-comparisons-fwer-fdr", "",
           "## LinkedIn post", "", LINKEDIN, "",
           "## LinkedIn first comment", "", FIRST_COMMENT, "",
           "## Instagram caption", "", INSTAGRAM, "",
           "## Shared feed order", ""]
    for i, c in enumerate(CARDS, 1):
        out.append(f"{i}. `assets/social/{c['stem']}.png` — {c['order']}")
    out += ["", "## Instagram Story", "",
            "No Story frames: this series ships feed cards only (owner decision, 2026-10-30), so the four Story checks of `validate_post.py --social` fail by design.",
            "", "### Story order", "", "None.", "", "## Asset metadata", ""]
    for c in CARDS:
        assert 80 <= len(c["alt"]) <= 160, (c["stem"], len(c["alt"]))
        out += [f"### {c['stem']}",
                f"- File: `assets/social/{c['stem']}.png`",
                f"- Title: {c['title']}",
                "- Platforms: Instagram feed, LinkedIn",
                f"- Role: {c['role']}",
                "- Dimensions: 1080×1350",
                f"- Narrative beat: {c['beat']}",
                f"- Technical source: {c['source']}",
                f"- Visual structure: {c['structure']}",
                f"- Visible-text transcript: {transcript(c['stem'])}",
                f"- Alt text: {c['alt']}",
                f"- Long description: {c['long']}",
                f"- Keywords: {c['keywords']}",
                f"- Canonical URL: {CANON}", ""]
    (POST / "social.md").write_text("\n".join(out))
    print("wrote social.md:", len(CARDS), "cards")


if __name__ == "__main__":
    main()
