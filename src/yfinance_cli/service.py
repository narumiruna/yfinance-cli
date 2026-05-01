from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from collections.abc import Sequence
from datetime import date
from datetime import datetime
from pathlib import Path
from typing import Protocol
from typing import cast

import pandas as pd
import yfinance as yf

from yfinance_cli.charts import export_history_chart
from yfinance_cli.errors import CliError

type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonDict = dict[str, JsonValue]
type MappingLike = Mapping[str, object]
type Scalar = None | bool | int | float | str


class FinanceService(Protocol):
    def get_info(self, ticker: str) -> JsonDict: ...

    def get_history(self, ticker: str, period: str, interval: str) -> JsonDict: ...

    def export_history_chart(
        self,
        ticker: str,
        period: str,
        interval: str,
        chart_type: str,
        output_path: Path,
    ) -> JsonDict: ...

    def search(self, query: str, search_type: str, limit: int | None) -> JsonDict: ...

    def get_news(self, ticker: str, limit: int | None) -> JsonDict: ...

    def get_financials(self, ticker: str, frequency: str) -> JsonDict: ...

    def get_options_dates(self, ticker: str) -> JsonDict: ...

    def get_options_chain(
        self,
        ticker: str,
        expiration_date: str,
        option_type: str,
        limit: int | None,
    ) -> JsonDict: ...

    def get_top(self, category: str, sector_slug: str, limit: int | None) -> JsonDict: ...


class YFinanceService:
    def _run(self, operation: str, func: Callable[[], JsonDict]) -> JsonDict:
        try:
            return func()
        except CliError:
            raise
        except Exception as exc:
            raise CliError(
                "NETWORK_ERROR",
                f"Failed to fetch {operation} from Yahoo Finance.",
                hint=str(exc),
            ) from exc

    def get_info(self, ticker: str) -> JsonDict:
        return self._run(f"info for '{ticker}'", lambda: self._get_info(ticker))

    def get_history(self, ticker: str, period: str, interval: str) -> JsonDict:
        return self._run(
            f"history for '{ticker}'",
            lambda: self._get_history(ticker=ticker, period=period, interval=interval),
        )

    def export_history_chart(
        self,
        ticker: str,
        period: str,
        interval: str,
        chart_type: str,
        output_path: Path,
    ) -> JsonDict:
        return self._run(
            f"history chart for '{ticker}'",
            lambda: self._export_history_chart(
                ticker=ticker,
                period=period,
                interval=interval,
                chart_type=chart_type,
                output_path=output_path,
            ),
        )

    def search(self, query: str, search_type: str, limit: int | None) -> JsonDict:
        return self._run(
            f"search results for '{query}'",
            lambda: self._search(query=query, search_type=search_type, limit=limit),
        )

    def get_news(self, ticker: str, limit: int | None) -> JsonDict:
        return self._run(
            f"news for '{ticker}'",
            lambda: self._get_news(ticker=ticker, limit=limit),
        )

    def get_financials(self, ticker: str, frequency: str) -> JsonDict:
        return self._run(
            f"financials for '{ticker}'",
            lambda: self._get_financials(ticker=ticker, frequency=frequency),
        )

    def get_options_dates(self, ticker: str) -> JsonDict:
        return self._run(
            f"option dates for '{ticker}'",
            lambda: self._get_options_dates(ticker=ticker),
        )

    def get_options_chain(
        self,
        ticker: str,
        expiration_date: str,
        option_type: str,
        limit: int | None,
    ) -> JsonDict:
        return self._run(
            f"option chain for '{ticker}'",
            lambda: self._get_options_chain(
                ticker=ticker,
                expiration_date=expiration_date,
                option_type=option_type,
                limit=limit,
            ),
        )

    def get_top(self, category: str, sector_slug: str, limit: int | None) -> JsonDict:
        return self._run(
            f"top {category} for '{sector_slug}'",
            lambda: self._get_top(category=category, sector_slug=sector_slug, limit=limit),
        )

    def _get_info(self, ticker: str) -> JsonDict:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info or {}
        fast_info = _as_mapping(ticker_obj.fast_info)

        current_price = _coalesce(
            fast_info.get("lastPrice"),
            info.get("currentPrice"),
            info.get("regularMarketPrice"),
        )

        if current_price is None and not info:
            raise CliError(
                "NO_DATA",
                f"No data is available for '{ticker}'.",
                hint=f"Check the ticker symbol and try 'yf search {ticker}'.",
            )

        payload = {
            "ticker": ticker,
            "company": {
                "name": _coalesce(info.get("longName"), info.get("shortName"), ticker),
                "short_name": info.get("shortName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "website": info.get("website"),
                "country": info.get("country"),
                "employees": info.get("fullTimeEmployees"),
                "summary": info.get("longBusinessSummary"),
            },
            "market": {
                "exchange": _coalesce(info.get("exchange"), info.get("fullExchangeName")),
                "currency": _coalesce(fast_info.get("currency"), info.get("currency")),
                "quote_type": info.get("quoteType"),
                "timezone": info.get("timeZoneShortName"),
            },
            "price": {
                "current": current_price,
                "previous_close": _coalesce(fast_info.get("previousClose"), info.get("previousClose")),
                "open": _coalesce(fast_info.get("open"), info.get("open")),
                "day_high": _coalesce(fast_info.get("dayHigh"), info.get("dayHigh")),
                "day_low": _coalesce(fast_info.get("dayLow"), info.get("dayLow")),
                "fifty_two_week_high": _coalesce(
                    fast_info.get("yearHigh"),
                    info.get("fiftyTwoWeekHigh"),
                ),
                "fifty_two_week_low": _coalesce(
                    fast_info.get("yearLow"),
                    info.get("fiftyTwoWeekLow"),
                ),
                "volume": _coalesce(fast_info.get("lastVolume"), info.get("volume")),
                "average_volume": _coalesce(
                    fast_info.get("tenDayAverageVolume"),
                    info.get("averageVolume"),
                ),
            },
            "metrics": {
                "market_cap": _coalesce(fast_info.get("marketCap"), info.get("marketCap")),
                "trailing_pe": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "dividend_yield": info.get("dividendYield"),
                "beta": info.get("beta"),
            },
        }
        return _normalize_dict(payload)

    def _get_history(self, *, ticker: str, period: str, interval: str) -> JsonDict:
        history = self._fetch_history_frame(ticker=ticker, period=period, interval=interval)
        rows = [_history_row_from_series(index, row) for index, row in history.iterrows()]

        first_close = _number(rows[0].get("close"))
        last_close = _number(rows[-1].get("close"))
        change = None
        change_percent = None
        if first_close not in (None, 0) and last_close is not None:
            change = last_close - first_close
            change_percent = (change / first_close) * 100

        summary = {
            "row_count": len(rows),
            "start": rows[0]["timestamp"],
            "end": rows[-1]["timestamp"],
            "first_close": first_close,
            "last_close": last_close,
            "change": change,
            "change_percent": change_percent,
            "high": history["High"].max(),
            "low": history["Low"].min(),
            "volume_total": history["Volume"].fillna(0).sum(),
        }
        return _normalize_dict(
            {
                "ticker": ticker,
                "period": period,
                "interval": interval,
                "summary": summary,
                "rows": rows,
            }
        )

    def _export_history_chart(
        self,
        *,
        ticker: str,
        period: str,
        interval: str,
        chart_type: str,
        output_path: Path,
    ) -> JsonDict:
        history = self._fetch_history_frame(ticker=ticker, period=period, interval=interval)
        export_history_chart(
            history=history,
            ticker=ticker,
            chart_type=chart_type,
            output_path=output_path,
        )
        return _normalize_dict(
            {
                "ticker": ticker,
                "period": period,
                "interval": interval,
                "chart": chart_type,
                "output": str(output_path),
                "row_count": len(history),
            }
        )

    def _search(self, *, query: str, search_type: str, limit: int | None) -> JsonDict:
        search_limit = 250 if limit is None else limit
        search = yf.Search(query, max_results=search_limit, news_count=search_limit)
        quotes = [_shape_search_quote(quote) for quote in search.quotes]
        news = [_shape_article(article) for article in search.news]

        if search_type == "quotes":
            selected_quotes = quotes[:search_limit]
            if not selected_quotes:
                raise CliError("NO_DATA", f"No quote matches were found for '{query}'.")
            return _normalize_dict(
                {
                    "query": query,
                    "type": search_type,
                    "counts": {"quotes": len(selected_quotes)},
                    "results": {"quotes": selected_quotes},
                }
            )

        if search_type == "news":
            selected_news = news[:search_limit]
            if not selected_news:
                raise CliError("NO_DATA", f"No news results were found for '{query}'.")
            return _normalize_dict(
                {
                    "query": query,
                    "type": search_type,
                    "counts": {"news": len(selected_news)},
                    "results": {"news": selected_news},
                }
            )

        selected_quotes = quotes[:search_limit]
        selected_news = news[:search_limit]
        if not selected_quotes and not selected_news:
            raise CliError("NO_DATA", f"No results were found for '{query}'.")

        return _normalize_dict(
            {
                "query": query,
                "type": search_type,
                "counts": {"quotes": len(selected_quotes), "news": len(selected_news)},
                "results": {"quotes": selected_quotes, "news": selected_news},
            }
        )

    def _get_news(self, *, ticker: str, limit: int | None) -> JsonDict:
        ticker_obj = yf.Ticker(ticker)
        articles = [_shape_article(article) for article in ticker_obj.news]
        if not articles:
            raise CliError("NO_DATA", f"No news is available for '{ticker}'.")
        selected = articles if limit is None else articles[:limit]
        return _normalize_dict(
            {
                "ticker": ticker,
                "count": len(selected),
                "total_count": len(articles),
                "articles": selected,
            }
        )

    def _get_financials(self, *, ticker: str, frequency: str) -> JsonDict:
        ticker_obj = yf.Ticker(ticker)
        frequency_map = {"annual": "yearly", "quarterly": "quarterly", "ttm": "trailing"}
        raw_frequency = frequency_map[frequency]
        notes: list[str] = []

        income_statement = _shape_statement(
            ticker_obj.get_income_stmt(pretty=True, freq=raw_frequency),
        )
        cash_flow = _shape_statement(
            ticker_obj.get_cash_flow(pretty=True, freq=raw_frequency),
        )

        balance_sheet: JsonDict | None
        if frequency == "ttm":
            balance_sheet = None
            notes.append("Balance sheet is not available for the ttm frequency.")
        else:
            balance_sheet = _shape_statement(
                ticker_obj.get_balance_sheet(pretty=True, freq=raw_frequency),
            )

        if income_statement is None and cash_flow is None and balance_sheet is None:
            raise CliError("NO_DATA", f"No financial statements are available for '{ticker}'.")

        return _normalize_dict(
            {
                "ticker": ticker,
                "frequency": frequency,
                "notes": notes,
                "statements": {
                    "income_statement": income_statement,
                    "balance_sheet": balance_sheet,
                    "cash_flow": cash_flow,
                },
            }
        )

    def _get_options_dates(self, *, ticker: str) -> JsonDict:
        ticker_obj = yf.Ticker(ticker)
        dates = list(ticker_obj.options)
        if not dates:
            raise CliError("NO_DATA", f"No option expiration dates are available for '{ticker}'.")
        return {"ticker": ticker, "count": len(dates), "dates": dates}

    def _get_options_chain(
        self,
        *,
        ticker: str,
        expiration_date: str,
        option_type: str,
        limit: int | None,
    ) -> JsonDict:
        ticker_obj = yf.Ticker(ticker)
        available_dates = list(ticker_obj.options)
        if expiration_date not in available_dates:
            raise CliError(
                "INVALID_PARAMS",
                f"Expiration date '{expiration_date}' is not available for '{ticker}'.",
                hint=f"Run 'yf options dates {ticker}' first. Available dates: {', '.join(available_dates)}",
            )

        chain = ticker_obj.option_chain(expiration_date)
        calls = _shape_option_contracts(chain.calls)
        puts = _shape_option_contracts(chain.puts)

        selected_calls = calls if option_type in ("all", "calls") else []
        selected_puts = puts if option_type in ("all", "puts") else []
        if limit is not None:
            selected_calls = selected_calls[:limit]
            selected_puts = selected_puts[:limit]

        if not calls and not puts:
            raise CliError("NO_DATA", f"No option chain data is available for '{ticker}' on {expiration_date}.")

        underlying = _as_mapping(chain.underlying)
        return _normalize_dict(
            {
                "ticker": ticker,
                "expiration_date": expiration_date,
                "option_type": option_type,
                "counts": {"calls": len(calls), "puts": len(puts)},
                "displayed": {"calls": len(selected_calls), "puts": len(selected_puts)},
                "underlying": {
                    "symbol": underlying.get("symbol"),
                    "price": underlying.get("regularMarketPrice"),
                    "change": underlying.get("regularMarketChange"),
                    "change_percent": underlying.get("regularMarketChangePercent"),
                    "currency": underlying.get("currency"),
                },
                "calls": selected_calls,
                "puts": selected_puts,
            }
        )

    def _get_top(self, *, category: str, sector_slug: str, limit: int | None) -> JsonDict:
        sector = yf.Sector(sector_slug)
        sector_name = sector.name or sector_slug.replace("-", " ").title()

        if category == "companies":
            results = _shape_top_companies(sector.top_companies)
        elif category == "etfs":
            results = _shape_symbol_name_mapping(sector.top_etfs)
        elif category == "mutual-funds":
            results = _shape_symbol_name_mapping(sector.top_mutual_funds)
        elif category == "growth":
            results = self._aggregate_industry_rankings(sector=sector, mode="growth")
        else:
            results = self._aggregate_industry_rankings(sector=sector, mode="performers")

        if not results:
            raise CliError("NO_DATA", f"No {category} data is available for sector '{sector_slug}'.")

        selected = results if limit is None else results[:limit]
        return _normalize_dict(
            {
                "category": category,
                "sector": {"key": sector_slug, "name": sector_name},
                "count": len(selected),
                "total_count": len(results),
                "results": selected,
            }
        )

    def _aggregate_industry_rankings(self, *, sector: yf.Sector, mode: str) -> list[JsonDict]:
        industries = sector.industries
        if industries is None or industries.empty:
            return []

        results: list[JsonDict] = []
        for industry_key, row in industries.iterrows():
            industry = yf.Industry(str(industry_key))
            if mode == "growth":
                frame = industry.top_growth_companies
                sort_key = "growth_estimate"
            else:
                frame = industry.top_performing_companies
                sort_key = "ytd_return"

            if frame is None or frame.empty:
                continue

            for symbol, values in frame.iterrows():
                item: JsonDict = {
                    "symbol": str(symbol),
                    "name": values.get("name"),
                    "industry_key": str(industry_key),
                    "industry_name": row.get("name"),
                    "ytd_return": values.get("ytd return"),
                }
                if mode == "growth":
                    item["growth_estimate"] = values.get("growth estimate")
                else:
                    item["last_price"] = values.get("last price")
                    item["target_price"] = values.get("target price")
                results.append(_normalize_dict(item))

        reverse = True
        results.sort(
            key=lambda item: item.get(sort_key) if item.get(sort_key) is not None else float("-inf"),
            reverse=reverse,
        )
        return results

    def _fetch_history_frame(self, *, ticker: str, period: str, interval: str) -> pd.DataFrame:
        ticker_obj = yf.Ticker(ticker)
        history = ticker_obj.history(period=period, interval=interval, auto_adjust=False)
        if history.empty:
            raise CliError(
                "NO_DATA",
                f"No history data is available for '{ticker}' with period '{period}' and interval '{interval}'.",
            )
        return history


def _coalesce(*values: object) -> object | None:
    for value in values:
        if value is not None:
            return value
    return None


def _as_mapping(value: object) -> MappingLike:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return {str(key): item for key, item in value.items()}

    keys_method = getattr(value, "keys", None)
    getitem_method = getattr(value, "__getitem__", None)
    if callable(keys_method) and callable(getitem_method):
        try:
            keys = cast(Iterable[object], keys_method())
            getter = cast(Callable[[object], object], getitem_method)
            return {str(key): getter(key) for key in keys}
        except (AttributeError, KeyError, TypeError, ValueError):
            return {}
    try:
        entries = cast(Iterable[tuple[object, object]], value)
        return {str(key): item for key, item in entries}
    except (TypeError, ValueError):
        return {}


def _normalize(value: object) -> JsonValue:
    if isinstance(value, Mapping):
        return {str(key): _normalize(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_normalize(item) for item in value]
    scalar = _normalize_scalar(value)
    if scalar is not None or value is None:
        return scalar
    item_method = getattr(value, "item", None)
    if callable(item_method):
        try:
            return _normalize(item_method())
        except (TypeError, ValueError):
            return str(value)
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    return str(value)


def _normalize_dict(value: Mapping[str, object]) -> JsonDict:
    return cast(JsonDict, _normalize(value))


def _normalize_scalar(value: object) -> Scalar:
    if value is None:
        return None
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (datetime, date, pd.Timestamp)):
        return value.isoformat()
    if isinstance(value, bool | int):
        return value
    if isinstance(value, float):
        return None if pd.isna(value) else value
    if isinstance(value, str):
        return value
    return None


def _number(value: JsonValue | None) -> int | float | None:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int | float):
        return value
    return None


def _history_row_from_series(index: object, row: pd.Series) -> JsonDict:
    return {
        "timestamp": _normalize(index),
        "open": _normalize(row.get("Open")),
        "high": _normalize(row.get("High")),
        "low": _normalize(row.get("Low")),
        "close": _normalize(row.get("Close")),
        "adj_close": _normalize(row.get("Adj Close")),
        "volume": _normalize(row.get("Volume")),
    }


def _extract_article_url(article: MappingLike) -> str | None:
    for key in ("link", "url"):
        value = article.get(key)
        if isinstance(value, str):
            return value
        if isinstance(value, Mapping):
            nested = _as_mapping(value).get("url")
            if isinstance(nested, str):
                return nested
    for key in ("clickThroughUrl", "canonicalUrl"):
        value = article.get(key)
        if isinstance(value, Mapping):
            nested = _as_mapping(value).get("url")
            if isinstance(nested, str):
                return nested
    return None


def _shape_article(article: MappingLike) -> JsonDict:
    related_tickers = article.get("relatedTickers")
    return _normalize_dict(
        {
            "title": article.get("title"),
            "publisher": article.get("publisher"),
            "published_at": _normalize(
                _coalesce(
                    article.get("providerPublishTime"),
                    article.get("pubDate"),
                    article.get("publishedAt"),
                )
            ),
            "link": _extract_article_url(article),
            "related_tickers": _string_values(related_tickers),
        }
    )


def _shape_search_quote(quote: MappingLike) -> JsonDict:
    return _normalize_dict(
        {
            "symbol": quote.get("symbol"),
            "name": _coalesce(quote.get("shortname"), quote.get("longname"), quote.get("symbol")),
            "exchange": _coalesce(quote.get("exchDisp"), quote.get("exchange")),
            "type": quote.get("quoteType"),
            "score": quote.get("score"),
        }
    )


def _shape_statement(frame: object) -> JsonDict | None:
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        return None

    columns = [_normalize(column) for column in frame.columns]
    rows = []
    for metric, values in frame.iterrows():
        rows.append(
            {
                "metric": str(metric),
                "values": [_normalize(value) for value in values.tolist()],
            }
        )
    return {"columns": columns, "rows": rows}


def _shape_option_contracts(frame: pd.DataFrame | None) -> list[JsonDict]:
    if frame is None or frame.empty:
        return []
    return [
        {
            "contract_symbol": row.get("contractSymbol"),
            "last_trade_date": _normalize(row.get("lastTradeDate")),
            "strike": _normalize(row.get("strike")),
            "last_price": _normalize(row.get("lastPrice")),
            "bid": _normalize(row.get("bid")),
            "ask": _normalize(row.get("ask")),
            "change": _normalize(row.get("change")),
            "percent_change": _normalize(row.get("percentChange")),
            "volume": _normalize(row.get("volume")),
            "open_interest": _normalize(row.get("openInterest")),
            "implied_volatility": _normalize(row.get("impliedVolatility")),
            "in_the_money": _normalize(row.get("inTheMoney")),
            "currency": _normalize(row.get("currency")),
        }
        for row in frame.to_dict(orient="records")
    ]


def _shape_top_companies(frame: pd.DataFrame | None) -> list[JsonDict]:
    if frame is None or frame.empty:
        return []
    rows: list[JsonDict] = []
    for symbol, values in frame.iterrows():
        rows.append(
            {
                "symbol": str(symbol),
                "name": values.get("name"),
                "rating": values.get("rating"),
                "market_weight": values.get("market weight"),
            }
        )
    return rows


def _shape_symbol_name_mapping(mapping: Mapping[str, str] | None) -> list[JsonDict]:
    if not mapping:
        return []
    return [{"symbol": symbol, "name": name} for symbol, name in mapping.items()]


def _string_values(value: object) -> list[str]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [str(item) for item in value]
    return []
