from __future__ import annotations

from typing import cast

from rich.console import Console
from rich.console import Group
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table

from yfinance_cli.constants import DEFAULT_FINANCIAL_ROWS
from yfinance_cli.constants import DEFAULT_HISTORY_ROWS
from yfinance_cli.constants import DEFAULT_OPTIONS_ROWS
from yfinance_cli.errors import CliError
from yfinance_cli.service import JsonDict

Payload = JsonDict
RowPayload = JsonDict


def emit_json(payload: Payload) -> None:
    import json

    print(json.dumps(payload, indent=2, sort_keys=True))


def render_error(console: Console, error: CliError, *, json_output: bool) -> None:
    if json_output:
        emit_json(error.to_dict())
        return

    lines = [f"[bold red]Error:[/bold red] {error.message}"]
    if error.hint:
        lines.append(f"[yellow]Hint:[/yellow] {error.hint}")
    console.print(Panel.fit("\n".join(lines), title="Request failed", border_style="red"))


def render_info(console: Console, payload: Payload, *, verbose: bool) -> None:
    company = _payload(payload["company"])
    market = _payload(payload["market"])
    price = _payload(payload["price"])
    metrics = _payload(payload["metrics"])

    summary = Table.grid(padding=(0, 2))
    summary.add_row("Ticker", str(payload["ticker"]))
    summary.add_row("Name", _display(company.get("name")))
    summary.add_row("Current", _display_number(price.get("current")))
    summary.add_row("Previous close", _display_number(price.get("previous_close")))
    summary.add_row("Market cap", _display_number(metrics.get("market_cap")))
    summary.add_row("Sector", _display(company.get("sector")))
    summary.add_row("Industry", _display(company.get("industry")))

    parts: list[RenderableType] = [Panel(summary, title="Info summary", border_style="cyan")]
    if verbose:
        details = Table(title="Additional details")
        details.add_column("Field")
        details.add_column("Value", overflow="fold")
        rows = [
            ("Exchange", _display(market.get("exchange"))),
            ("Currency", _display(market.get("currency"))),
            ("Quote type", _display(market.get("quote_type"))),
            ("52w high", _display_number(price.get("fifty_two_week_high"))),
            ("52w low", _display_number(price.get("fifty_two_week_low"))),
            ("Open", _display_number(price.get("open"))),
            ("Day high", _display_number(price.get("day_high"))),
            ("Day low", _display_number(price.get("day_low"))),
            ("Volume", _display_number(price.get("volume"))),
            ("Average volume", _display_number(price.get("average_volume"))),
            ("Trailing PE", _display_number(metrics.get("trailing_pe"))),
            ("Forward PE", _display_number(metrics.get("forward_pe"))),
            ("Dividend yield", _display_percent(metrics.get("dividend_yield"))),
            ("Beta", _display_number(metrics.get("beta"))),
            ("Website", _display(company.get("website"))),
            ("Country", _display(company.get("country"))),
            ("Employees", _display_number(company.get("employees"))),
        ]
        for field, value in rows:
            details.add_row(field, value)
        parts.append(details)
        summary_text = company.get("summary")
        if summary_text:
            parts.append(Panel(str(summary_text), title="Business summary", border_style="blue"))

    console.print(Group(*parts))


def render_history(console: Console, payload: Payload, *, verbose: bool) -> None:
    summary_data = _payload(payload["summary"])
    summary = Table.grid(padding=(0, 2))
    summary.add_row("Ticker", str(payload["ticker"]))
    summary.add_row("Period", str(payload["period"]))
    summary.add_row("Interval", str(payload["interval"]))
    summary.add_row("Rows", str(summary_data["row_count"]))
    summary.add_row("Start", _display(summary_data.get("start")))
    summary.add_row("End", _display(summary_data.get("end")))
    summary.add_row("Last close", _display_number(summary_data.get("last_close")))
    summary.add_row("Change", _display_change(summary_data.get("change"), summary_data.get("change_percent")))
    summary.add_row("High", _display_number(summary_data.get("high")))
    summary.add_row("Low", _display_number(summary_data.get("low")))
    summary.add_row("Volume total", _display_number(summary_data.get("volume_total")))

    table = Table(title="Recent history")
    table.add_column("Timestamp")
    table.add_column("Open", justify="right")
    table.add_column("High", justify="right")
    table.add_column("Low", justify="right")
    table.add_column("Close", justify="right")
    if verbose:
        table.add_column("Adj close", justify="right")
    table.add_column("Volume", justify="right")

    rows = _rows(payload["rows"])[-DEFAULT_HISTORY_ROWS:]
    for row in rows:
        values = [
            _display(row.get("timestamp")),
            _display_number(row.get("open")),
            _display_number(row.get("high")),
            _display_number(row.get("low")),
            _display_number(row.get("close")),
        ]
        if verbose:
            values.append(_display_number(row.get("adj_close")))
        values.append(_display_number(row.get("volume")))
        table.add_row(*values)

    console.print(Group(Panel(summary, title="History summary", border_style="cyan"), table))


def render_chart_export(console: Console, payload: Payload) -> None:
    summary = Table.grid(padding=(0, 2))
    summary.add_row("Ticker", str(payload["ticker"]))
    summary.add_row("Period", str(payload["period"]))
    summary.add_row("Interval", str(payload["interval"]))
    summary.add_row("Chart", str(payload["chart"]))
    summary.add_row("Output", str(payload["output"]))
    summary.add_row("Rows", str(payload["row_count"]))
    console.print(Panel(summary, title="Chart exported", border_style="green"))


def render_search(console: Console, payload: Payload, *, verbose: bool) -> None:
    panels: list[RenderableType] = []
    results = _payload(payload["results"])

    if "quotes" in results:
        table = Table(title="Quote matches")
        table.add_column("Symbol")
        table.add_column("Name")
        table.add_column("Exchange")
        table.add_column("Type")
        if verbose:
            table.add_column("Score", justify="right")
        for quote in _rows(results["quotes"]):
            row = [
                _display(quote.get("symbol")),
                _display(quote.get("name")),
                _display(quote.get("exchange")),
                _display(quote.get("type")),
            ]
            if verbose:
                row.append(_display_number(quote.get("score")))
            table.add_row(*row)
        panels.append(table)

    if "news" in results:
        table = Table(title="News matches")
        table.add_column("Published")
        table.add_column("Publisher")
        table.add_column("Title", overflow="fold")
        if verbose:
            table.add_column("Link", overflow="fold")
        for article in _rows(results["news"]):
            row = [
                _display(article.get("published_at")),
                _display(article.get("publisher")),
                _display(article.get("title")),
            ]
            if verbose:
                row.append(_display(article.get("link")))
            table.add_row(*row)
        panels.append(table)

    header = Table.grid(padding=(0, 2))
    header.add_row("Query", str(payload["query"]))
    header.add_row("Type", str(payload["type"]))
    for key, value in _payload(payload["counts"]).items():
        header.add_row(f"{key.title()} count", str(value))

    console.print(Group(Panel(header, title="Search summary", border_style="cyan"), *panels))


def render_news(console: Console, payload: Payload, *, verbose: bool) -> None:
    summary = Table.grid(padding=(0, 2))
    summary.add_row("Ticker", str(payload["ticker"]))
    summary.add_row("Displayed", str(payload["count"]))
    summary.add_row("Available", str(payload["total_count"]))

    table = Table(title="News")
    table.add_column("Published")
    table.add_column("Publisher")
    table.add_column("Title", overflow="fold")
    if verbose:
        table.add_column("Related tickers")
        table.add_column("Link", overflow="fold")
    for article in _rows(payload["articles"]):
        row = [
            _display(article.get("published_at")),
            _display(article.get("publisher")),
            _display(article.get("title")),
        ]
        if verbose:
            row.append(", ".join(_string_list(article.get("related_tickers"))) or "-")
            row.append(_display(article.get("link")))
        table.add_row(*row)

    console.print(Group(Panel(summary, title="News summary", border_style="cyan"), table))


def render_financials(console: Console, payload: Payload, *, verbose: bool) -> None:
    summary = Table.grid(padding=(0, 2))
    summary.add_row("Ticker", str(payload["ticker"]))
    summary.add_row("Frequency", str(payload["frequency"]))
    notes = _string_list(payload.get("notes"))
    if notes:
        summary.add_row("Notes", " | ".join(str(note) for note in notes))

    statements = _payload(payload["statements"])
    sections: list[RenderableType] = [Panel(summary, title="Financials summary", border_style="cyan")]
    for title, key in (
        ("Income statement", "income_statement"),
        ("Balance sheet", "balance_sheet"),
        ("Cash flow", "cash_flow"),
    ):
        statement = statements.get(key)
        if statement is None:
            continue
        sections.append(_statement_table(title, _payload(statement), verbose=verbose))

    console.print(Group(*sections))


def render_options_dates(console: Console, payload: Payload) -> None:
    summary = Table.grid(padding=(0, 2))
    summary.add_row("Ticker", str(payload["ticker"]))
    summary.add_row("Expiration dates", str(payload["count"]))
    table = Table(title="Available dates")
    table.add_column("Date")
    for expiration_date in _string_list(payload["dates"]):
        table.add_row(str(expiration_date))
    console.print(Group(Panel(summary, title="Options summary", border_style="cyan"), table))


def render_options_chain(console: Console, payload: Payload, *, verbose: bool) -> None:
    displayed = _payload(payload["displayed"])
    counts = _payload(payload["counts"])
    underlying = _payload(payload["underlying"])
    summary = Table.grid(padding=(0, 2))
    summary.add_row("Ticker", str(payload["ticker"]))
    summary.add_row("Expiration", str(payload["expiration_date"]))
    summary.add_row("Type", str(payload["option_type"]))
    summary.add_row("Calls", f"{displayed['calls']} / {counts['calls']}")
    summary.add_row("Puts", f"{displayed['puts']} / {counts['puts']}")
    summary.add_row("Underlying", _display_number(underlying.get("price")))

    parts: list[RenderableType] = [Panel(summary, title="Option chain summary", border_style="cyan")]
    calls = _rows(payload["calls"])
    puts = _rows(payload["puts"])
    if calls:
        parts.append(_options_table("Calls", calls, verbose=verbose))
    if puts:
        parts.append(_options_table("Puts", puts, verbose=verbose))
    console.print(Group(*parts))


def render_top(console: Console, payload: Payload, *, verbose: bool) -> None:
    sector = _payload(payload["sector"])
    summary = Table.grid(padding=(0, 2))
    summary.add_row("Category", str(payload["category"]))
    summary.add_row("Sector", str(sector["name"]))
    summary.add_row("Displayed", str(payload["count"]))
    summary.add_row("Available", str(payload["total_count"]))
    table = _build_top_results_table(str(payload["category"]), _rows(payload["results"]), verbose=verbose)
    console.print(Group(Panel(summary, title="Top summary", border_style="cyan"), table))


def _statement_table(title: str, statement: Payload, *, verbose: bool) -> Table:
    table = Table(title=title)
    table.add_column("Metric")
    columns = _values(statement["columns"])
    for column in columns:
        table.add_column(str(column), justify="right")

    rows = _rows(statement["rows"])
    row_limit = len(rows) if verbose else min(DEFAULT_FINANCIAL_ROWS, len(rows))
    for row in rows[:row_limit]:
        values = [_display_number(value) for value in _values(row["values"])]
        table.add_row(str(row["metric"]), *values)
    return table


def _options_table(title: str, rows: list[RowPayload], *, verbose: bool) -> Table:
    table = Table(title=title)
    table.add_column("Contract")
    table.add_column("Strike", justify="right")
    table.add_column("Last", justify="right")
    table.add_column("Bid", justify="right")
    table.add_column("Ask", justify="right")
    table.add_column("IV", justify="right")
    table.add_column("Volume", justify="right")
    table.add_column("Open interest", justify="right")
    if verbose:
        table.add_column("Last trade")
        table.add_column("ITM")

    row_limit = len(rows) if verbose else min(DEFAULT_OPTIONS_ROWS, len(rows))
    for row in rows[:row_limit]:
        values = [
            _display(row.get("contract_symbol")),
            _display_number(row.get("strike")),
            _display_number(row.get("last_price")),
            _display_number(row.get("bid")),
            _display_number(row.get("ask")),
            _display_percent(row.get("implied_volatility")),
            _display_number(row.get("volume")),
            _display_number(row.get("open_interest")),
        ]
        if verbose:
            values.append(_display(row.get("last_trade_date")))
            values.append(_display(row.get("in_the_money")))
        table.add_row(*values)
    return table


def _build_top_results_table(category: str, results: list[RowPayload], *, verbose: bool) -> Table:
    table = Table(title="Top results")
    _add_top_columns(table, category, verbose=verbose)
    for item in results:
        table.add_row(*_top_row(category, item, verbose=verbose))
    return table


def _add_top_columns(table: Table, category: str, *, verbose: bool) -> None:
    table.add_column("Symbol")
    table.add_column("Name")
    if category == "companies":
        table.add_column("Rating")
        table.add_column("Market weight", justify="right")
        return
    if category == "growth":
        if verbose:
            table.add_column("Industry")
        table.add_column("YTD return", justify="right")
        table.add_column("Growth estimate", justify="right")
        return
    if category == "performers":
        if verbose:
            table.add_column("Industry")
        table.add_column("YTD return", justify="right")
        table.add_column("Last price", justify="right")
        table.add_column("Target price", justify="right")


def _top_row(category: str, item: RowPayload, *, verbose: bool) -> list[str]:
    if category == "companies":
        return [
            _display(item.get("symbol")),
            _display(item.get("name")),
            _display(item.get("rating")),
            _display_number(item.get("market_weight")),
        ]

    if category == "growth":
        row = [_display(item.get("symbol")), _display(item.get("name"))]
        if verbose:
            row.append(_display(item.get("industry_name")))
        row.extend(
            [
                _display_percent(item.get("ytd_return")),
                _display_percent(item.get("growth_estimate")),
            ]
        )
        return row

    if category == "performers":
        row = [_display(item.get("symbol")), _display(item.get("name"))]
        if verbose:
            row.append(_display(item.get("industry_name")))
        row.extend(
            [
                _display_percent(item.get("ytd_return")),
                _display_number(item.get("last_price")),
                _display_number(item.get("target_price")),
            ]
        )
        return row

    return [_display(item.get("symbol")), _display(item.get("name"))]


def _display(value: object) -> str:
    if value in (None, ""):
        return "-"
    return str(value)


def _display_number(value: object) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        if abs(value) >= 1000:
            return f"{value:,.2f}"
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)


def _display_percent(value: object) -> str:
    if value is None:
        return "-"
    if isinstance(value, (int, float)):
        return f"{value * 100:.2f}%"
    return str(value)


def _display_change(change: object, change_percent: object) -> str:
    if change is None:
        return "-"
    left = _display_number(change)
    ratio = change_percent / 100 if isinstance(change_percent, (int, float)) else None
    right = _display_percent(ratio)
    return f"{left} ({right})"


def _payload(value: object) -> Payload:
    return cast(Payload, value)


def _rows(value: object) -> list[RowPayload]:
    return cast(list[RowPayload], value)


def _values(value: object) -> list[object]:
    return cast(list[object], value)


def _string_list(value: object) -> list[str]:
    return cast(list[str], value or [])
