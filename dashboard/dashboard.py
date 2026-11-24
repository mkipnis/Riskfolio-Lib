# Copyright (c) Mike Kipnis - RiskFolio - Dashboard
import json
import os

import dash
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import pandas as pd
from dash_bootstrap_templates import load_figure_template
from dash import html, dcc, Input, Output

from components.PortfolioPanel import PortfolioPanel
from components.ReturnsPanel import ReturnsPanel

# =============================
# Dash App Initialization
# =============================
app = dash.Dash(
    __name__,
    title="Riskfolio - Dashboard",
    external_stylesheets=[dag.themes.BASE, dag.themes.BALHAM, dbc.themes.SUPERHERO],
    eager_loading=True
)

# Load Plotly template
load_figure_template("sandstone_dark")

server = app.server  # Gunicorn expects this

# Path to css folder
CSS_FOLDER = "css"

# Dynamically include all CSS files in assets/
css_files = [
    f for f in os.listdir(CSS_FOLDER) if f.endswith(".css")
]

# Instantiate your analytics layout
portfolio_panel = PortfolioPanel(app)
returns_panel = ReturnsPanel(app)

# Wrap layout to include all CSS assets explicitly
app.layout = html.Div(
    [
        # Dynamically add all CSS files with cache-busting
        *[html.Link(href=app.get_asset_url(f) + "?v=2", rel="stylesheet") for f in css_files],

        # Original layout
        portfolio_panel.layout(),
        returns_panel.layout(),
        dcc.Store(id="portfolio-components"),
        dcc.Store(id="portfolio-returns"),
        dcc.Store(id="portfolio-returns-matrix", storage_type="memory"),
        dcc.Interval(id="startup", n_intervals=0, max_intervals=1),
    ]
)


# =============================
# Callbacks
# =============================
@app.callback(
    Output("portfolio-components", "data"),
    Output("portfolio-returns", "data"),
    Input("startup", "n_intervals"),
)
def setup_dashboard(_):
    debug_messages = []
    underlying_symbol_data = []
    risk_free_rates = []

    try:

        with open("data/portfolio_components.json", "r") as sector_file:
            portfolio_components = json.load(sector_file)

        with open("data/hist_prices.json", "r") as hist_price_file:
            hist_prices = json.load(hist_price_file)

    except Exception as e:
        debug_messages.append(f"Error: {str(e)}")

    return portfolio_components, hist_prices


# =============================
# Local Development
# =============================
if __name__ == "__main__":
    host = os.getenv("DASH_HOST", "127.0.0.1")
    port = int(os.getenv("DASH_PORT", "8050"))
    debug = os.getenv("DASH_DEBUG", "true").lower() == "true"

    app.run(host=host, port=port, debug=debug)