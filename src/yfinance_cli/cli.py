from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from yfinance_cli.constants import DEFAULT_LIMIT
from yfinance_cli.errors import CliError
from yfinance_cli.renderers import emit_json
from yfinance_cli.renderers import render_chart_export
from yfinance_cli.renderers import render_error
from yfinance_cli.renderers import render_financials
from yfinance_cli.renderers import render_history
from yfinance_cli.renderers import render_info
from yfinance_cli.renderers import render_news
from yfinance_cli.renderers import render_options_chain
from yfinance_cli.renderers import render_options_dates
from yfinance_cli.renderers import render_search
from yfinance_cli.renderers import render_top
from yfinance_cli.service import FinanceService
from yfinance_cli.service import JsonDict
from yfinance_cli.service import YFinanceService
from yfinance_cli.validation import normalize_chart_type
from yfinance_cli.validation import normalize_expiration_date
from yfinance_cli.validation import normalize_frequency
from yfinance_cli.validation import normalize_interval
from yfinance_cli.validation import normalize_option_type
from yfinance_cli.validation import normalize_period
from yfinance_cli.validation import normalize_query
from yfinance_cli.validation import normalize_search_type
from yfinance_cli.validation import normalize_sector_slug
from yfinance_cli.validation import normalize_ticker
from yfinance_cli.validation import resolve_limit
from yfinance_cli.validation import validate_history_modes

TickerArg = Annotated[str, typer.Argument(help="Ticker symbol, for example AAPL or MSFT.")]
QueryArg = Annotated[str, typer.Argument(help="Search query, for example nvidia.")]
SectorArg = Annotated[str, typer.Argument(help="Sector slug, for example technology.")]
JsonOption = Annotated[
    bool,
    typer.Option("--json", help="Emit a stable JSON payload instead of rich terminal output."),
]
VerboseOption = Annotated[
    bool,
    typer.Option("--verbose", "-v", help="Show more fields in the human-readable output."),
]
AllOption = Annotated[
    bool,
    typer.Option("--all", help="Return all available rows instead of the default preview."),
]
LimitOption = Annotated[
    int,
    typer.Option("--limit", min=1, help="Maximum number of rows to return when --all is not used."),
]
Payload = JsonDict
ServiceGetter = Callable[[], FinanceService]


def create_app(service_factory: Callable[[], FinanceService] | None = None) -> typer.Typer:
    factory = service_factory or YFinanceService

    app = typer.Typer(
        add_completion=False,
        no_args_is_help=True,
        help="Yahoo Finance CLI.",
    )
    options_app = typer.Typer(no_args_is_help=True, help="Inspect option expiration dates and chains.")
    top_app = typer.Typer(no_args_is_help=True, help="Inspect top sector rankings.")
    app.add_typer(options_app, name="options")
    app.add_typer(top_app, name="top")

    def get_service() -> FinanceService:
        return factory()

    _register_root_commands(app, get_service)
    _register_options_commands(options_app, get_service)
    _register_top_commands(top_app, get_service)

    return app


def _register_root_commands(app: typer.Typer, get_service: ServiceGetter) -> None:
    @app.command("info")
    def info_command(
        ticker: TickerArg,
        json_output: JsonOption = False,
        verbose: VerboseOption = False,
    ) -> None:
        _run_command(
            json_output=json_output,
            action=lambda: get_service().get_info(normalize_ticker(ticker)),
            renderer=lambda console, payload: render_info(console, payload, verbose=verbose),
        )

    @app.command("history")
    def history_command(
        ticker: TickerArg,
        period: Annotated[str, typer.Option("--period", help="History window, for example 1mo or 1y.")] = "1mo",
        interval: Annotated[str, typer.Option("--interval", help="Sampling interval, for example 1d or 1wk.")] = "1d",
        chart: Annotated[
            str | None,
            typer.Option("--chart", help="Chart type to export: price or price-volume."),
        ] = None,
        output: Annotated[
            Path | None,
            typer.Option("--output", help="Output file path for chart export."),
        ] = None,
        json_output: JsonOption = False,
        verbose: VerboseOption = False,
    ) -> None:
        if chart is not None:
            _run_command(
                json_output=False,
                action=lambda: _export_history_chart(
                    get_service(),
                    ticker=ticker,
                    period=period,
                    interval=interval,
                    chart=chart,
                    output=output,
                    json_output=json_output,
                ),
                renderer=render_chart_export,
            )
            return

        _run_command(
            json_output=json_output,
            action=lambda: _get_history_payload(
                get_service(),
                ticker=ticker,
                period=period,
                interval=interval,
                chart=chart,
                output=output,
                json_output=json_output,
            ),
            renderer=lambda console, payload: render_history(console, payload, verbose=verbose),
        )

    @app.command("search")
    def search_command(
        query: QueryArg,
        search_type: Annotated[
            str,
            typer.Option("--type", help="Result set to return: quotes, news, or all."),
        ] = "quotes",
        limit: LimitOption = DEFAULT_LIMIT,
        include_all: AllOption = False,
        json_output: JsonOption = False,
        verbose: VerboseOption = False,
    ) -> None:
        _run_command(
            json_output=json_output,
            action=lambda: get_service().search(
                normalize_query(query),
                normalize_search_type(search_type),
                resolve_limit(limit, include_all),
            ),
            renderer=lambda console, payload: render_search(console, payload, verbose=verbose),
        )

    @app.command("news")
    def news_command(
        ticker: TickerArg,
        limit: LimitOption = DEFAULT_LIMIT,
        include_all: AllOption = False,
        json_output: JsonOption = False,
        verbose: VerboseOption = False,
    ) -> None:
        _run_command(
            json_output=json_output,
            action=lambda: get_service().get_news(
                normalize_ticker(ticker),
                resolve_limit(limit, include_all),
            ),
            renderer=lambda console, payload: render_news(console, payload, verbose=verbose),
        )

    @app.command("financials")
    def financials_command(
        ticker: TickerArg,
        frequency: Annotated[
            str,
            typer.Option("--frequency", help="Statement frequency: annual, quarterly, or ttm."),
        ] = "annual",
        json_output: JsonOption = False,
        verbose: VerboseOption = False,
    ) -> None:
        _run_command(
            json_output=json_output,
            action=lambda: get_service().get_financials(
                normalize_ticker(ticker),
                normalize_frequency(frequency),
            ),
            renderer=lambda console, payload: render_financials(console, payload, verbose=verbose),
        )


def _register_options_commands(options_app: typer.Typer, get_service: ServiceGetter) -> None:
    @options_app.command("dates")
    def options_dates_command(
        ticker: TickerArg,
        json_output: JsonOption = False,
    ) -> None:
        _run_command(
            json_output=json_output,
            action=lambda: get_service().get_options_dates(normalize_ticker(ticker)),
            renderer=render_options_dates,
        )

    @options_app.command("chain")
    def options_chain_command(
        ticker: TickerArg,
        expiration_date: str = typer.Option(..., "--date", help="Expiration date in YYYY-MM-DD format."),
        option_type: Annotated[
            str,
            typer.Option("--type", help="Which side of the chain to display: all, calls, or puts."),
        ] = "all",
        limit: LimitOption = DEFAULT_LIMIT,
        include_all: AllOption = False,
        json_output: JsonOption = False,
        verbose: VerboseOption = False,
    ) -> None:
        _run_command(
            json_output=json_output,
            action=lambda: get_service().get_options_chain(
                normalize_ticker(ticker),
                normalize_expiration_date(expiration_date),
                normalize_option_type(option_type),
                resolve_limit(limit, include_all),
            ),
            renderer=lambda console, payload: render_options_chain(console, payload, verbose=verbose),
        )


def _register_top_commands(top_app: typer.Typer, get_service: ServiceGetter) -> None:
    def register_top_command(name: str) -> None:
        @top_app.command(name)
        def top_command(
            sector_slug: SectorArg,
            limit: LimitOption = DEFAULT_LIMIT,
            include_all: AllOption = False,
            json_output: JsonOption = False,
            verbose: VerboseOption = False,
        ) -> None:
            _run_command(
                json_output=json_output,
                action=lambda: get_service().get_top(
                    name,
                    normalize_sector_slug(sector_slug),
                    resolve_limit(limit, include_all),
                ),
                renderer=lambda console, payload: render_top(console, payload, verbose=verbose),
            )

    for name in ("companies", "etfs", "mutual-funds", "growth", "performers"):
        register_top_command(name)


def _run_command(
    *,
    json_output: bool,
    action: Callable[[], Payload],
    renderer: Callable[[Console, Payload], None],
) -> None:
    console = Console(highlight=False)
    try:
        payload = action()
    except CliError as exc:
        render_error(console, exc, json_output=json_output)
        raise typer.Exit(code=1) from exc

    if json_output:
        emit_json(payload)
        return

    renderer(console, payload)


app = create_app()


def _get_history_payload(
    service: FinanceService,
    *,
    ticker: str,
    period: str,
    interval: str,
    chart: str | None,
    output: Path | None,
    json_output: bool,
) -> Payload:
    validate_history_modes(
        json_output=json_output,
        chart=normalize_chart_type(chart) if chart else None,
        output=output,
    )
    return service.get_history(
        normalize_ticker(ticker),
        normalize_period(period),
        normalize_interval(interval),
    )


def _export_history_chart(
    service: FinanceService,
    *,
    ticker: str,
    period: str,
    interval: str,
    chart: str,
    output: Path | None,
    json_output: bool,
) -> Payload:
    normalized_chart = normalize_chart_type(chart)
    validate_history_modes(json_output=json_output, chart=normalized_chart, output=output)
    assert output is not None
    return service.export_history_chart(
        normalize_ticker(ticker),
        normalize_period(period),
        normalize_interval(interval),
        normalized_chart,
        output,
    )


if __name__ == "__main__":
    app()
