from __future__ import annotations

from datetime import date
from pathlib import Path

from yfinance.const import SECTOR_INDUSTY_MAPPING_LC

from yfinance_cli.constants import ALLOWED_CHART_TYPES
from yfinance_cli.constants import ALLOWED_FREQUENCIES
from yfinance_cli.constants import ALLOWED_INTERVALS
from yfinance_cli.constants import ALLOWED_OPTION_TYPES
from yfinance_cli.constants import ALLOWED_PERIODS
from yfinance_cli.constants import ALLOWED_SEARCH_TYPES
from yfinance_cli.errors import CliError


def _format_choices(choices: tuple[str, ...] | list[str]) -> str:
    return ", ".join(choices)


def normalize_ticker(ticker: str) -> str:
    normalized = ticker.strip().upper()
    if normalized:
        return normalized
    raise CliError("INVALID_PARAMS", "Ticker cannot be empty.")


def normalize_query(query: str) -> str:
    normalized = query.strip()
    if normalized:
        return normalized
    raise CliError("INVALID_PARAMS", "Search query cannot be empty.")


def ensure_choice(value: str, choices: tuple[str, ...], *, label: str) -> str:
    normalized = value.strip().lower()
    if normalized in choices:
        return normalized
    raise CliError(
        "INVALID_PARAMS",
        f"Invalid {label} '{value}'.",
        hint=f"Valid values: {_format_choices(choices)}.",
    )


def normalize_period(period: str) -> str:
    return ensure_choice(period, ALLOWED_PERIODS, label="period")


def normalize_interval(interval: str) -> str:
    return ensure_choice(interval, ALLOWED_INTERVALS, label="interval")


def normalize_search_type(search_type: str) -> str:
    return ensure_choice(search_type, ALLOWED_SEARCH_TYPES, label="search type")


def normalize_frequency(frequency: str) -> str:
    return ensure_choice(frequency, ALLOWED_FREQUENCIES, label="frequency")


def normalize_option_type(option_type: str) -> str:
    return ensure_choice(option_type, ALLOWED_OPTION_TYPES, label="option type")


def normalize_chart_type(chart_type: str) -> str:
    return ensure_choice(chart_type, ALLOWED_CHART_TYPES, label="chart type")


def normalize_sector_slug(sector_slug: str) -> str:
    normalized = sector_slug.strip().lower()
    if normalized in SECTOR_INDUSTY_MAPPING_LC:
        return normalized
    valid = tuple(sorted(SECTOR_INDUSTY_MAPPING_LC))
    raise CliError(
        "INVALID_PARAMS",
        f"Unknown sector '{sector_slug}'.",
        hint=f"Try one of: {_format_choices(valid)}.",
    )


def normalize_expiration_date(expiration_date: str) -> str:
    stripped = expiration_date.strip()
    try:
        date.fromisoformat(stripped)
    except ValueError as exc:
        raise CliError(
            "INVALID_PARAMS",
            f"Invalid expiration date '{expiration_date}'.",
            hint="Use YYYY-MM-DD format.",
        ) from exc
    return stripped


def resolve_limit(limit: int, include_all: bool) -> int | None:
    if include_all:
        return None
    if limit > 0:
        return limit
    raise CliError("INVALID_PARAMS", "Limit must be greater than zero.")


def validate_history_modes(*, json_output: bool, chart: str | None, output: Path | None) -> None:
    if chart and json_output:
        raise CliError(
            "INVALID_PARAMS",
            "The --chart and --json options cannot be used together.",
        )
    if chart and output is None:
        raise CliError(
            "INVALID_PARAMS",
            "The --output option is required when exporting a chart.",
            hint="Example: yfinance-cli history AAPL --chart price-volume --output aapl.webp",
        )
    if output is not None and not chart:
        raise CliError(
            "INVALID_PARAMS",
            "The --output option can only be used together with --chart.",
        )
    if output is not None and not output.suffix:
        raise CliError(
            "INVALID_PARAMS",
            f"Output path '{output}' must include a file extension.",
            hint="Examples: report.png, history.webp",
        )
