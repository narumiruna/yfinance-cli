from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from yfinance_cli.cli import create_app
from yfinance_cli.errors import CliError

runner = CliRunner()


class FakeService:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def get_info(self, ticker: str) -> dict:
        self.calls.append(("get_info", ticker))
        return {
            "ticker": ticker,
            "company": {
                "name": "Apple Inc.",
                "short_name": "Apple",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "website": "https://apple.com",
                "country": "United States",
                "employees": 100000,
                "summary": "Makes devices.",
            },
            "market": {
                "exchange": "NASDAQ",
                "currency": "USD",
                "quote_type": "EQUITY",
                "timezone": "EDT",
            },
            "price": {
                "current": 189.55,
                "previous_close": 188.2,
                "open": 188.4,
                "day_high": 190.1,
                "day_low": 187.9,
                "fifty_two_week_high": 199.2,
                "fifty_two_week_low": 160.4,
                "volume": 1000000,
                "average_volume": 900000,
            },
            "metrics": {
                "market_cap": 3000000000,
                "trailing_pe": 27.1,
                "forward_pe": 25.3,
                "dividend_yield": 0.005,
                "beta": 1.2,
            },
        }

    def get_history(self, ticker: str, period: str, interval: str) -> dict:
        self.calls.append(("get_history", ticker, period, interval))
        return {
            "ticker": ticker,
            "period": period,
            "interval": interval,
            "summary": {
                "row_count": 3,
                "start": "2026-01-01T00:00:00",
                "end": "2026-01-03T00:00:00",
                "first_close": 180.0,
                "last_close": 189.0,
                "change": 9.0,
                "change_percent": 5.0,
                "high": 191.0,
                "low": 179.0,
                "volume_total": 600000,
            },
            "rows": [
                {
                    "timestamp": "2026-01-01T00:00:00",
                    "open": 180.0,
                    "high": 182.0,
                    "low": 179.0,
                    "close": 180.0,
                    "adj_close": 180.0,
                    "volume": 100000,
                },
                {
                    "timestamp": "2026-01-02T00:00:00",
                    "open": 181.0,
                    "high": 185.0,
                    "low": 180.0,
                    "close": 184.0,
                    "adj_close": 184.0,
                    "volume": 200000,
                },
                {
                    "timestamp": "2026-01-03T00:00:00",
                    "open": 184.0,
                    "high": 191.0,
                    "low": 183.0,
                    "close": 189.0,
                    "adj_close": 189.0,
                    "volume": 300000,
                },
            ],
        }

    def export_history_chart(
        self,
        ticker: str,
        period: str,
        interval: str,
        chart_type: str,
        output_path: Path,
    ) -> dict:
        self.calls.append(("export_history_chart", ticker, period, interval, chart_type, str(output_path)))
        return {
            "ticker": ticker,
            "period": period,
            "interval": interval,
            "chart": chart_type,
            "output": str(output_path),
            "row_count": 3,
        }

    def search(self, query: str, search_type: str, limit: int | None) -> dict:
        self.calls.append(("search", query, search_type, limit))
        return {
            "query": query,
            "type": search_type,
            "counts": {"quotes": 1},
            "results": {
                "quotes": [
                    {
                        "symbol": "NVDA",
                        "name": "NVIDIA Corporation",
                        "exchange": "NASDAQ",
                        "type": "EQUITY",
                        "score": 1.0,
                    }
                ]
            },
        }

    def get_news(self, ticker: str, limit: int | None) -> dict:
        self.calls.append(("get_news", ticker, limit))
        return {
            "ticker": ticker,
            "count": 1,
            "total_count": 2,
            "articles": [
                {
                    "title": "Apple launches something",
                    "publisher": "Example News",
                    "published_at": "2026-01-01T00:00:00",
                    "link": "https://example.com/story",
                    "related_tickers": ["AAPL"],
                }
            ],
        }

    def get_financials(self, ticker: str, frequency: str) -> dict:
        self.calls.append(("get_financials", ticker, frequency))
        return {
            "ticker": ticker,
            "frequency": frequency,
            "notes": [],
            "statements": {
                "income_statement": {
                    "columns": ["2025-12-31"],
                    "rows": [{"metric": "Total Revenue", "values": [1000]}],
                },
                "balance_sheet": None,
                "cash_flow": {
                    "columns": ["2025-12-31"],
                    "rows": [{"metric": "Free Cash Flow", "values": [500]}],
                },
            },
        }

    def get_options_dates(self, ticker: str) -> dict:
        self.calls.append(("get_options_dates", ticker))
        return {"ticker": ticker, "count": 2, "dates": ["2026-06-19", "2026-09-18"]}

    def get_options_chain(
        self,
        ticker: str,
        expiration_date: str,
        option_type: str,
        limit: int | None,
    ) -> dict:
        self.calls.append(("get_options_chain", ticker, expiration_date, option_type, limit))
        return {
            "ticker": ticker,
            "expiration_date": expiration_date,
            "option_type": option_type,
            "counts": {"calls": 2, "puts": 2},
            "displayed": {"calls": 2, "puts": 0 if option_type == "calls" else 2},
            "underlying": {"symbol": ticker, "price": 189.5, "change": 1.2, "change_percent": 0.6, "currency": "USD"},
            "calls": [
                {
                    "contract_symbol": "AAPL260619C00190000",
                    "last_trade_date": "2026-05-01T00:00:00",
                    "strike": 190.0,
                    "last_price": 4.0,
                    "bid": 3.9,
                    "ask": 4.1,
                    "change": 0.2,
                    "percent_change": 0.05,
                    "volume": 100,
                    "open_interest": 200,
                    "implied_volatility": 0.24,
                    "in_the_money": False,
                    "currency": "USD",
                }
            ],
            "puts": []
            if option_type == "calls"
            else [
                {
                    "contract_symbol": "AAPL260619P00190000",
                    "last_trade_date": "2026-05-01T00:00:00",
                    "strike": 190.0,
                    "last_price": 3.5,
                    "bid": 3.4,
                    "ask": 3.6,
                    "change": -0.1,
                    "percent_change": -0.02,
                    "volume": 80,
                    "open_interest": 150,
                    "implied_volatility": 0.22,
                    "in_the_money": True,
                    "currency": "USD",
                }
            ],
        }

    def get_top(self, category: str, sector_slug: str, limit: int | None) -> dict:
        self.calls.append(("get_top", category, sector_slug, limit))
        return {
            "category": category,
            "sector": {"key": sector_slug, "name": "Technology"},
            "count": 1,
            "total_count": 3,
            "results": [{"symbol": "MSFT", "name": "Microsoft", "rating": "A", "market_weight": 0.2}],
        }


def create_test_app(fake_service: FakeService):
    return create_app(service_factory=lambda: fake_service)


def test_info_command_renders_summary() -> None:
    fake_service = FakeService()
    result = runner.invoke(create_test_app(fake_service), ["info", "AAPL"])

    assert result.exit_code == 0
    assert "Info summary" in result.stdout
    assert "Apple Inc." in result.stdout
    assert fake_service.calls == [("get_info", "AAPL")]


def test_info_command_json_output_uses_stable_schema() -> None:
    fake_service = FakeService()
    result = runner.invoke(create_test_app(fake_service), ["info", "AAPL", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ticker"] == "AAPL"
    assert payload["company"]["name"] == "Apple Inc."


def test_search_defaults_to_quotes_and_default_limit() -> None:
    fake_service = FakeService()
    result = runner.invoke(create_test_app(fake_service), ["search", "nvidia", "--json"])

    assert result.exit_code == 0
    assert fake_service.calls == [("search", "nvidia", "quotes", 10)]


def test_history_chart_and_json_are_mutually_exclusive() -> None:
    fake_service = FakeService()
    result = runner.invoke(
        create_test_app(fake_service),
        ["history", "AAPL", "--chart", "price", "--output", "chart.png", "--json"],
    )

    assert result.exit_code == 1
    assert "cannot be used together" in result.stdout
    assert fake_service.calls == []


def test_history_chart_export_uses_export_service_method() -> None:
    fake_service = FakeService()
    result = runner.invoke(
        create_test_app(fake_service),
        ["history", "AAPL", "--chart", "price-volume", "--output", "chart.webp"],
    )

    assert result.exit_code == 0
    assert "Chart exported" in result.stdout
    assert fake_service.calls == [("export_history_chart", "AAPL", "1mo", "1d", "price-volume", "chart.webp")]


def test_news_all_passes_none_limit() -> None:
    fake_service = FakeService()
    result = runner.invoke(create_test_app(fake_service), ["news", "AAPL", "--all"])

    assert result.exit_code == 0
    assert fake_service.calls == [("get_news", "AAPL", None)]


def test_financials_verbose_renders_sections() -> None:
    fake_service = FakeService()
    result = runner.invoke(create_test_app(fake_service), ["financials", "AAPL", "-v"])

    assert result.exit_code == 0
    assert "Income statement" in result.stdout
    assert "Cash flow" in result.stdout


def test_options_dates_renders_available_expirations() -> None:
    fake_service = FakeService()
    result = runner.invoke(create_test_app(fake_service), ["options", "dates", "AAPL"])

    assert result.exit_code == 0
    assert "2026-06-19" in result.stdout
    assert fake_service.calls == [("get_options_dates", "AAPL")]


def test_options_chain_defaults_to_all_with_default_limit() -> None:
    fake_service = FakeService()
    result = runner.invoke(
        create_test_app(fake_service),
        ["options", "chain", "AAPL", "--date", "2026-06-19", "--json"],
    )

    assert result.exit_code == 0
    assert fake_service.calls == [("get_options_chain", "AAPL", "2026-06-19", "all", 10)]


def test_options_chain_all_passes_none_limit() -> None:
    fake_service = FakeService()
    result = runner.invoke(
        create_test_app(fake_service),
        ["options", "chain", "AAPL", "--date", "2026-06-19", "--all", "--type", "calls"],
    )

    assert result.exit_code == 0
    assert fake_service.calls == [("get_options_chain", "AAPL", "2026-06-19", "calls", None)]


def test_top_command_rejects_unknown_sector_before_service_call() -> None:
    fake_service = FakeService()
    result = runner.invoke(create_test_app(fake_service), ["top", "companies", "unknown-sector"])

    assert result.exit_code == 1
    assert "Unknown sector" in result.stdout
    assert fake_service.calls == []


def test_json_error_output_uses_structured_error_schema() -> None:
    class ErrorService(FakeService):
        def get_info(self, ticker: str) -> dict:
            raise CliError("INVALID_SYMBOL", "Ticker was not found.", hint="Try yf search BAD.")

    result = runner.invoke(create_test_app(ErrorService()), ["info", "BAD", "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload == {
        "error": "Ticker was not found.",
        "error_code": "INVALID_SYMBOL",
        "hint": "Try yf search BAD.",
    }
