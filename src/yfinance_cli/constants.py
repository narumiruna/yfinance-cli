from __future__ import annotations

DEFAULT_LIMIT = 10
DEFAULT_HISTORY_ROWS = 8
DEFAULT_FINANCIAL_ROWS = 8
DEFAULT_OPTIONS_ROWS = 10

ALLOWED_PERIODS = (
    "1d",
    "5d",
    "1mo",
    "3mo",
    "6mo",
    "1y",
    "2y",
    "5y",
    "10y",
    "ytd",
    "max",
)

ALLOWED_INTERVALS = (
    "1m",
    "2m",
    "5m",
    "15m",
    "30m",
    "60m",
    "90m",
    "1h",
    "1d",
    "5d",
    "1wk",
    "1mo",
    "3mo",
)

ALLOWED_SEARCH_TYPES = ("quotes", "news", "all")
ALLOWED_FREQUENCIES = ("annual", "quarterly", "ttm")
ALLOWED_OPTION_TYPES = ("all", "calls", "puts")
ALLOWED_CHART_TYPES = ("price", "price-volume")
ALLOWED_TOP_CATEGORIES = ("companies", "etfs", "mutual-funds", "growth", "performers")
