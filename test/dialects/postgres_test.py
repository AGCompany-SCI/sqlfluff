"""Tests specific to the postgres dialect."""

from typing import Callable

import pytest
from _pytest.logging import LogCaptureFixture

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.errors import SQLParseError
from sqlfluff.dialects.dialect_postgres_keywords import (
    get_keywords,
    priority_keyword_merge,
)


@pytest.mark.parametrize(
    "datatype,valid",
    [
        ("between", False),
        ("coalesce", False),
        ("not", False),
        ("select", False),
        ("bigint", True),
        ("dec(5, 2)", True),
        ("nchar(10)", True),
        ('"between"', True),
        ("public.between", True),
        ("public.select", True),
    ],
)
def test_postgres_datatype_keyword_category(datatype: str, valid: bool) -> None:
    """Keywords barred from type names remain legal in other identifier roles."""
    result = Linter(dialect="postgres").parse_string(
        f"CREATE TABLE test_table (type {datatype} NOT NULL);"
    )
    assert any(isinstance(v, SQLParseError) for v in result.violations) != valid


def test_postgres_cast_rejects_not_as_datatype() -> None:
    """Preserve the existing datatype parser's NOT exclusion in casts."""
    result = Linter(dialect="postgres").parse_string("SELECT NULL::NOT;")
    assert any(isinstance(v, SQLParseError) for v in result.violations)


@pytest.mark.parametrize("datatype", ["between", "coalesce", "not", "select"])
def test_postgres_datatype_segment_rejects_keyword(
    datatype: str,
    caplog: LogCaptureFixture,
    dialect_specific_segment_not_match: Callable,
) -> None:
    """Reject forbidden names at the datatype segment itself."""
    dialect_specific_segment_not_match("postgres", "DatatypeSegment", datatype, caplog)


@pytest.mark.parametrize("datatype", ["bigint", "dec(5, 2)", "nchar(10)"])
def test_postgres_datatype_segment_preserves_builtin(
    datatype: str,
    caplog: LogCaptureFixture,
    dialect_specific_segment_parses: Callable,
) -> None:
    """Keep builtin types outside the restricted generic identifier branch."""
    dialect_specific_segment_parses("postgres", "DatatypeSegment", datatype, caplog)


@pytest.mark.parametrize(
    "segment_reference,raw",
    [
        # AT TIME ZONE constructs
        ("SelectClauseElementSegment", "c_column AT TIME ZONE 'UTC'"),
        ("SelectClauseElementSegment", "(c_column AT TIME ZONE 'UTC')::time"),
        (
            "SelectClauseElementSegment",
            "timestamp with time zone '2021-10-01' AT TIME ZONE 'UTC'",
        ),
        # Notnull and Isnull
        ("ExpressionSegment", "c is null"),
        ("ExpressionSegment", "c is not null"),
        ("ExpressionSegment", "c isnull"),
        ("ExpressionSegment", "c notnull"),
        ("SelectClauseElementSegment", "c is null as c_isnull"),
        ("SelectClauseElementSegment", "c is not null as c_notnull"),
        ("SelectClauseElementSegment", "c isnull as c_isnull"),
        ("SelectClauseElementSegment", "c notnull as c_notnull"),
        ("ArrayAccessorSegment", "[2:10]"),
        ("ArrayAccessorSegment", "[:10]"),
        ("ArrayAccessorSegment", "[2:]"),
        ("ArrayAccessorSegment", "[2]"),
    ],
)
def test_dialect_postgres_specific_segment_parses(
    segment_reference: str,
    raw: str,
    caplog: LogCaptureFixture,
    dialect_specific_segment_parses: Callable,
) -> None:
    """Test that specific segments parse as expected.

    NB: We're testing the PARSE function not the MATCH function
    although this will be a recursive parse and so the match
    function of SUBSECTIONS will be tested if present. The match
    function of the parent will not be tested.
    """
    dialect_specific_segment_parses("postgres", segment_reference, raw, caplog)


@pytest.mark.parametrize(
    "raw",
    [
        "SELECT t1.field, EXTRACT(EPOCH FROM t1.sometime) AS myepoch FROM t1",
        "SELECT t1.field, EXTRACT(EPOCH FROM t1.sometime - t1.othertime) AS myepoch "
        "FROM t1",
    ],
)
def test_epoch_datetime_unit(raw: str) -> None:
    """Test the EPOCH keyword for postgres dialect."""
    # Don't test for new lines or capitalisation
    cfg = FluffConfig(
        configs={"core": {"exclude_rules": "LT12,LT05,LT09", "dialect": "postgres"}}
    )
    lnt = Linter(config=cfg)
    result = lnt.lint_string(raw)
    assert result.num_violations() == 0


@pytest.mark.parametrize(
    "raw",
    [
        "SELECT foo AS space FROM t1",
        "SELECT space.something FROM t1 AS space",
    ],
)
def test_space_is_not_reserved(raw: str) -> None:
    """Ensure that SPACE is not treated as reserved."""
    cfg = FluffConfig(
        configs={"core": {"exclude_rules": "LT12,LT05,AL07", "dialect": "postgres"}}
    )
    lnt = Linter(config=cfg)
    result = lnt.lint_string(raw)
    assert result.num_violations() == 0


def test_priority_keyword_merge() -> None:
    """Test merging on keyword lists works as expected."""
    kw_list_1 = [("A", "not-keyword"), ("B", "non-reserved")]

    kw_list_2 = [("A", "reserved"), ("C", "non-reserved")]

    result = priority_keyword_merge(kw_list_1, kw_list_2)

    expected_result = [("A", "reserved"), ("B", "non-reserved"), ("C", "non-reserved")]

    assert sorted(result) == sorted(expected_result)

    kw_list_1 = [("A", "not-keyword"), ("B", "non-reserved")]

    kw_list_2 = [("A", "reserved"), ("C", "non-reserved")]

    result_2 = priority_keyword_merge(kw_list_2, kw_list_1)

    expected_result_2 = [
        ("A", "not-keyword"),
        ("B", "non-reserved"),
        ("C", "non-reserved"),
    ]

    assert sorted(result_2) == sorted(expected_result_2)

    kw_list_1 = [("A", "not-keyword"), ("B", "non-reserved")]

    kw_list_2 = [("A", "reserved"), ("C", "non-reserved")]

    kw_list_3 = [("B", "reserved")]

    result_3 = priority_keyword_merge(kw_list_2, kw_list_1, kw_list_3)

    expected_result_3 = [("A", "not-keyword"), ("B", "reserved"), ("C", "non-reserved")]

    assert sorted(result_3) == sorted(expected_result_3)

    kw_list_1 = [("A", "not-keyword"), ("B", "non-reserved")]

    result_4 = priority_keyword_merge(kw_list_1)

    expected_result_4 = kw_list_1

    assert sorted(result_4) == sorted(expected_result_4)


def test_get_keywords() -> None:
    """Test keyword filtering works as expected."""
    kw_list = [
        ("A", "not-keyword"),
        ("B", "reserved"),
        ("C", "non-reserved"),
        ("D", "not-keyword"),
        ("E", "non-reserved-(cannot-be-function-or-type)"),
    ]

    expected_result = ["A", "D"]

    assert sorted(get_keywords(kw_list, "not-keyword")) == sorted(expected_result)

    expected_result_2 = ["C", "E"]

    assert sorted(get_keywords(kw_list, "non-reserved")) == sorted(expected_result_2)

    expected_result_3 = ["B"]

    assert sorted(get_keywords(kw_list, "reserved")) == sorted(expected_result_3)
