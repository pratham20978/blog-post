"""Write assets/linkedin-prompts.md for Part 9 (private build script, never uploaded).

Five self-contained image prompts for an alternative LinkedIn carousel. The CONSTRAINTS block is
copied verbatim from the blog-visuals skill.
Usage: python3 assets/_linkedin_prompts.py
"""
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
skill = next(pathlib.Path("/root/.claude/skills/synced").rglob("blog-visuals/SKILL.md")).read_text()
CONS = re.search(r"CONSTRAINTS\n(4:5 portrait frame.*?)\n```", skill, re.S).group(1).strip()
assert CONS.startswith("4:5 portrait frame") and "Maintain the same visual world" in CONS
WORLD = ("The recurring world of this sequence: round sieves with fine meshes, small silver-grey beads that stand for "
         "tests with nothing behind them, solid jet-black beads that stand for real effects, and shallow collection trays "
         "that hold whatever a sieve lets through.")
FRAMES = [
    ("Lucky noise", "lucky-noise",
     "with thousands of tests at one threshold, some pure noise passes by chance and sits in the results beside the real finds",
     "A long row of sieves over one tray; most grey beads stay caught, a few slip into the tray beside dark beads, one falling bead highlighted",
     "A 4:5 LinkedIn carousel frame, the first of five, showing why testing thousands of hypotheses at once lets noise into the results.",
     "A long row of identical round sieves recedes in gentle isometric perspective from the lower left toward the upper right, each catching a light shower of silver-grey beads falling from above. One shallow collection tray runs beneath the whole row. Almost every grey bead stays caught in its mesh, but a scattering have slipped through into the tray, where they lie mixed with a handful of solid jet-black beads.",
     "The single focal element is one grey bead caught mid-fall just below a mesh, outlined in atomic-tangerine: a false discovery as it happens. Fine one-pixel strokes for the meshes and rims, flat fills, and a calm empty band across the top third."),
    ("Two promises", "two-promises",
     "FWER control keeps any false find out of the list; FDR control lets a small, steady share in and keeps far more real finds",
     "Two trays under one row of sieves: two dark beads behind a very fine mesh, and many dark beads with a few grey ones behind a coarser mesh",
     "A 4:5 LinkedIn carousel frame, the second of five, contrasting the two promises a multiple-testing correction can make.",
     "Two collection trays stand side by side under the same row of round sieves. The left tray sits behind an extra-fine mesh that lets almost nothing through: it holds only two jet-black beads and no grey bead at all, while many dark beads stay stuck on the mesh above it. The right tray sits behind a coarser mesh and holds many jet-black beads with a few silver-grey beads mixed in.",
     "The single focal element is a small atomic-tangerine level mark on the outer wall of the right tray, marking the share of grey beads it is allowed on average. Both trays are drawn the same size and at the same height so the contrast is in their contents alone."),
    ("The step-up line", "step-up-line",
     "Benjamini-Hochberg sorts the evidence and keeps every item up to the last one that sits under a line rising with rank",
     "Beads sorted by size along a rising ramp edge; every bead up to the last one under the edge drops into a channel; that bead is marked",
     "A 4:5 LinkedIn carousel frame, the third of five, showing how the Benjamini-Hochberg rule decides how many results to keep.",
     "A single row of beads, sorted from the smallest to the largest, rests along the floor of a long open channel. Above them a straight ramp edge rises gently and steadily from left to right. The beads on the left sit beneath the ramp edge and drop into the channel; past a certain point the beads are taller than the edge and stay outside it, on a ledge.",
     "The single focal element is the last bead still under the ramp edge, filled atomic-tangerine; every bead to its left is kept, including any that sits close to the edge. Mostly jet-black beads on the kept side and silver-grey beads beyond it, in clean isometric line work."),
    ("Same average, different lists", "same-average",
     "an FDR is an average over repeated studies; when tests move together most lists are clean or empty and a few are badly wrong",
     "A shelf of identical small trays from repeated runs: most empty or holding only dark beads, one tray crowded with grey beads, highlighted",
     "A 4:5 LinkedIn carousel frame, the fourth of five, showing that a false discovery rate describes many repeated studies, not the one list in hand.",
     "A long shelf holds a row of identical small collection trays, each the result of one repeated run of the same sieving. Many trays are empty, many hold only a few jet-black beads, a few hold one stray silver-grey bead, and one tray near the end is crowded with silver-grey beads.",
     "The single focal element is the rim of the crowded tray, drawn in atomic-tangerine. The trays are evenly spaced and identical in shape so the eye compares their contents; the shelf recedes slightly in isometric perspective with generous empty space above it."),
    ("Forking paths", "forking-paths",
     "choices made after seeing the data multiply hidden tests, so a correction never sees the real number of tests",
     "One chute branching into many smaller chutes, each with its own sieve, all draining into one small tray, with one branch highlighted",
     "A 4:5 LinkedIn carousel frame, the last of five, showing how analysis choices hide many tests behind one reported result.",
     "A single feed chute at the top splits into two, then each branch splits again, and again, into a fan of many narrow chutes. Each branch ends in its own small round sieve, and every sieve drains into one small collection tray at the bottom that holds a single bead.",
     "The single focal element is the one branch of chutes that delivered the bead, traced in atomic-tangerine from the top to its sieve; all the other branches stay blue-slate and silver and look equally possible. Symmetric, tree-like composition with clean isometric line work."),
]


def main():
    out = ["# LinkedIn image prompts — multiple-comparisons-fwer-fdr", "",
           "An alternative five-frame carousel to generate with an image tool. Each prompt stands alone; together they "
           "follow one arc: the problem, the two promises, the mechanism, the consequence, the uncounted tests.", ""]
    for i, (name, slug, beat, alt, scene, subject, details) in enumerate(FRAMES, 1):
        assert 80 <= len(alt) <= 140, (i, len(alt))
        out += [f"## {i:02d} — {name}", f"- Narrative beat: {beat}", f"- File: linkedin-{i:02d}-{slug}.png",
                f"- Alt text: {alt}", "### Prompt", "```text", "SCENE AND INTENDED USE", scene, "",
                "SUBJECT", subject + " " + WORLD, "", "KEY DETAILS", details, "", "CONSTRAINTS", CONS, "```", ""]
    (HERE / "linkedin-prompts.md").write_text("\n".join(out))
    print("wrote", len(FRAMES), "prompts")


if __name__ == "__main__":
    main()
