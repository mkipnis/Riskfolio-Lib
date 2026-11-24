
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

import riskfolio.src.PlotFunctions as plf
import riskfolio.src.RiskFunctions as rk

def plot_frontier(
    w_frontier,
    returns,
    mu=None,
    cov=None,
    rm="MV",
    kelly=False,
    rf=0,
    alpha=0.05,
    a_sim=100,
    beta=None,
    b_sim=None,
    kappa=0.30,
    kappa_g=None,
    p_em=2,
    p_esm=2,
    solver="CLARABEL",
    cmap="Viridis",
    w=None,
    label="Portfolio",
    marker="star",
    s=16,
    c="red",
    height=600,
    width=1000,
    t_factor=252,
):
    """
    Creates a Plotly efficient frontier chart for the specified risk measure.

    Returns
    -------
    plotly.graph_objects.Figure
    """

    if not isinstance(w_frontier, pd.DataFrame):
        raise TypeError("w_frontier must be a DataFrame")

    if not isinstance(returns, pd.DataFrame):
        raise TypeError("returns must be a DataFrame")

    if returns.columns.tolist() == w_frontier.index.tolist():
        w_frontier_ = w_frontier.copy()
    elif returns.columns.tolist() == w_frontier.columns.tolist():
        w_frontier_ = w_frontier.T.copy()
    else:
        raise ValueError("returns and w_frontier must have same assets")

    if mu is None:
        mu_ = returns.mean()
    elif isinstance(mu, pd.DataFrame):
        if mu.shape[0] == 1 or mu.shape[1] == 1:
            mu_ = mu.squeeze()
        else:
            raise TypeError("mu must be a column DataFrame or Series")
    elif isinstance(mu, pd.Series):
        mu_ = mu.copy()
    else:
        raise TypeError("mu must be a DataFrame or Series")

    if cov is None:
        cov = returns.cov()
    elif isinstance(cov, pd.DataFrame):
        if cov.index.tolist() != cov.columns.tolist():
            raise TypeError(
                "cov must be a square DataFrame with same labels in indexes and columns"
            )
        if cov.index.tolist() != w_frontier_.index.tolist():
            raise ValueError("cov and w_frontier must have the same assets")
    else:
        raise TypeError("cov must be a square DataFrame")

    if beta is None:
        beta = alpha
    if b_sim is None:
        b_sim = a_sim
    if kappa_g is None:
        kappa_g = kappa

    # Prepare optional user portfolios
    w_ = None

    if w is not None:
        if isinstance(w, pd.Series):
            w_ = w.to_frame()
        elif isinstance(w, pd.DataFrame):
            if returns.columns.tolist() == w.columns.tolist():
                w_ = w.T.copy()
            elif returns.columns.tolist() == w.index.tolist():
                w_ = w.copy()
            else:
                raise ValueError("returns and w must have the same assets")
        else:
            raise TypeError("w must be a DataFrame or Series")

    # Risk measure label
    item = plf.rmeasures.index(rm)

    x_label = plf.rm_names[item] + " (" + rm + ")"

    if rm in [
        "CVaR", "TG", "EVaR", "RLVaR",
        "CVRG", "TGRG", "EVRG", "RVRG",
        "CDaR", "EDaR", "RLDaR",
    ]:
        x_label += f" (alpha = {alpha:.2%})"

    if rm in ["CVRG", "TGRG", "EVRG", "RVRG"]:
        x_label += f", beta = {beta:.2%}"

    if rm in ["RLVaR", "RLDaR", "RVRG"]:
        x_label += f", kappa = {kappa:.2f}"
        x_label += f", kappa_g = {kappa_g:.2f}"

    if rm == "EM":
        x_label = f"{p_em}-th " + x_label
        x_label += f" of Order {2 * p_em}"

    if rm == "ESM":
        x_label = f"{p_esm}-th " + x_label
        x_label += f" of Order {2 * p_esm}"

    # Calculate efficient frontier
    X1, Y1, Z1 = [], [], []

    mu_array = np.array(mu_, ndmin=2)

    for i in range(w_frontier_.shape[1]):
        weights = np.array(
            w_frontier_.iloc[:, i], ndmin=2
        ).T

        try:
            risk = rk.Sharpe_Risk(
                returns=returns,
                w=weights,
                cov=cov,
                rm=rm,
                rf=rf,
                alpha=alpha,
                a_sim=a_sim,
                beta=beta,
                b_sim=b_sim,
                kappa=kappa,
                kappa_g=kappa_g,
                p_em=p_em,
                p_esm=p_esm,
                solver=solver,
            )

            if kelly:
                ret = np.mean(
                    np.log(1 + returns.to_numpy() @ weights)
                )
            else:
                ret = (mu_array @ weights).item()

            ret = float(ret) * t_factor

            if rm not in [
                "MDD", "ADD", "CDaR", "EDaR", "RLDaR", "UCI"
            ]:
                risk = risk * t_factor**0.5

            risk = float(np.asarray(risk).item())
            ratio = (ret - rf) / risk

            X1.append(risk)
            Y1.append(ret)
            Z1.append(ratio)

        except Exception as e:
            print(f"Skipping iteration '{i}' due to error: {e}")

    if not X1:
        raise ValueError("Unable to calculate any efficient frontier points")

    # Efficient frontier scatter
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=X1,
            y=Y1,
            mode="markers",
            name="Efficient Frontier",
            marker=dict(
                size=s,
                color=Z1,
                colorscale=cmap,
                showscale=True,
                colorbar=dict(
                    title="Risk Adjusted<br>Return Ratio"
                ),
                line=dict(width=0.5, color="black"),
            ),
            customdata=np.column_stack([Z1]),
            hovertemplate=(
                "Risk: %{x:.2%}<br>"
                "Return: %{y:.2%}<br>"
                "Risk Adjusted Ratio: %{customdata[0]:.4f}"
                "<extra></extra>"
            ),
        )
    )

    # Optional user portfolios
    if w_ is not None:

        if isinstance(label, str):
            labels = [label]
        elif label is None:
            labels = w_.columns.tolist()
        else:
            labels = list(label)

        if w_.shape[1] != len(labels):
            labels = w_.columns.tolist()

        # Make duplicate labels unique
        labels = [
            f"{v} {labels[:i].count(v) + 1}" if labels.count(v) > 1 else v
            for i, v in enumerate(labels)
        ]

        if isinstance(c, str):
            colors = [c] * w_.shape[1]
        elif c is None:
            colors = ["red"] * w_.shape[1]
        elif isinstance(c, list):
            colors = c
            if len(colors) != w_.shape[1]:
                colors = px.colors.qualitative.Dark24
        else:
            colors = px.colors.qualitative.Dark24

        for i in range(w_.shape[1]):

            weights = w_.iloc[:, i].to_numpy().reshape(-1, 1)

            risk = rk.Sharpe_Risk(
                returns=returns,
                w=weights,
                cov=cov,
                rm=rm,
                rf=rf,
                alpha=alpha,
                a_sim=a_sim,
                beta=beta,
                b_sim=b_sim,
                kappa=kappa,
                kappa_g=kappa_g,
                p_em=p_em,
                p_esm=p_esm,
                solver=solver,
            )

            if kelly:
                ret = np.mean(
                    np.log(1 + returns.to_numpy() @ weights)
                )
            else:
                ret = (mu_array @ weights).item()

            ret = float(ret) * t_factor

            if rm not in [
                "MDD", "ADD", "CDaR", "EDaR", "RLDaR", "UCI"
            ]:
                risk = risk * t_factor**0.5

            risk = float(np.asarray(risk).item())

            color = colors[i % len(colors)]

            fig.add_trace(
                go.Scatter(
                    x=[risk],
                    y=[ret],
                    mode="markers",
                    name=labels[i],
                    marker=dict(
                        symbol=marker,
                        size=s,
                        color=color,
                        line=dict(width=1, color="black"),
                    ),
                    hovertemplate=(
                        f"{labels[i]}<br>"
                        "Risk: %{x:.2%}<br>"
                        "Return: %{y:.2%}"
                        "<extra></extra>"
                    ),
                )
            )

    # Layout and axes
    xmin, xmax = min(X1), max(X1)
    ymin, ymax = min(Y1), max(Y1)

    xpad = abs(xmax - xmin) * 0.1
    ypad = abs(ymax - ymin) * 0.1

    if xpad == 0:
        xpad = max(abs(xmin) * 0.1, 0.01)
    if ypad == 0:
        ypad = max(abs(ymin) * 0.1, 0.01)

    fig.update_layout(
        title=f"Efficient Frontier Mean - {x_label}",
        xaxis_title=f"Expected Risk - {x_label}",
        yaxis_title=(
            "Expected Logarithmic Return"
            if kelly
            else "Expected Arithmetic Return"
        ),
        template="plotly_dark",
        height=height,
        width=width,
        hovermode="closest",
        legend=dict(
            x=0.01,
            y=0.99,
            xanchor="left",
            yanchor="top",
        ),
        margin=dict(l=80, r=100, t=80, b=70),
    )

    fig.update_xaxes(
        range=[xmin - xpad, xmax + xpad],
        tickformat=".2%",
        showgrid=True,
        griddash="dot",
    )

    fig.update_yaxes(
        range=[ymin - ypad, ymax + ypad],
        tickformat=".2%",
        showgrid=True,
        griddash="dot",
    )

    return fig
