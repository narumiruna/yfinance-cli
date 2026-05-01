## GOTCHA

- This repo starts greenfield; do not assume existing package layout, git metadata, or local commands.

## TASTE

- Treat `narumiruna/yfinance-mcp` as a reference implementation only; keep the CLI directly on `yfinance` with CLI-native command names.
- Build the `yf` command tree with Typer.
- Use `rich` for human-readable terminal output.
- Target Python 3.12+.
- Keep the CLI UX and project docs in English.
- Use `yfinance-cli` as the distribution name, `yfinance_cli` as the import package, and `yf` as the console script.
- Recommend `uv tool install yfinance-cli` as the primary installation path in README.
- Prefer unit tests and CLI parsing/output tests for v1; do not rely on live Yahoo Finance integration tests.
- Stay close to `yfinance` semantics where possible; only add CLI-specific shaping when it materially improves terminal ergonomics.
- Accept CLI-friendly lowercase sector slugs such as `technology` and `communication-services`.
- Make `--json` output CLI-owned stable schemas instead of raw `yfinance` or `yfinance-mcp` payloads.
- Reuse the `yfinance-mcp` high-level error code names for structured `--json` errors.
- Default multi-result commands to 10 results, with `--limit` and `--all` for expansion.
- Infer chart export format from the `--output` file extension instead of imposing a default image format.
- Preserve `yfinance` news ordering by default instead of re-sorting in the CLI.
- Make `yf history --chart ...` mutually exclusive with `--json`.
- For invalid input, show human-readable errors plus valid values or the next corrective command.
- Require an explicit expiration date for `yf options chain`; use `yf options dates` first.
- Default `yf options chain` to a summary plus the first 10 calls/puts rows, with `--limit` and `--all` for expansion.
- Keep `yf history` on `--period` and `--interval` only for v1.
- Default `yf history` to a summary plus the most recent table rows, not a full raw table dump.
- Keep `yf info` as one aggregate command rather than splitting it into quote/profile/valuation subcommands.
- Do not add CLI-only shortcut commands; keep the command set aligned to the underlying capabilities.
