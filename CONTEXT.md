# yfinance-cli Remaining Gaps

This document tracks only unresolved product and UX gaps for `yfinance-cli`.
Implemented vocabulary, command-structure decisions, and output-mode rules are
intentionally omitted.

Remove items from this file once they are implemented or covered by tests and
user-facing docs.

## Open Gaps

### Verbose View Consistency

`--verbose` / `-v` is presented as the expanded human-readable mode across the
CLI, but `options dates` currently exposes only summary output and `--json`.
Resolve this by either adding a meaningful verbose mode to `options dates` or
by narrowing the global verbose claim to commands that actually have additional
fields to reveal.

### Output Mode Regression Coverage

The CLI already implements summary output, verbose output, and `--json`, but the
test suite does not yet lock down the summary-versus-verbose behavior for every
command that supports `--verbose`. Add focused CLI coverage for `info`,
`history`, `search`, `news`, `options chain`, and `top` so output-mode
regressions are caught early.
