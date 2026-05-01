from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from yfinance_cli.errors import CliError


def export_history_chart(
    *,
    history: pd.DataFrame,
    ticker: str,
    chart_type: str,
    output_path: Path,
) -> None:
    if history.empty:
        raise CliError("NO_DATA", f"No history data is available for '{ticker}'.")

    suffix = output_path.suffix.lower().removeprefix(".")
    if not suffix:
        raise CliError(
            "INVALID_PARAMS",
            f"Output path '{output_path}' must include a file extension.",
        )

    history = history.copy()
    history.index = pd.to_datetime(history.index)
    history = history.sort_index()

    if chart_type == "price":
        figure, axis = plt.subplots(figsize=(12, 6))
        axis.plot(history.index, history["Close"], linewidth=2, label="Close")
        axis.set_ylabel("Price")
        axis.legend(loc="upper left")
        axes = [axis]
    else:
        figure, (axis, volume_axis) = plt.subplots(
            2,
            1,
            figsize=(12, 8),
            sharex=True,
            gridspec_kw={"height_ratios": [3, 1]},
        )
        axis.plot(history.index, history["Close"], linewidth=2, label="Close")
        axis.set_ylabel("Price")
        axis.legend(loc="upper left")
        volume_axis.bar(history.index, history["Volume"], width=1.0, alpha=0.7)
        volume_axis.set_ylabel("Volume")
        axes = [axis, volume_axis]

    for axis in axes:
        axis.grid(alpha=0.2)
        axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

    figure.suptitle(f"{ticker} history")
    figure.autofmt_xdate()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.tight_layout()
    try:
        figure.savefig(output_path, format=suffix, dpi=160, bbox_inches="tight")
    except ValueError as exc:
        raise CliError(
            "INVALID_PARAMS",
            f"Unsupported output format '.{suffix}'.",
            hint="Choose a Matplotlib-supported extension such as .png or .webp.",
        ) from exc
    finally:
        plt.close(figure)
