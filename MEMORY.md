## GOTCHA

- This repo starts greenfield; do not assume existing package layout, git metadata, or local commands.
- In `yfinance` 1.3.0, sector rankings expose `top_companies` / `top_etfs` / `top_mutual_funds`, but `growth` and `performers` come from `Industry`; sector-level CLI commands must aggregate industry data.
- Use `yfinance-cli` consistently as the console command in docs, hints, and examples.

## TASTE

- Treat `narumiruna/yfinance-mcp` as a reference implementation only; keep the CLI directly on `yfinance` with CLI-native command names.
- Build the `yfinance-cli` command tree with Typer.
- Use `rich` for human-readable terminal output.
- Target Python 3.12+.
- Keep the CLI UX and project docs in English.
- Treat `CONTEXT.md` as a short remaining-gaps note, not a permanent glossary.
- Use `yfinance-cli` as both the distribution name and console script, and `yfinance_cli` as the import package.
- Recommend `uv tool install yfinance-cli` as the primary installation path in README.
- Prefer unit tests and CLI parsing/output tests for v1; do not rely on live Yahoo Finance integration tests.
- Stay close to `yfinance` semantics where possible; only add CLI-specific shaping when it materially improves terminal ergonomics.
- Accept CLI-friendly lowercase sector slugs such as `technology` and `communication-services`.
- Make `--json` output CLI-owned stable schemas instead of raw `yfinance` or `yfinance-mcp` payloads.
- Reuse the `yfinance-mcp` high-level error code names for structured `--json` errors.
- Default multi-result commands to 10 results, with `--limit` and `--all` for expansion.
- Infer chart export format from the `--output` file extension instead of imposing a default image format.
- Preserve `yfinance` news ordering by default instead of re-sorting in the CLI.
- Make `yfinance-cli history --chart ...` mutually exclusive with `--json`.
- For invalid input, show human-readable errors plus valid values or the next corrective command.
- Require an explicit expiration date for `yfinance-cli options chain`; use `yfinance-cli options dates` first.
- Default `yfinance-cli options chain` to a summary plus the first 10 calls/puts rows, with `--limit` and `--all` for expansion.
- Keep `yfinance-cli history` on `--period` and `--interval` only for v1.
- Default `yfinance-cli history` to a summary plus the most recent table rows, not a full raw table dump.
- Keep `yfinance-cli info` as one aggregate command rather than splitting it into quote/profile/valuation subcommands.
- Do not add CLI-only shortcut commands; keep the command set aligned to the underlying capabilities.
