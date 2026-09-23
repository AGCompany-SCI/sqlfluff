"""Tests the python routines within LT12 and CV06."""

from sqlfluff.core import FluffConfig, Linter


def test__rules__std_LT12_and_CV06_interaction() -> None:
    """Test interaction between LT12 and CV06 doesn't stop CV06 from being applied."""
    # Test sql with no final newline and no final semicolon.
    sql = "SELECT foo FROM bar"

    # Ensure final semicolon requirement is active.
    cfg = FluffConfig(overrides={"dialect": "ansi"})
    cfg.set_value(
        config_path=["rules", "convention.terminator", "require_final_semicolon"],
        val=True,
    )
    linter = Linter(config=cfg)

    # Return linted/fixed file.
    linted_file = linter.lint_string(sql, fix=True)

    # Check expected lint errors are raised.
    assert set([v.rule.code for v in linted_file.violations]) == {"LT12", "CV06"}

    # Check file is fixed.
    assert linted_file.fix_string()[0] == "SELECT foo FROM bar;\n"


def test__rules__CV06_oracle_batch_missing_semicolon_positions() -> None:
    """Report missing Oracle batch terminators at the end of each statement."""
    sql = (
        "DELETE FROM t WHERE a = 1;\n"
        "--\n"
        "DELETE FROM t WHERE a = 2\n"
        "-- Next batch\n"
        "INSERT INTO t(a) VALUES(1);\n"
        "--\n"
        "INSERT INTO t(a) VALUES(2)\n"
    )
    cfg = FluffConfig(overrides={"dialect": "oracle", "rules": "CV06"})
    cfg.set_value(
        config_path=["rules", "convention.terminator", "require_final_semicolon"],
        val=True,
    )

    violations = Linter(config=cfg).lint_string(sql).violations

    assert [(v.rule_code(), v.line_no) for v in violations] == [
        ("CV06", 3),
        ("CV06", 7),
    ]


def test__rules__CV06_oracle_keeps_trailing_noqa_on_statement() -> None:
    """A new semicolon line should not move an inline noqa comment."""
    sql = "SELECT\n  1+2 -- noqa: LT01\n"
    cfg = FluffConfig(overrides={"dialect": "oracle", "rules": "CV06,LT01"})
    cfg.set_value(
        config_path=["rules", "convention.terminator", "require_final_semicolon"],
        val=True,
    )
    cfg.set_value(
        config_path=["rules", "convention.terminator", "multiline_newline"],
        val=True,
    )
    linter = Linter(config=cfg)

    fixed = linter.lint_string(sql, fix=True).fix_string()[0]

    assert fixed == "SELECT\n  1+2 -- noqa: LT01\n;\n"
    assert not linter.lint_string(fixed).violations
