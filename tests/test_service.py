from __future__ import annotations

from typing import cast

import pandas as pd
import pytest

from yfinance_cli.errors import CliError
from yfinance_cli.service import YFinanceService

Payload = dict[str, object]


def test_get_info_shapes_company_and_price_fields(monkeypatch) -> None:
    class FakeTicker:
        def __init__(self, ticker: str) -> None:
            self.ticker = ticker
            self.info = {
                "longName": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "exchange": "NASDAQ",
                "quoteType": "EQUITY",
                "marketCap": 3_000_000_000,
                "currentPrice": 189.55,
                "previousClose": 188.2,
                "website": "https://apple.com",
            }
            self.fast_info = {
                "currency": "USD",
                "dayHigh": 190.1,
                "dayLow": 187.9,
                "marketCap": 3_100_000_000,
            }

    monkeypatch.setattr("yfinance_cli.service.yf.Ticker", FakeTicker)

    payload = YFinanceService().get_info("AAPL")
    company = cast(Payload, payload["company"])
    price = cast(Payload, payload["price"])
    metrics = cast(Payload, payload["metrics"])

    assert payload["ticker"] == "AAPL"
    assert company["name"] == "Apple Inc."
    assert price["current"] == 189.55
    assert metrics["market_cap"] == 3_100_000_000


def test_get_top_growth_aggregates_industries(monkeypatch) -> None:
    industries = pd.DataFrame(
        [
            {
                "key": "software-infrastructure",
                "name": "Software Infrastructure",
                "symbol": "^XSWI",
                "market weight": 0.6,
            },
            {"key": "semiconductors", "name": "Semiconductors", "symbol": "^XSEM", "market weight": 0.4},
        ]
    ).set_index("key")

    class FakeSector:
        def __init__(self, key: str) -> None:
            self.key = key
            self.name = "Technology"
            self.top_companies = None
            self.top_etfs = {}
            self.top_mutual_funds = {}
            self.industries = industries

    growth_tables = {
        "software-infrastructure": pd.DataFrame(
            [{"symbol": "MSFT", "name": "Microsoft", "ytd return": 0.12, "growth estimate": 0.2}]
        ).set_index("symbol"),
        "semiconductors": pd.DataFrame(
            [{"symbol": "NVDA", "name": "NVIDIA", "ytd return": 0.25, "growth estimate": 0.45}]
        ).set_index("symbol"),
    }

    class FakeIndustry:
        def __init__(self, key: str) -> None:
            self.key = key
            self.top_growth_companies = growth_tables[key]
            self.top_performing_companies = None

    monkeypatch.setattr("yfinance_cli.service.yf.Sector", FakeSector)
    monkeypatch.setattr("yfinance_cli.service.yf.Industry", FakeIndustry)

    payload = YFinanceService().get_top("growth", "technology", None)
    sector = cast(Payload, payload["sector"])
    results = cast(list[Payload], payload["results"])

    assert sector["name"] == "Technology"
    assert results[0]["symbol"] == "NVDA"
    assert results[0]["industry_key"] == "semiconductors"


def test_get_options_chain_rejects_unknown_expiration(monkeypatch) -> None:
    class FakeTicker:
        def __init__(self, ticker: str) -> None:
            self.options = ["2026-06-19"]

        def option_chain(self, expiration_date: str):  # pragma: no cover - defensive
            raise AssertionError(f"unexpected option_chain call for {expiration_date}")

    monkeypatch.setattr("yfinance_cli.service.yf.Ticker", FakeTicker)

    with pytest.raises(CliError) as error:
        YFinanceService().get_options_chain("AAPL", "2026-07-17", "all", 10)

    assert error.value.error_code == "INVALID_PARAMS"
    assert "Run 'yfinance-cli options dates AAPL' first" in (error.value.hint or "")
