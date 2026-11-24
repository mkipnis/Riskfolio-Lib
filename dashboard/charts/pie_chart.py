
import numpy as np
import pandas as pd
import plotly.graph_objects as go


def plot_pie(
    w,
    title="",
    others=0.05,
    nrow=25,
    cmap="tab20",
    n_colors=20,
    height=600,
    width=None,
):
    """
    Create an interactive portfolio composition donut chart.

    Parameters
    ----------
    w : DataFrame or Series
        Portfolio weights.
    title : str
        Chart title.
    others : float
        Fraction of absolute portfolio weights grouped into Others.
    nrow : int
        Number of legend entries per column.
    cmap : str
        Color palette.
    n_colors : int
        Number of colors in the palette.
    height : int
        Chart height in pixels.
    width : int, optional
        Chart width in pixels.

    Returns
    -------
    plotly.graph_objects.Figure
    """

    # Normalize input
    if isinstance(w, pd.Series):
        w_ = w.to_frame()

    elif isinstance(w, pd.DataFrame):
        if w.shape[0] == 1:
            w_ = w.T.copy()
        elif w.shape[1] == 1:
            w_ = w.copy()
        else:
            raise TypeError("w must be a column DataFrame or Series")

    else:
        raise TypeError("w must be a column DataFrame or Series")

    # Validate weights
    weights = pd.to_numeric(w_.iloc[:, 0], errors="coerce")

    if weights.isna().any() or not np.isfinite(weights).all():
        raise ValueError("Portfolio weights must be finite numeric values")

    if others < 0 or others >= 1:
        raise ValueError("others must be >= 0 and < 1")

    if nrow < 1:
        raise ValueError("nrow must be >= 1")

    if weights.abs().sum() == 0:
        raise ValueError("Portfolio weights cannot all be zero")

    # Sort by absolute weight
    sizes = pd.DataFrame({
        "labels": weights.index.astype(str),
        "abs_values": weights.abs().values,
        "values": weights.values,
    })

    sizes = sizes.sort_values(
        by="abs_values",
        ascending=False
    ).reset_index(drop=True)

    # Aggregate small positions into Others
    if others > 0:
        cumulative = sizes["abs_values"].cumsum() / sizes["abs_values"].sum()

        cutoff = np.searchsorted(
            cumulative.values,
            1 - others,
            side="left"
        )

        if cutoff < len(sizes) - 1:
            remaining = sizes.iloc[cutoff + 1:]

            other = pd.DataFrame([{
                "labels": "Others",
                "abs_values": remaining["abs_values"].sum(),
                "values": remaining["values"].sum(),
            }])

            sizes = pd.concat(
                [sizes.iloc[:cutoff + 1], other],
                ignore_index=True
            )

    # Chart data
    labels = sizes["labels"].tolist()
    values = sizes["abs_values"].tolist()
    signed_values = sizes["values"].tolist()

    total = sum(values)

    if not title:
        title = "Portfolio Composition"

    if (weights < 0).any():
        title += " (Areas in Absolute Values)"

    # Color palette
    palette = {
        "tab20": "Plotly",
        "Set3": "Set3",
        "Pastel1": "Pastel",
        "Dark2": "Dark2",
        "Paired": "Paired",
        "viridis": "Viridis",
        "plasma": "Plasma",
        "gist_rainbow": "Rainbow",
    }

    colorscale = palette.get(cmap, cmap)

    # Create chart
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.60,
            sort=False,
            direction="clockwise",
            rotation=345,
            marker=dict(
                colors=None,
                line=dict(color="black", width=1),
            ),
            textinfo="none",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Absolute weight: %{percent}<br>"
                "Signed weight: %{customdata:.2%}"
                "<extra></extra>"
            ),
            customdata=signed_values,
        )
    )

    # Apply Plotly colors
    fig.update_traces(
        marker=dict(
            colors=(
                __import__("plotly.express", fromlist=["colors"])
                .colors.sample_colorscale(
                    colorscale,
                    [i / max(n_colors - 1, 1) for i in range(n_colors)]
                )[:len(labels)]
                if colorscale in ["Viridis", "Plasma", "Rainbow"]
                else None
            )
        )
    )

    # For categorical palettes, use Plotly Express palette names
    if colorscale not in ["Viridis", "Plasma", "Rainbow"]:
        import plotly.express as px

        palette_colors = getattr(px.colors.qualitative, colorscale, None)

        if palette_colors:
            fig.update_traces(
                marker=dict(
                    colors=[
                        palette_colors[i % len(palette_colors)]
                        for i in range(len(labels))
                    ]
                )
            )

    # Outside labels
    fig.update_traces(
        text=[
            f"{label} {value / total:.1%}"
            for label, value in zip(labels, values)
        ],
        textinfo="text",
        textposition="outside",
        automargin=True,
    )

    fig.update_layout(
        title=title,
        height=height,
        width=width,
        showlegend=True,
        legend=dict(
            orientation="v",
            x=1.02,
            y=0.5,
            yanchor="middle",
            font=dict(size=11),
        ),
        margin=dict(l=30, r=180, t=60, b=30),
        template="plotly_dark",
    )

    return fig
