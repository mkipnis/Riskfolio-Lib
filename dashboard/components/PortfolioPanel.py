# Copyright (c) Mike Kipnis - RiskFolio - Dashboard

import copy

import dash
import dash_ag_grid as dag
from dash import Input, Output, State
from dash import dcc, html
from dash import callback_context as ctx


class PortfolioPanel(object):

    def __init__(self, app: dash.Dash):
        self.app = app

        self.portfolio_grid = "portfolio-grid"

        self.grid = dag.AgGrid(
            id=self.portfolio_grid,
            columnDefs=[
                {
                    "headerName": "Symbol",
                    "field": "symbol",
                    "cellStyle": {"textAlign": "left"},
                },
                {
                    "headerName": "Name",
                    "field": "name",
                    "cellClass": "text-left",
                    "hide": True
                },
                {
                    "headerName": "Sector",
                    "field": "sector",
                    "editable": True,
                    "cellClass": "text-right"
                }

            ],
            rowData=[],
            dashGridOptions={
                "rowSelection": "single",
                "theme": "legacy"
            },

            # 🟦 GLOBAL cellStyle applied to all cells
            defaultColDef={
                "flex": 1,
                "minWidth": 80,
                "resizable": False,
            },

            # ✅ style must be a dict, not a string
            style={"height": "80vh", "width": "100%"},

            className="ag-theme-balham-dark"

        )

        self._register_callbacks()

    def layout(self):
        return html.Div(
            [
                self.grid
            ]
        )


    def _register_callbacks(self):
        @self.app.callback(
            Output(self.portfolio_grid, "rowData"),
            Output(self.portfolio_grid, "selectedRows"),
            Input("portfolio-components", "data"),
            prevent_initial_call=True
        )
        def on_data_ready(market_data):
            if not market_data:
                return [], []

            return market_data, [market_data[0]]