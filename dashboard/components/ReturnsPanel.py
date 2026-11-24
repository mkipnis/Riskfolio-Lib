
# Copyright (c) Mike Kipnis - RiskFolio - Dashboard

import dash
import dash_ag_grid as dag
import pandas as pd
from dash import Input, Output, html


class ReturnsPanel:

    def __init__(self, app: dash.Dash):
        self.app = app
        self.returns_grid = "returns-grid"

        self.grid = dag.AgGrid(
            id=self.returns_grid,
            columnDefs=[],
            rowData=[],
            dashGridOptions={
                "rowSelection": "single",
                "theme": "legacy"
            },
            defaultColDef={
                "flex": 1,
                "minWidth": 80,
                "resizable": True,
                "sortable": True,
                "filter": True,
            },
            style={"height": "80vh", "width": "100%"},
            className="ag-theme-balham-dark"
        )

        self._register_callbacks()

    def layout(self):
        return html.Div([self.grid])

    def _register_callbacks(self):

        @self.app.callback(
            Output(self.returns_grid, "columnDefs"),
            Output(self.returns_grid, "rowData"),
            Output("portfolio-returns-matrix", "data"),
            Input("portfolio-returns", "data"),
            prevent_initial_call=True
        )
        def on_data_ready(hist_prices):

            if not hist_prices:
                return [], [], {}

            df = pd.DataFrame(hist_prices)

            df["close"] = pd.to_numeric(df["close"], errors="coerce")

            df["price_date"] = pd.to_datetime(
                df["price_date"].astype(str),
                format="%Y%m%d"
            )

            prices = (
                df.pivot(
                    index="price_date",
                    columns="symbol",
                    values="close"
                )
                .sort_index()
            )

            Y = prices.pct_change().dropna(how="all")

            grid_df = Y.reset_index()

            returns_json = Y.to_json(
                orient="split",
                date_format="iso"
            )

            grid_df["price_date"] = (
                grid_df["price_date"].dt.strftime("%Y-%m-%d")
            )

            column_defs = []

            for col in grid_df.columns:

                col_def = {
                    "headerName": col,
                    "field": col,
                    "sortable": True,
                    "filter": True,
                    "resizable": True,
                }

                if col != "price_date":
                    col_def["type"] = "numericColumn"
                    col_def["valueFormatter"] = {
                        "function": "d3.format('.2%')(params.value)"
                    }

                column_defs.append(col_def)

            rows = grid_df.to_dict("records")

            return column_defs, rows, returns_json
