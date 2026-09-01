"""Reading addresses out of an uploaded sheet.

The sheet is written by a person, so the tests are mostly about tolerating what
people actually produce — headers, several columns, blank rows, a stray note —
while refusing anything that would put a malformed address on a send list.
"""

from __future__ import annotations

import io

import pytest
from openpyxl import Workbook

from blogs.adapters.email.recipients import read_recipients
from blogs.core.errors import BlogPlatformError


def sheet(rows: list[list[object]], *, extra: list[list[object]] | None = None) -> bytes:
    book = Workbook()
    first = book.active
    assert first is not None
    for row in rows:
        first.append(row)
    if extra is not None:
        second = book.create_sheet("Second")
        for row in extra:
            second.append(row)
    buffer = io.BytesIO()
    book.save(buffer)
    return buffer.getvalue()


class TestReadRecipients:
    def test_finds_addresses_regardless_of_column_or_header(self) -> None:
        data = sheet([
            ["Name", "Notes", "Email"],
            ["Ada", "investor", "ada@example.com"],
            ["Grace", "", "grace@example.com"],
        ])
        result = read_recipients(data, limit=100)
        assert result.addresses == ("ada@example.com", "grace@example.com")

    def test_lowercases_and_deduplicates(self) -> None:
        # The same person typed twice in different case is one recipient, not
        # two emails to the same inbox.
        data = sheet([["Ada@Example.com"], ["ada@example.com"], ["ADA@EXAMPLE.COM"]])
        result = read_recipients(data, limit=100)
        assert result.addresses == ("ada@example.com",)
        assert result.duplicates == 2

    def test_reads_every_worksheet(self) -> None:
        data = sheet([["a@example.com"]], extra=[["b@example.com"]])
        assert set(read_recipients(data, limit=100).addresses) == {
            "a@example.com",
            "b@example.com",
        }

    def test_counts_non_addresses_instead_of_guessing(self) -> None:
        data = sheet([["Name", "Email"], ["Ada", "not-an-email"], ["Grace", "g@example.com"]])
        result = read_recipients(data, limit=100)
        assert result.addresses == ("g@example.com",)
        # Every non-address cell counts, headers and name columns included,
        # so this is a rough signal rather than an error count: "Name", "Email",
        # "Ada" and "not-an-email" are four, plus "Grace".
        assert result.skipped == 5

    def test_rejects_a_cell_that_merely_contains_an_address(self) -> None:
        # "contact: a@b.com" means the sheet is not the shape we think it is.
        # Half-parsing it would send to a plausible-looking wrong address.
        data = sheet([["contact: a@example.com"]])
        assert read_recipients(data, limit=100).addresses == ()

    def test_ignores_blank_rows_and_none_cells(self) -> None:
        data = sheet([[None, None], ["  "], ["a@example.com"], []])
        assert read_recipients(data, limit=100).addresses == ("a@example.com",)

    def test_refuses_outright_past_the_limit(self) -> None:
        data = sheet([[f"user{i}@example.com"] for i in range(10)])
        # Refused, not truncated: a half-sent announcement is worse than none,
        # because there is no way to tell who already received it.
        with pytest.raises(BlogPlatformError) as caught:
            read_recipients(data, limit=5)
        assert caught.value.category.value == "REQUEST_INVALID"

    def test_a_non_xlsx_file_is_a_readable_refusal(self) -> None:
        with pytest.raises(BlogPlatformError) as caught:
            read_recipients(b"this is a csv, actually", limit=100)
        assert caught.value.safe_details["reason"] == "NOT_XLSX"
