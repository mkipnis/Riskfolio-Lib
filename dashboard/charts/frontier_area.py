
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def plot_frontier_area(
    w_frontier,
    nrow=25,
    cmap="tab20",
    n_colors=20,
    height=600,
    width=None,
):
    """
    Create an interactive stacked area chart showing
    asset composition across the efficient frontier.

    Parameters
    ----------
    w_frontier : DataFrame
        Portfolio weights of the efficient frontier.
        Index must contain asset names and columns must
        represent efficient-frontier portfolio points.
    nrow : int
        Number of legend entries per column.
    cmap : str
        Plotly color palette.
    n_colors : int
        Number of distinct colors.
    height : int
        Chart height in pixels.
    width : int, optional
        Chart width in pixels.

    Returns
    -------
    plotly.graph_objects.Figure
    """

    if not isinstance(w_frontier, pd.DataFrame):
        raise TypeError("w_frontier must be a DataFrame")

    if w_frontier.empty:
        raise ValueError("w_frontier cannot be empty")

    # Normalize orientation
    index = w_frontier.index.tolist()
    columns = w_frontier.columns.tolist()

    if not all(isinstance(x, str) for x in index):
        if not all(isinstance(x, str) for x in columns):
            raise ValueError(
                "w_frontier index must contain asset names"
            )
        w_frontier_ = w_frontier.T.copy()
    else:
        w_frontier_ = w_frontier.copy()

    # Validate frontier points
    columns = w_frontier_.columns.tolist()

    if not all(
        isinstance(x, (int, float, np.integer, np.floating))
        for x in columns
    ):
        raise ValueError(
            "w_frontier columns must represent frontier points"
        )

    # Convert weights to numeric
    w_frontier_ = w_frontier_.apply(
        pd.to_numeric,
        errors="coerce"
    )

    if w_frontier_.isna().any().any():
        raise ValueError("Portfolio weights must be numeric")

    if not np.isfinite(w_frontier_.values).all():
        raise ValueError("Portfolio weights must be finite")

    if n_colors < 1:
        raise ValueError("n_colors must be positive")

    if nrow < 1:
        raise ValueError("nrow must be positive")

    # Frontier points
    x = list(range(len(columns)))

    # Color palettes
    palettes = {
        "tab20": px.colors.qualitative.Dark24,
        "Set3": px.colors.qualitative.Set3,
        "Pastel1": px.colors.qualitative.Pastel,
        "Dark2": px.colors.qualitative.Dark2,
        "Paired": px.colors.qualitative.Paired,
        "gist_rainbow": px.colors.qualitative.Alphabet,
    }

    colors = palettes.get(cmap, px.colors.qualitative.Plotly)

    colors = [
        colors[i % len(colors)]
        for i in range(min(n_colors, len(w_frontier_)))
    ]

    # Create figure
    fig = go.Figure()

    for i, asset in enumerate(w_frontier_.index):

        weights = w_frontier_.loc[asset].values

        fig.add_trace(
            go.Scatter(
                x=x,
                y=weights,
                mode="lines",
                name=str(asset),
                stackgroup="one",
                groupnorm="",
                line=dict(
                    color=colors[i % len(colors)],
                    width=0.8,
                ),
                fillcolor=colors[i % len(colors)],
                opacity=0.7,
                hovertemplate=(
                    f"<b>{asset}</b><br>"
                    "Portfolio: %{x}<br>"
                    "Weight: %{y:.2%}"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title="Efficient Frontier's Assets Structure",
        height=height,
        width=width,
        template="plotly_dark",
        hovermode="x unified",
        xaxis=dict(
            title="Efficient Frontier Portfolio",
            range=[0, max(len(x) - 1, 1)],
            showgrid=True,
            gridcolor="rgba(128,128,128,0.25)",
        ),
        yaxis=dict(
            title="Portfolio Weight",
            range=[0, 1],
            tickformat=".2%",
            showgrid=True,
            gridcolor="rgba(128,128,128,0.25)",
        ),
        legend=dict(
            orientation="v",
            x=1.02,
            y=0.5,
            yanchor="middle",
            font=dict(size=10),
        ),
        margin=dict(l=60, r=180, t=60, b=50),
    )

    return fig
