import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.dates as mdates
from typing import Optional, Tuple


def plot_derivative_indicators(
    df: pd.DataFrame,
    price_data: Optional[pd.DataFrame] = None,
    title: str = "Derivative Market Indicators",
    figsize: Tuple[int, int] = (16, 16),
):
    """
    Visualizes the core derivative indicators on a chart.

    Parameters:
        df: DataFrame containing indicator data
        price_data: DataFrame with price data (optional)
        title: Chart title
        figsize: Figure size

    Returns:
        Matplotlib figure object
    """
    # Determine how many subplots we need based on available indicators
    num_plots = 1  # Price/OI always shown
    has_funding = "funding_rate" in df.columns
    has_ls_ratio = "long_short_ratio" in df.columns
    has_liquidations = "long" in df.columns and "short" in df.columns
    has_squeeze = (
        "potential_short_squeeze" in df.columns
        or "potential_long_squeeze" in df.columns
    )
    has_divergence = "oi_price_divergence" in df.columns
    has_oi_volume = "oi_volume_ratio" in df.columns

    if has_funding:
        num_plots += 1
    if has_ls_ratio:
        num_plots += 1
    if has_liquidations:
        num_plots += 1
    if has_divergence or has_oi_volume:
        num_plots += 1

    # Create figure and gridspec
    fig = plt.figure(figsize=figsize)
    gs = GridSpec(num_plots, 1, figure=fig, height_ratios=[3] + [1] * (num_plots - 1))

    current_plot = 0

    # Plot 1: Price and Open Interest
    ax1 = fig.add_subplot(gs[current_plot])
    current_plot += 1

    # Plot price if available
    if price_data is not None and "close" in price_data.columns:
        # Align price data with our indicator data
        aligned_price = pd.merge_asof(
            df[["datetime"]].sort_values("datetime"),
            price_data[["datetime", "close"]],
            on="datetime",
            direction="nearest",
        )
        ax1.plot(df["datetime"], aligned_price["close"], color="blue", label="Price")
        ax1.set_ylabel("Price", color="blue")

    # Plot Open Interest if available
    if "open_interest" in df.columns:
        ax1_twin = ax1.twinx()
        ax1_twin.plot(
            df["datetime"], df["open_interest"], color="orange", label="Open Interest"
        )
        ax1_twin.set_ylabel("Open Interest", color="orange")

    # Mark squeeze events if available
    if has_squeeze:
        if "potential_short_squeeze" in df.columns:
            short_squeeze_points = df[df["potential_short_squeeze"]]
            if not short_squeeze_points.empty:
                ax1.scatter(
                    short_squeeze_points["datetime"],
                    [ax1.get_ylim()[0] * 1.05] * len(short_squeeze_points),
                    marker="^",
                    color="red",
                    s=100,
                    label="Potential Short Squeeze",
                )

        if "potential_long_squeeze" in df.columns:
            long_squeeze_points = df[df["potential_long_squeeze"]]
            if not long_squeeze_points.empty:
                ax1.scatter(
                    long_squeeze_points["datetime"],
                    [ax1.get_ylim()[0] * 1.02] * len(long_squeeze_points),
                    marker="v",
                    color="green",
                    s=100,
                    label="Potential Long Squeeze",
                )

    # Mark Long/Short Ratio extremes if available
    if "extreme_bullish" in df.columns and "extreme_bearish" in df.columns:
        bullish_points = df[df["extreme_bullish"]]
        bearish_points = df[df["extreme_bearish"]]

        if not bullish_points.empty:
            ax1.scatter(
                bullish_points["datetime"],
                [ax1.get_ylim()[1] * 0.98] * len(bullish_points),
                marker="*",
                color="green",
                s=100,
                label="Extreme Bullish LS Ratio",
            )

        if not bearish_points.empty:
            ax1.scatter(
                bearish_points["datetime"],
                [ax1.get_ylim()[1] * 0.95] * len(bearish_points),
                marker="*",
                color="red",
                s=100,
                label="Extreme Bearish LS Ratio",
            )

    ax1.set_title(f"{title} - Price & Open Interest")
    ax1.grid(True)
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = [], []
    if "open_interest" in df.columns:
        handles2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc="upper left")

    # Plot 2: Funding Rate and Trend
    if has_funding:
        ax2 = fig.add_subplot(gs[current_plot], sharex=ax1)
        current_plot += 1

        ax2.plot(
            df["datetime"], df["funding_rate"], color="purple", label="Funding Rate"
        )
        ax2.axhline(y=0, color="black", linestyle="-", alpha=0.3)

        if "funding_rate_trend" in df.columns:
            ax2_twin = ax2.twinx()
            ax2_twin.plot(
                df["datetime"],
                df["funding_rate_trend"],
                color="red",
                linestyle="--",
                label="Funding Trend",
            )
            ax2_twin.set_ylabel("Funding Trend", color="red")

        ax2.set_title("Funding Rate Analysis")
        ax2.set_ylabel("Funding Rate", color="purple")
        ax2.grid(True)

        handles1, labels1 = ax2.get_legend_handles_labels()
        handles2, labels2 = [], []
        if "funding_rate_trend" in df.columns:
            handles2, labels2 = ax2_twin.get_legend_handles_labels()
        ax2.legend(handles1 + handles2, labels1 + labels2, loc="upper left")

    # Plot 3: Long/Short Ratio
    if has_ls_ratio:
        ax3 = fig.add_subplot(gs[current_plot], sharex=ax1)
        current_plot += 1

        ax3.plot(
            df["datetime"],
            df["long_short_ratio"],
            color="green",
            label="Long/Short Ratio",
        )
        ax3.axhline(y=1, color="black", linestyle="-", alpha=0.3)

        if "ls_ratio_z_score" in df.columns:
            ax3_twin = ax3.twinx()
            ax3_twin.plot(
                df["datetime"],
                df["ls_ratio_z_score"],
                color="orange",
                linestyle="--",
                label="LS Ratio Z-Score",
            )
            ax3_twin.axhline(y=2, color="red", linestyle="--", alpha=0.5)
            ax3_twin.axhline(y=-2, color="red", linestyle="--", alpha=0.5)
            ax3_twin.set_ylabel("Z-Score", color="orange")

        ax3.set_title("Long/Short Ratio Analysis")
        ax3.set_ylabel("L/S Ratio", color="green")
        ax3.grid(True)

        handles1, labels1 = ax3.get_legend_handles_labels()
        handles2, labels2 = [], []
        if "ls_ratio_z_score" in df.columns:
            handles2, labels2 = ax3_twin.get_legend_handles_labels()
        ax3.legend(handles1 + handles2, labels1 + labels2, loc="upper left")

    # Plot 4: Liquidations
    if has_liquidations:
        ax4 = fig.add_subplot(gs[current_plot], sharex=ax1)
        current_plot += 1

        if "long" in df.columns and "short" in df.columns:
            ax4.bar(
                df["datetime"],
                df["long"],
                color="green",
                alpha=0.5,
                label="Long Liquidations",
            )
            ax4.bar(
                df["datetime"],
                df["short"],
                color="red",
                alpha=0.5,
                label="Short Liquidations",
            )
            ax4.set_title("Liquidations Analysis")
            ax4.set_ylabel("Liquidation Volume")
            ax4.grid(True)
            ax4.legend(loc="upper left")

    # Plot 5: OI Price Divergence & OI/Volume Ratio
    if has_divergence or has_oi_volume:
        ax5 = fig.add_subplot(gs[current_plot], sharex=ax1)
        current_plot += 1

        if has_divergence:
            ax5.plot(
                df["datetime"],
                df["oi_price_divergence"],
                color="magenta",
                label="OI-Price Divergence",
            )
            ax5.axhline(y=0, color="black", linestyle="-", alpha=0.3)
            ax5.set_ylabel("OI-Price Divergence", color="magenta")

        if has_oi_volume:
            if has_divergence:
                ax5_twin = ax5.twinx()
                ax5_twin.plot(
                    df["datetime"],
                    df["oi_volume_ratio"],
                    color="brown",
                    label="OI/Volume Ratio",
                )
                ax5_twin.set_ylabel("OI/Volume Ratio", color="brown")
            else:
                ax5.plot(
                    df["datetime"],
                    df["oi_volume_ratio"],
                    color="brown",
                    label="OI/Volume Ratio",
                )
                ax5.set_ylabel("OI/Volume Ratio", color="brown")

        title_parts = []
        if has_divergence:
            title_parts.append("OI-Price Divergence")
        if has_oi_volume:
            title_parts.append("OI/Volume Ratio")

        ax5.set_title(" & ".join(title_parts))
        ax5.grid(True)

        handles1, labels1 = ax5.get_legend_handles_labels()
        handles2, labels2 = [], []
        if has_divergence and has_oi_volume:
            handles2, labels2 = ax5_twin.get_legend_handles_labels()
        ax5.legend(handles1 + handles2, labels1 + labels2, loc="upper left")

    # Format x-axis dates and add grid
    for ax in fig.axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(df) // 30)))
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig
