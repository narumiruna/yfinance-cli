---
name: yfinance-cli
description: Use the repository-local `yfinance-cli` command to answer finance data requests about tickers, companies, price history, news, financial statements, option expirations and chains, or sector rankings. Trigger when a user asks for stock or market information that can be retrieved with `yfinance-cli`, especially when Codex should translate a natural-language request into one or more CLI commands and summarize the result.
---

# yfinance-cli

## Overview

Use `uv run yfinance-cli` from the repository root to fetch finance data locally and summarize the result for the user.

Prefer running the CLI over guessing. If the user gives an ambiguous company name, theme, or partial symbol instead of a confirmed ticker, resolve it with `search` first.

## Command Map

- Use `info TICKER` for a company snapshot, quote, market cap, exchange, valuation, and other overview fields.
- Use `history TICKER --period ... --interval ...` for performance and price history questions.
- Use `search QUERY --type quotes|news|all` to find tickers or search by topic.
- Use `news TICKER` for recent articles about one ticker.
- Use `financials TICKER --frequency annual|quarterly|ttm` for statement data.
- Use `options dates TICKER` to list valid expiration dates.
- Use `options chain TICKER --date YYYY-MM-DD [--type all|calls|puts]` after the expiration date is known.
- Use `top CATEGORY SECTOR_SLUG` for sector leaderboard requests.

Valid `top` categories: `companies`, `etfs`, `mutual-funds`, `growth`, `performers`

Valid sector slugs: `basic-materials`, `communication-services`, `consumer-cyclical`, `consumer-defensive`, `energy`, `financial-services`, `healthcare`, `industrials`, `real-estate`, `technology`, `utilities`

For multi-ticker comparisons, run one command per ticker and synthesize the comparison yourself.

## Output Modes And Constraints

- Default output is the summary view for terminal use.
- Use `--verbose` for a richer human-readable answer.
- Use `--json` when you need stable structured output for extraction or further processing.
- Use `--limit` or `--all` on multi-row commands when the user wants more than the default preview.
- Use `history ... --chart price|price-volume --output PATH` for chart exports.
- Do not combine `history --chart` with `--json`.
- Do not invent unsupported flags or subcommands; surface CLI validation hints when the command rejects the input.

## Workflow

1. Normalize the ticker or resolve it with `search`.
2. Run the narrowest command that answers the user request.
3. If the user asks for an option chain without a date, run `options dates` first.
4. Summarize the result instead of dumping raw tables unless the user explicitly asks for raw output.
5. Include the exact command when reproducibility helps.
6. If the CLI returns a validation or not-found error, relay the CLI hint rather than guessing a workaround.

## Examples

- "Summarize Apple" -> `uv run yfinance-cli info AAPL`
- "Show Tesla over six months" -> `uv run yfinance-cli history TSLA --period 6mo --interval 1d`
- "Find the ticker for Taiwan Semiconductor" -> `uv run yfinance-cli search "Taiwan Semiconductor" --type quotes`
- "Show Nvidia news as JSON" -> `uv run yfinance-cli news NVDA --json`
- "List SPY option expirations" -> `uv run yfinance-cli options dates SPY`
- "Show top healthcare growth names" -> `uv run yfinance-cli top growth healthcare`
