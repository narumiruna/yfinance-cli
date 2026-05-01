# yfinance-cli

`yfinance-cli` is a terminal-first CLI for Yahoo Finance Data. It keeps the command
set close to `yfinance`, defaults to readable rich output, and offers stable JSON
payloads when you need shell pipelines or automation.

## Features

- Single-ticker lookups for company info, price history, news, financials, and options
- Search across quote matches, news, or both
- Sector ranking lookups for companies, ETFs, mutual funds, growth, and performers
- Human-readable summary output by default
- Stable `--json` output for scripts and pipelines
- History chart export with the output format inferred from the file extension

## Requirements

- Python 3.12+
- `uv` for local development and packaging workflows

## Installation

Primary packaged install:

```bash
uv tool install yfinance-cli
```

Run it after installation:

```bash
yfinance-cli --help
```

Run it without installing:

```bash
uvx yfinance-cli --help
```

Run a one-off command with `uvx`:

```bash
uvx yfinance-cli info AAPL
```

Install from source for local development:

```bash
git clone git@github.com:narumiruna/yfinance-cli.git
cd yfinance-cli
uv sync
uv run yfinance-cli --help
```

## Quick Start

```bash
# One-off execution without installing
uvx yfinance-cli info AAPL

# Company overview
yfinance-cli info AAPL

# Historical prices
yfinance-cli history AAPL --period 6mo --interval 1d

# Export a chart
yfinance-cli history AAPL --chart price-volume --output aapl.webp

# Search quotes
yfinance-cli search nvidia

# Search news results as JSON
yfinance-cli search nvidia --type news --json

# Latest ticker news
yfinance-cli news MSFT --limit 5

# Financial statements
yfinance-cli financials NVDA --frequency quarterly -v

# Option expiration dates, then a chain lookup
yfinance-cli options dates AAPL
yfinance-cli options chain AAPL --date 2026-06-19 --type calls

# Sector rankings
yfinance-cli top companies technology
```

## Command Overview

### `info`

Look up a single ticker and show a summary of company, market, price, and key metrics.

```bash
yfinance-cli info AAPL
yfinance-cli info MSFT --json
yfinance-cli info NVDA --verbose
```

### `history`

Fetch historical price data for one ticker.

```bash
yfinance-cli history AAPL
yfinance-cli history AAPL --period 1y --interval 1wk
yfinance-cli history AAPL --json
yfinance-cli history AAPL --chart price --output aapl.png
```

Allowed `--period` values:
`1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`

Allowed `--interval` values:
`1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m`, `1h`, `1d`, `5d`, `1wk`, `1mo`, `3mo`

Allowed `--chart` values:
`price`, `price-volume`

Notes:

- `--chart` and `--json` cannot be used together.
- `--output` is required when exporting a chart.
- The export format is inferred from the output file extension.

### `search`

Search quote matches, news, or both.

```bash
yfinance-cli search tesla
yfinance-cli search tesla --type all
yfinance-cli search "artificial intelligence" --type news --limit 20
yfinance-cli search nvidia --all --json
```

Allowed `--type` values:
`quotes`, `news`, `all`

### `news`

Show recent news for a single ticker.

```bash
yfinance-cli news AMZN
yfinance-cli news AMD --limit 5
yfinance-cli news META --all --json
```

### `financials`

Show income statement, balance sheet, and cash flow data.

```bash
yfinance-cli financials AAPL
yfinance-cli financials AAPL --frequency quarterly
yfinance-cli financials AAPL --frequency ttm --json
```

Allowed `--frequency` values:
`annual`, `quarterly`, `ttm`

Note:

- `ttm` does not include a balance sheet because that dataset is not available for the trailing frequency.

### `options`

Inspect option expiration dates and option chains.

```bash
yfinance-cli options dates AAPL
yfinance-cli options chain AAPL --date 2026-06-19
yfinance-cli options chain AAPL --date 2026-06-19 --type puts --limit 25
yfinance-cli options chain AAPL --date 2026-06-19 --all --json
```

Allowed `--type` values for `options chain`:
`all`, `calls`, `puts`

Notes:

- `options chain` requires an explicit `--date`.
- A useful workflow is `yfinance-cli options dates TICKER` first, then `options chain`.

### `top`

Inspect top sector rankings grouped by category.

Available categories:
`companies`, `etfs`, `mutual-funds`, `growth`, `performers`

```bash
yfinance-cli top companies technology
yfinance-cli top etfs financial-services
yfinance-cli top growth healthcare --limit 20
yfinance-cli top performers communication-services --json
```

Available sector slugs:
`basic-materials`, `communication-services`, `consumer-cyclical`,
`consumer-defensive`, `energy`, `financial-services`, `healthcare`,
`industrials`, `real-estate`, `technology`, `utilities`

## Output Modes

Default output is a human-readable summary view for terminal use.

Use `--verbose` or `-v` to expand the human-readable output with more fields:

```bash
yfinance-cli info AAPL -v
```

Use `--json` to emit stable JSON payloads for automation:

```bash
yfinance-cli history AAPL --json
```

Use `--limit` for preview size or `--all` to request the full result set on multi-row commands:

```bash
yfinance-cli news AAPL --limit 5
yfinance-cli search nvidia --all
```

## Docker

Build the local image:

```bash
docker build -t yfinance-cli .
```

Run a command through the image:

```bash
docker run --rm yfinance-cli info AAPL
```

Export a chart to the host by mounting a directory:

```bash
docker run --rm -v "$PWD:/work" yfinance-cli \
  history AAPL --chart price-volume --output /work/aapl.webp
```

## Development

Set up the local environment:

```bash
uv sync
```

Useful commands:

```bash
uv run yfinance-cli --help
uv build
just format
just lint
just type
just test
just all
```

Tests are expected to be fast and deterministic. Prefer mocked Yahoo Finance behavior
over live network integration tests.
