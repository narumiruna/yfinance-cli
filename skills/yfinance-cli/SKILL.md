---
name: yfinance-cli
description: Use when answering finance-data requests with `yfinance-cli`, including ticker lookup, company snapshots, price history, ticker news, financial statements, option expiration dates or chains, and sector rankings. Trigger when a user asks for stock, ETF, or options information that maps to the CLI's `search`, `info`, `history`, `news`, `financials`, `options`, or `top` commands and Codex should run the CLI and summarize the result.
---

# yfinance-cli

## Overview

Use `yfinance-cli` to fetch finance data and summarize the result for the user.

Prefer running the CLI over guessing. If the user gives an ambiguous company name, theme, or partial symbol instead of a confirmed ticker, resolve it with `search` first.

## Command Selection

- If the current working directory is the `yfinance-cli` repository root or one of its subdirectories, run `uv run yfinance-cli ...` from the repository root.
- Otherwise, run `uvx yfinance-cli ...`.
- Treat `uv run` as the current local workspace or branch. Treat `uvx` as the latest published release.
- If `uv run` fails inside the repository, report the local repository or environment issue and stop instead of falling back to `uvx`.
- If `uvx` fails because `uv` is missing, the network is restricted, or package resolution fails, report the prerequisite and stop. Offer `uv tool install yfinance-cli` as the manual install path.

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

1. Choose the execution path with the command selection rules above.
2. Normalize the ticker or resolve it with `search`.
3. Run the narrowest command that answers the user request.
4. If the user asks for an option chain without a date, run `options dates` first.
5. Summarize the result instead of dumping raw tables unless the user explicitly asks for raw output.
6. Include the exact command when reproducibility helps.
7. If the CLI returns a validation or not-found error, relay the CLI hint rather than guessing a workaround.

## Examples

- "Summarize Apple" -> `uvx yfinance-cli info AAPL`
- "Show Tesla over six months" -> `uvx yfinance-cli history TSLA --period 6mo --interval 1d`
- "Find the ticker for Taiwan Semiconductor" -> `uvx yfinance-cli search "Taiwan Semiconductor" --type quotes`
- "Show Nvidia news as JSON" -> `uvx yfinance-cli news NVDA --json`
- "List SPY option expirations" -> `uvx yfinance-cli options dates SPY`
- "Show top healthcare growth names" -> `uvx yfinance-cli top growth healthcare`
