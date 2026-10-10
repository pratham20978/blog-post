"""Conversion tests for build_lab_notebook: README sections, anchored cells, and the shipped JSON."""

from __future__ import annotations

import io
import json
import re
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from .build_lab_notebook import (
    BuildError,
    assemble,
    build_notebook,
    dumps,
    main,
    parse_cells,
    parse_readme,
)

README = """# Lab — Toy

- **Grade:** G1 · runs anywhere

## Run

```bash
# not a heading: a shell comment inside a fence
python run.py
```

## Exercises

### E1 — Reproduce: the total

Run it.

**Self-check:** prints 42.

<details><summary>Answer</summary>

```python
print("a fragment inside an answer")
```

</details>

### E3 — Predict: doubling

```python
import run
print(run.total(2))
```

**Self-check:** 84.

<details><summary>Answer</summary>

84.

</details>
"""


def kinds(items, heading):
    """The (kind, first line) of every item under one heading."""
    return [(kind, lines[0]) for kind, lines, _, owner in items if owner == heading]


def post_with(directory: str, readme: str = README, cells: str | None = None) -> Path:
    root = Path(directory)
    (root / "lab").mkdir()
    (root / "lab" / "README.md").write_text(readme, encoding="utf-8")
    (root / "lab" / "run.py").write_text("def total(k=1):\n    return 42 * k\n", encoding="utf-8")
    if cells is not None:
        (root / "lab-cells.py").write_text(cells, encoding="utf-8")
    return root


class ReadmeTests(unittest.TestCase):
    def test_lines_starting_with_hash_inside_a_fence_are_not_headings(self) -> None:
        headings = [section["heading"] for section in parse_readme(README)]
        self.assertEqual(
            headings,
            ["Lab — Toy", "Run", "Exercises", "E1 — Reproduce: the total", "E3 — Predict: doubling"],
        )

    def test_python_fence_outside_an_answer_becomes_a_code_cell(self) -> None:
        items = assemble(parse_readme(README), [])
        self.assertIn(("code", "import run"), kinds(items, "E3 — Predict: doubling"))

    def test_fences_inside_answers_and_shell_fences_stay_markdown(self) -> None:
        items = assemble(parse_readme(README), [])
        code = [lines for kind, lines, _, _ in items if kind == "code"]
        self.assertEqual(code, [["import run", "print(run.total(2))"]])

    def test_an_unclosed_fence_fails(self) -> None:
        with self.assertRaises(BuildError):
            parse_readme("# Lab\n\n```python\nprint(1)\n")


class CellPlacementTests(unittest.TestCase):
    def test_an_anchored_cell_lands_after_the_self_check_and_before_the_answer(self) -> None:
        items = assemble(parse_readme(README), parse_cells("# %% after: E1\nprint(total)\n"))
        self.assertEqual(
            kinds(items, "E1 — Reproduce: the total"),
            [
                ("md", "### E1 — Reproduce: the total"),
                ("code", "print(total)"),
                ("md", "<details><summary>Answer</summary>"),
            ],
        )

    def test_a_section_without_an_answer_takes_the_cell_at_its_end(self) -> None:
        items = assemble(parse_readme(README), parse_cells("# %% after: Run\nimport run\n"))
        self.assertEqual(kinds(items, "Run"), [("md", "## Run"), ("code", "import run")])

    def test_cells_keep_their_order_within_a_section(self) -> None:
        cells = parse_cells("# %% after: Run\nfirst = 1\n\n# %% after: Run\nsecond = 2\n")
        items = assemble(parse_readme(README), cells)
        self.assertEqual(
            kinds(items, "Run"), [("md", "## Run"), ("code", "first = 1"), ("code", "second = 2")]
        )

    def test_an_anchor_must_match_exactly_one_heading(self) -> None:
        with self.assertRaisesRegex(BuildError, "no README heading"):
            assemble(parse_readme(README), parse_cells("# %% after: E9\npass\n"))
        both = README + "\n## Run order\n\nText.\n"
        with self.assertRaisesRegex(BuildError, "several README headings"):
            assemble(parse_readme(both), parse_cells("# %% after: Run\npass\n"))

    def test_a_prefix_anchor_ends_at_a_word(self) -> None:
        readme = "# Lab\n\n### E1 — One\n\nA.\n\n### E10 — Ten\n\nB.\n"
        items = assemble(parse_readme(readme), parse_cells("# %% after: E1\npass\n"))
        self.assertEqual(kinds(items, "E10 — Ten"), [("md", "### E10 — Ten")])

    def test_skip_build_marks_the_cell(self) -> None:
        cells = parse_cells("# %% after: E3 — Predict  [skip-build]\nverify()\n")
        self.assertEqual((cells[0]["anchor"], cells[0]["skip"]), ("E3 — Predict", True))


class CellsFileTests(unittest.TestCase):
    def test_malformed_cells_files_fail_with_a_line_number(self) -> None:
        cases = {
            "x = 1\n# %% after: Run\npass\n": "lab-cells.py:1: code before the first cell marker",
            "# %% Run\npass\n": "lab-cells.py:1: a cell marker reads",
            "# %% after: Run\n\n# %% after: E1\npass\n": "lab-cells.py:1: the cell under this marker is empty",
            "# %% after:\npass\n": "lab-cells.py:1: the marker names no README heading",
        }
        for text, message in cases.items():
            with self.subTest(text=text), self.assertRaises(BuildError) as caught:
                parse_cells(text)
            self.assertIn(message, str(caught.exception))

    def test_comments_before_the_first_marker_are_allowed(self) -> None:
        cells = parse_cells("# Cells for the toy lab.\n\n# %% after: Run\npass\n")
        self.assertEqual(len(cells), 1)

    def test_shell_magics_are_rejected_with_the_reason(self) -> None:
        with TemporaryDirectory() as directory:
            root = post_with(directory, cells="# %% after: Run\n!python run.py\n")
            with self.assertRaisesRegex(BuildError, "subprocess and sys.executable"):
                build_notebook(root)


class NotebookTests(unittest.TestCase):
    def test_the_notebook_is_deterministic_cleared_and_well_formed(self) -> None:
        with TemporaryDirectory() as directory:
            root = post_with(directory, cells="# %% after: E1\nimport run\nprint(run.total())\n")
            first, wheres = build_notebook(root)
            second, _ = build_notebook(root)
            self.assertEqual(dumps(first), dumps(second))
            self.assertEqual((first["nbformat"], first["nbformat_minor"]), (4, 5))
            ids = [cell["id"] for cell in first["cells"]]
            self.assertEqual(len(ids), len(set(ids)))
            self.assertTrue(all(re.fullmatch(r"[a-z0-9-]{1,64}", value) for value in ids))
            code = [cell for cell in first["cells"] if cell["cell_type"] == "code"]
            self.assertEqual(len(code), 2)
            self.assertTrue(all(c["outputs"] == [] and c["execution_count"] is None for c in code))
            self.assertEqual(set(wheres), {cell["id"] for cell in code})
            self.assertNotIn("blog_forge", first["metadata"])

    def test_the_readme_text_survives_verbatim(self) -> None:
        with TemporaryDirectory() as directory:
            notebook, _ = build_notebook(post_with(directory))
            markdown = "\n".join(
                "".join(cell["source"]) for cell in notebook["cells"] if cell["cell_type"] == "markdown"
            )
            for line in README.splitlines():
                if line.strip() and line not in ("```python", "import run", "print(run.total(2))"):
                    self.assertIn(line, markdown)

    def test_convert_only_never_writes_into_lab(self) -> None:
        with TemporaryDirectory() as directory:
            root = post_with(directory)
            with redirect_stderr(io.StringIO()):
                self.assertEqual(
                    main([str(root), "--convert-only", "--out", str(root / "lab" / "x.ipynb")]), 1
                )
            self.assertFalse((root / "lab" / "x.ipynb").exists())
            out = Path(directory) / "draft.ipynb"
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(root), "--convert-only", "--out", str(out)]), 0)
            self.assertNotIn("blog_forge", json.loads(out.read_text(encoding="utf-8"))["metadata"])

    def test_a_missing_readme_cannot_be_read(self) -> None:
        with TemporaryDirectory() as directory, redirect_stderr(io.StringIO()):
            self.assertEqual(main([directory, "--convert-only"]), 2)


if __name__ == "__main__":
    unittest.main()
