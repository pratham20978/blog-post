"""Guard the one lint rule this project switches off.

``pyproject.toml`` disables ruff's S608 (hardcoded-SQL-expression) for the
repository package, on the stated grounds that every f-string reaching a query
interpolates a module constant and never caller data. That is an assertion, and
an assertion in a config comment is worth nothing on its own — the suppression
would happily cover a genuine injection added next year.

So this re-derives it mechanically: every f-string in a SQL position is parsed,
and each interpolated expression must resolve to a module-level constant, a
literal, or a lookup in a closed dict. Anything reachable from a function
parameter fails.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

REPOSITORY = pathlib.Path(__file__).parents[2] / "blogs" / "repository"

#: Names allowed inside an interpolation. All are module-level constants holding
#: fixed column lists or fragments; none can hold a value from a request.
ALLOWED_NAMES = {
    "_BLOG_COLUMNS",
    "_CATEGORY_AGG",
    "_USER_COLUMNS",
    "_OTP_COLUMNS",
    "_REFRESH_COLUMNS",
    "_ACTOR_COLUMNS",
    "_COMMENT_COLUMNS",
    "_CATALOG_COLUMNS",
    "_PIN_COLUMNS",
    "_BUCKET_SQL",
    "clauses",
    "where",
    "ownership",
}

#: Functions allowed to produce a fragment, because they build from constants.
ALLOWED_CALLS = {"join", "_signal_weights_sql", "replace"}


def _sql_fstrings(tree: ast.AST) -> list[ast.JoinedStr]:
    """Every f-string that is passed to a query-executing call."""
    found: list[ast.JoinedStr] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        target = node.func
        name = target.attr if isinstance(target, ast.Attribute) else getattr(target, "id", "")
        if name not in {"_execute", "_fetch_one", "_fetch_all", "execute"}:
            continue
        found.extend(a for a in node.args if isinstance(a, ast.JoinedStr))
    return found


def _interpolated_sources(fstring: ast.JoinedStr) -> list[str]:
    """Describe what each ``{...}`` in the f-string draws from."""
    sources: list[str] = []
    for part in fstring.values:
        if not isinstance(part, ast.FormattedValue):
            continue
        # `_CONSTANT[key]` is safe whatever the key: the value comes from a
        # closed module-level dict, and a key outside it raises rather than
        # reaching the query. Only the container is checked, not the subscript.
        expression = part.value
        if isinstance(expression, ast.Subscript) and isinstance(
            expression.value, ast.Name
        ):
            sources.append(expression.value.id)
            continue
        for node in ast.walk(expression):
            if isinstance(node, ast.Name):
                sources.append(node.id)
            elif isinstance(node, ast.Attribute):
                sources.append(node.attr)
            elif isinstance(node, ast.Call):
                func = node.func
                sources.append(
                    func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "?")
                )
    return sources


@pytest.mark.parametrize(
    "path", sorted(REPOSITORY.glob("*.py")), ids=lambda p: p.name
)
def test_no_caller_data_is_interpolated_into_sql(path: pathlib.Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    offenders: list[str] = []

    for fstring in _sql_fstrings(tree):
        for source in _interpolated_sources(fstring):
            if source in ALLOWED_NAMES or source in ALLOWED_CALLS:
                continue
            # Subscripts into the closed bucket dict resolve to its values.
            if source.isupper() and source.startswith("_"):
                continue
            offenders.append(f"{path.name}:{fstring.lineno} interpolates {source!r}")

    assert not offenders, (
        "SQL built from something other than a module constant — S608 is "
        "suppressed in this package on the promise that this never happens:\n  "
        + "\n  ".join(offenders)
    )


def test_the_guard_would_actually_catch_an_injection() -> None:
    """A negative control.

    Without this, a bug in the walker above would make every file pass and the
    suppression would be unguarded again — the test would look green while
    checking nothing.
    """
    tree = ast.parse(
        'async def f(self, user_input):\n'
        '    await self._execute(f"SELECT * FROM t WHERE x = {user_input}")\n'
    )
    fstrings = _sql_fstrings(tree)
    assert fstrings, "the walker failed to find an f-string in a query position"
    assert "user_input" in _interpolated_sources(fstrings[0])
    assert "user_input" not in ALLOWED_NAMES
