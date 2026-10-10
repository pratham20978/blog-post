#!/usr/bin/env python3
"""Build a lab's notebook.ipynb from its README and its anchored code cells, and execute it.

Usage:
    uv run --no-project --with nbclient --with nbformat --with ipykernel \\
        [--with-requirements posts/<slug>/lab/requirements.txt] \\
        python build_lab_notebook.py posts/<slug>/ [--timeout SECONDS]
    python3 build_lab_notebook.py posts/<slug>/ --convert-only [--out PATH]

The notebook is lab/README.md, verbatim and split at its headings, with the code
cells of the private <post>/lab-cells.py placed under the headings they name. A
python fence in the README outside an answer becomes a runnable cell too. Every
code cell not marked [skip-build] runs top to bottom in a fresh kernel and a
fresh copy of the lab. Only then is the notebook written, with its outputs
cleared and a receipt that tells the validator when it has gone stale.
--convert-only skips execution, writes no receipt and never writes into lab/.

Exit codes: 0 built, 1 the build failed and nothing was written, 2 could not read inputs.
"""

import argparse
import datetime as dt
import json
import os
import pathlib
import platform
import re
import shutil
import sys
import tempfile
import textwrap
import time

try:
    from .validate_post import (
        LAB_CELLS_FILE, NOTEBOOK_FILE, lab_cells_digest, lab_inputs_digest, publishable_lab_files,
    )
except ImportError:  # run as a script rather than as part of the scripts package
    from validate_post import (
        LAB_CELLS_FILE, NOTEBOOK_FILE, lab_cells_digest, lab_inputs_digest, publishable_lab_files,
    )

HEADING_RE = re.compile(r"^ {0,3}#{1,6}[ \t]+(?P<text>.*?)(?:[ \t]+#+)?[ \t]*$")
FENCE_OPEN_RE = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>[^`]*)$")
DETAILS_OPEN_RE = re.compile(r"<details\b", re.I)
DETAILS_CLOSE_RE = re.compile(r"</details\s*>", re.I)
CELL_MARKER_RE = re.compile(
    r"^# %%[ \t]+after:[ \t]*(?P<anchor>.*?)[ \t]*(?P<skip>\[skip-build\])?[ \t]*$"
)
SKIP_TAG = "skip-build"
KERNELSPEC = {"display_name": "Python 3", "language": "python", "name": "python3"}
UV_COMMAND = (
    "uv run --no-project --with nbclient --with nbformat --with ipykernel "
    "[--with-requirements <post>/lab/requirements.txt] python build_lab_notebook.py <post> "
    "(the pinned versions are in references/labs.md)"
)


class BuildError(Exception):
    """A problem that stops the build; its message says what to fix."""


def trim_blank(lines):
    """Drop the blank lines at both ends of a block."""
    start, end = 0, len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]


def parse_readme(text):
    """Split a README into sections at its headings, outside code fences and answers.

    Each section holds its heading, its items in order, ("md", lines) or ("code",
    lines), and the item index where its first <details> answer starts. A python
    fence outside an answer becomes a code item; every other fence stays markdown.
    """
    sections = []
    section = {"heading": None, "items": [], "answer_at": None}
    markdown = []
    fence = None  # (character, length, promoted, body)
    depth = 0

    def flush():
        lines = trim_blank(markdown)
        if lines:
            section["items"].append(("md", lines))
        markdown.clear()

    for line in text.splitlines():
        if fence is not None:
            character, length, promoted, body = fence
            closing = line.strip()
            if closing and set(closing) == {character} and len(closing) >= length:
                if promoted:
                    flush()
                    code = trim_blank(textwrap.dedent("\n".join(body)).splitlines())
                    if code:
                        section["items"].append(("code", code))
                else:
                    markdown.append(line)
                fence = None
            else:
                (body if promoted else markdown).append(line)
            continue
        opened = FENCE_OPEN_RE.match(line)
        if opened:
            info = opened.group("info").split()
            promoted = depth == 0 and bool(info) and info[0].casefold() == "python"
            fence = (opened.group("fence")[0], len(opened.group("fence")), promoted, [])
            if not promoted:
                markdown.append(line)
            continue
        heading = HEADING_RE.match(line) if depth == 0 else None
        if heading and heading.group("text"):
            flush()
            sections.append(section)
            section = {"heading": heading.group("text"), "items": [], "answer_at": None}
            markdown.append(line)
            continue
        opens = len(DETAILS_OPEN_RE.findall(line))
        if opens and depth == 0 and section["answer_at"] is None:
            flush()
            section["answer_at"] = len(section["items"])
        depth = max(0, depth + opens - len(DETAILS_CLOSE_RE.findall(line)))
        markdown.append(line)
    if fence is not None:
        raise BuildError("lab/README.md: a code fence is never closed")
    flush()
    sections.append(section)
    return [s for s in sections if s["heading"] is not None or s["items"]]


def parse_cells(text):
    """Read the anchored code cells: each starts with '# %% after: <README heading>'."""
    cells = []
    current = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = CELL_MARKER_RE.match(line)
        if marker:
            if not marker.group("anchor"):
                raise BuildError(f"{LAB_CELLS_FILE}:{number}: the marker names no README heading")
            current = {
                "anchor": marker.group("anchor"),
                "skip": bool(marker.group("skip")),
                "line": number,
                "lines": [],
            }
            cells.append(current)
        elif line.startswith("# %%"):
            raise BuildError(
                f"{LAB_CELLS_FILE}:{number}: a cell marker reads "
                "'# %% after: <README heading>', optionally ending in [skip-build]"
            )
        elif current is None:
            if line.strip() and not line.lstrip().startswith("#"):
                raise BuildError(f"{LAB_CELLS_FILE}:{number}: code before the first cell marker")
        else:
            current["lines"].append(line)
    for cell in cells:
        cell["lines"] = trim_blank(cell["lines"])
        if not cell["lines"]:
            raise BuildError(f"{LAB_CELLS_FILE}:{cell['line']}: the cell under this marker is empty")
    return cells


def normalise(text):
    return " ".join(text.replace("`", "").replace("*", "").split()).casefold()


def heading_matches(anchor, heading):
    """An anchor names a heading by its whole text or by a prefix that ends at a word."""
    anchor, heading = normalise(anchor), normalise(heading)
    return heading == anchor or (
        heading.startswith(anchor) and not heading[len(anchor)].isalnum()
    )


def assemble(sections, cells):
    """Place each anchored cell in its section, before the section's first answer.

    Returns (kind, lines, skip, heading) items in notebook order.
    """
    placed = {index: [] for index in range(len(sections))}
    for cell in cells:
        matches = [
            index for index, section in enumerate(sections)
            if section["heading"] and heading_matches(cell["anchor"], section["heading"])
        ]
        if len(matches) != 1:
            found = "no README heading" if not matches else "several README headings: " + "; ".join(
                sections[index]["heading"] for index in matches
            )
            raise BuildError(f"{LAB_CELLS_FILE}:{cell['line']}: '{cell['anchor']}' matches {found}")
        placed[matches[0]].append(("code", cell["lines"], cell["skip"]))
    items = []
    for index, section in enumerate(sections):
        ordered = [(kind, lines, False) for kind, lines in section["items"]]
        at = section["answer_at"] if section["answer_at"] is not None else len(ordered)
        ordered[at:at] = placed[index]
        items.extend((kind, lines, skip, section["heading"]) for kind, lines, skip in ordered)
    return items


def check_code(source, where):
    try:
        compile(source, where, "exec")
    except SyntaxError as exc:
        hint = ""
        if any(line.lstrip()[:1] in ("!", "%") for line in source.splitlines()):
            hint = "; cells are plain Python, so run a command with subprocess and sys.executable"
        raise BuildError(f"{where}: not valid Python ({exc.msg}, line {exc.lineno}){hint}") from None


def cell_id(number, heading):
    slug = re.sub(r"[^a-z0-9]+", "-", (heading or "").casefold()).strip("-")[:59].strip("-")
    return f"{number:03d}-{slug or 'start'}"


def build_notebook(post):
    """Return the unexecuted notebook and, for each code cell id, where it sits."""
    readme = (post / "lab" / "README.md").read_text(encoding="utf-8")
    cells_file = post / LAB_CELLS_FILE
    cells = parse_cells(cells_file.read_text(encoding="utf-8")) if cells_file.is_file() else []
    items = assemble(parse_readme(readme), cells)
    notebook_cells, wheres = [], {}
    for number, (kind, lines, skip, heading) in enumerate(items, 1):
        identifier = cell_id(number, heading)
        source = "\n".join(lines).splitlines(keepends=True)
        if kind == "md":
            notebook_cells.append(
                {"cell_type": "markdown", "id": identifier, "metadata": {}, "source": source}
            )
            continue
        where = f"the code cell under '{heading}'" if heading else "the first code cell"
        check_code("".join(source), where)
        wheres[identifier] = where
        notebook_cells.append({
            "cell_type": "code",
            "execution_count": None,
            "id": identifier,
            "metadata": {"tags": [SKIP_TAG]} if skip else {},
            "outputs": [],
            "source": source,
        })
    notebook = {
        "cells": notebook_cells,
        "metadata": {"kernelspec": dict(KERNELSPEC), "language_info": {"name": "python"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    return notebook, wheres


def output_text(cell):
    parts = []
    for output in cell.get("outputs", []):
        if output.get("output_type") == "stream":
            parts.append(output.get("text", ""))
        elif output.get("output_type") == "error":
            parts.append("\n".join(output.get("traceback", [])))
        else:
            parts.append(output.get("data", {}).get("text/plain", ""))
    return "".join(part if isinstance(part, str) else "".join(part) for part in parts)


def duration(cell):
    timing = cell.get("metadata", {}).get("execution", {})
    try:
        start = dt.datetime.fromisoformat(timing["iopub.execute_input"].replace("Z", "+00:00"))
        end = dt.datetime.fromisoformat(timing["shell.execute_reply"].replace("Z", "+00:00"))
    except (KeyError, ValueError, AttributeError):
        return None
    return (end - start).total_seconds()


def failure(run, runnable, wheres, exc, kernel_log=""):
    """Say which cell failed and why, mapping the run back to the README."""
    for index, cell in enumerate(run.cells):
        for output in cell.get("outputs", []):
            if output.get("output_type") != "error":
                continue
            if index == 0:
                return f"the kernel could not start a Python session: {output.get('evalue')}"
            where = wheres[runnable[index - 1]["id"]]
            message = f"{where} failed: {output.get('ename')}: {output.get('evalue')}"
            if output.get("ename") == "ModuleNotFoundError":
                message += " (pass --with-requirements <post>/lab/requirements.txt to uv)"
            return message
    first = str(exc).strip().splitlines()
    message = f"execution stopped: {type(exc).__name__}: {first[0] if first else ''}"
    tail = kernel_log.strip().splitlines()[-5:]
    return message + ("\nthe kernel's last words:\n  " + "\n  ".join(tail) if tail else "")


def execute(post, notebook, wheres, timeout):
    """Run every code cell not marked skip-build in a fresh kernel and a fresh copy of the lab."""
    try:
        import nbformat
        from nbclient import NotebookClient
    except ImportError as exc:
        raise BuildError(f"{exc.name} is not installed; run the build as: {UV_COMMAND}") from None
    runnable = [
        cell for cell in notebook["cells"]
        if cell["cell_type"] == "code" and SKIP_TAG not in cell["metadata"].get("tags", [])
    ]
    run = nbformat.v4.new_notebook(metadata={"kernelspec": dict(KERNELSPEC)})
    # The probe proves the kernel runs in this environment, the one built from requirements.txt.
    run.cells = [nbformat.v4.new_code_cell("import sys\nprint(sys.prefix)")] + [
        nbformat.v4.new_code_cell("".join(cell["source"])) for cell in runnable
    ]
    with tempfile.TemporaryDirectory(prefix="lab-notebook-") as scratch:
        for relative in publishable_lab_files(post):
            if relative == NOTEBOOK_FILE:
                continue
            target = pathlib.Path(scratch, pathlib.PurePosixPath(relative).relative_to("lab"))
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(post / relative, target)
        client = NotebookClient(
            run, timeout=timeout, kernel_name="python3",
            resources={"metadata": {"path": scratch}},
        )
        started = time.monotonic()
        # The kernel's own streams carry its warnings and an echo of what cells print; the
        # notebook already receives the output, so keep them out of the build report.
        with tempfile.TemporaryFile() as kernel_out, tempfile.TemporaryFile() as kernel_err:
            try:
                client.execute(stdout=kernel_out, stderr=kernel_err)
            except Exception as exc:  # a failing cell, a timeout, or a dead kernel
                kernel_err.seek(0)
                log = kernel_err.read().decode("utf-8", "replace")
                raise BuildError(failure(run, runnable, wheres, exc, log)) from None
        seconds = time.monotonic() - started
        prefix = output_text(run.cells[0]).strip()
        if prefix != sys.prefix:
            raise BuildError(
                "the kernel ran outside this environment; a user-level python3 kernelspec "
                "may be shadowing the one ipykernel provides"
            )
        home = str(pathlib.Path.home())
        timings = []
        for cell, ran in zip(runnable, run.cells[1:]):
            where = wheres[cell["id"]]
            text = output_text(ran)
            for path in {scratch, os.path.realpath(scratch)}:
                text = text.replace(path, ".")
            if home in text:
                raise BuildError(
                    f"{where} printed a path in your home directory; "
                    "print paths relative to the lab folder"
                )
            timings.append((duration(ran), where))
    return seconds, timings


def dumps(notebook):
    return json.dumps(notebook, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("post_dir")
    ap.add_argument("--timeout", type=int, default=3600,
                    help="seconds one cell may run before the build fails (default 3600)")
    ap.add_argument("--convert-only", action="store_true",
                    help="build without executing: no receipt, and never into lab/")
    ap.add_argument("--out", help="with --convert-only, the file to write (default: stdout)")
    args = ap.parse_args(argv)

    post = pathlib.Path(args.post_dir)
    readme = post / "lab" / "README.md"
    if not readme.is_file():
        print(f"Cannot read {readme}", file=sys.stderr)
        return 2
    try:
        notebook, wheres = build_notebook(post)
        if args.convert_only:
            if not args.out:
                sys.stdout.write(dumps(notebook))
                return 0
            out = pathlib.Path(args.out).resolve()
            if (post / "lab").resolve() in out.parents:
                raise BuildError("--convert-only never writes into lab/: an unexecuted notebook is not shippable")
            out.write_text(dumps(notebook), encoding="utf-8")
            print(f"wrote {out} (not executed, no receipt)")
            return 0

        before = lab_inputs_digest(post), lab_cells_digest(post)
        seconds, timings = execute(post, notebook, wheres, args.timeout)
        if (lab_inputs_digest(post), lab_cells_digest(post)) != before:
            raise BuildError("the lab or lab-cells.py changed while the build ran; build again")
        notebook["metadata"]["blog_forge"] = {
            "built": dt.datetime.now(dt.timezone.utc).date().isoformat(),
            "cells_sha256": before[1],
            "lab_sha256": before[0],
            "python": platform.python_version(),
            "seconds": round(seconds),
        }
        import nbformat
        try:
            nbformat.validate(nbformat.from_dict(notebook))
        except nbformat.ValidationError as exc:
            raise BuildError(f"the notebook fails the nbformat schema: {exc.message}") from None
        target = post / NOTEBOOK_FILE
        partial = target.with_name(".notebook.ipynb.partial")
        partial.write_text(dumps(notebook), encoding="utf-8")
        os.replace(partial, target)
    except BuildError as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1

    code = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    skipped = sum(SKIP_TAG in cell["metadata"].get("tags", []) for cell in code)
    print(
        f"wrote {NOTEBOOK_FILE}: {len(notebook['cells']) - len(code)} markdown and "
        f"{len(code)} code cells, {skipped} marked {SKIP_TAG}"
    )
    print(f"executed in {seconds:.0f} s on Python {platform.python_version()}; slowest cells:")
    for taken, where in sorted((t for t in timings if t[0] is not None), reverse=True)[:3]:
        print(f"  {taken:8.1f} s  {where}")
    archive = post / f"lab-{post.resolve().name}.zip"
    if archive.exists():
        print(f"rebuild {archive.name} now: the notebook is a lab file (references/labs.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
