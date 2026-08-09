from dash import Dash, dcc, html

from data_loader import load_data
from filters import get_filter_options
from callbacks import register_callbacks

# =========================
# Ð—ÐÐ“Ð Ð£Ð—ÐšÐ
# =========================

file_path = "t1_data.htm"

df = load_data(file_path)

# =========================
# Ð¡ÐŸÐ˜Ð¡ÐšÐ˜ Ð”Ð›Ð¯ Ð¤Ð˜Ð›Ð¬Ð¢Ð ÐžÐ’
# =========================

(
    pair_options,
    robo_type_options,
    robo_name_options
) = get_filter_options(df)

# =========================
# APP
# =========================

app = Dash(__name__)
server = app.server

button_style = {
    'backgroundColor': 'black',
    'color': 'white',
    'border': '1px solid black',
    'borderRadius': '4px',
    'padding': '10px 16px',
    'fontWeight': '600',
    'cursor': 'pointer',
    'whiteSpace': 'nowrap'
}

modal_button_style = {
    'backgroundColor': 'black',
    'color': 'white',
    'border': '1px solid black',
    'borderRadius': '4px',
    'padding': '8px 12px',
    'cursor': 'pointer'
}

modal_panel_style = {
    'backgroundColor': 'white',
    'border': '1px solid #d0d0d0',
    'borderRadius': '8px',
    'boxShadow': '0 12px 40px rgba(0,0,0,0.22)',
    'padding': '20px',
    'width': '900px',
    'maxWidth': '94vw',
    'maxHeight': '82vh',
    'overflowY': 'auto'
}

modal_overlay_style = {
    'display': 'none',
    'position': 'fixed',
    'top': '0',
    'left': '0',
    'right': '0',
    'bottom': '0',
    'zIndex': '1000',
    'backgroundColor': 'rgba(0,0,0,0.25)',
    'alignItems': 'center',
    'justifyContent': 'center'
}

app.layout = html.Div([

    dcc.Store(
        id='filter-values-store',
        data={
            'pair': ['ALL'],
            'robo_type': ['ALL'],
            'robo_name': ['ALL']
        }
    ),

    html.H2(
        "Forex Robot Performance Analysis",
        style={
            'width': '80%',
            'textAlign': 'center'
        }
    ),

    html.Div([

        html.Div([

            html.Div([

                html.Div([

                    dcc.DatePickerRange(
                        id='date-picker',
                        start_date=df['Close Time'].min().date(),
                        end_date=df['Close Time'].max().date(),
                        display_format='YYYY-MM-DD'
                    )

                ],
                style={
                    'width': '10%',
                    'minWidth': '220px'
                }),

                html.Div([

                    dcc.Dropdown(
                        id='pair-dropdown',
                        options=pair_options,
                        value=['ALL'],
                        clearable=False,
                        multi=True
                    )

                ],
                style={
                    'width': '10%',
                    'minWidth': '180px'
                }),

                html.Div([

                    dcc.Dropdown(
                        id='robo-type-dropdown',
                        options=robo_type_options,
                        value=['ALL'],
                        clearable=False,
                        multi=True
                    )

                ],
                style={
                    'width': '10%',
                    'minWidth': '180px'
                }),

                html.Div([

                    dcc.Dropdown(
                        id='robo-name-dropdown',
                        options=robo_name_options,
                        value=['ALL'],
                        clearable=False,
                        multi=True
                    )

                ],
                style={
                    'width': '10%',
                    'minWidth': '220px'
                })

            ],
            style={
                'display': 'flex',
                'flexDirection': 'row',
                'gap': '20px',
                'alignItems': 'center',
                'justifyContent': 'center',
                'flexWrap': 'wrap',
                'width': '100%'
            })

        ],
        style={
            'flex': '1'
        }),

        html.Div([

            html.Button(
                "Trade Summary",
                id='trade-summary-button',
                n_clicks=0,
                style=button_style
            ),

            html.Button(
                "Swap & Holding",
                id='swap-holding-button',
                n_clicks=0,
                style=button_style
            ),

            html.Button(
                "Trades",
                id='trades-button',
                n_clicks=0,
                style=button_style
            )

        ],
        style={
            'display': 'flex',
            'gap': '10px',
            'minWidth': '310px'
        }),

        html.Div([

            dcc.Dropdown(
                id='combo-metric-dropdown',
                options=[
                    {'label': 'Balance', 'value': 'Balance'},
                    {'label': 'Expected Payoff', 'value': 'Expected Payoff'},
                    {'label': 'Profit Factor', 'value': 'Profit Factor'}
                ],
                value='Balance',
                clearable=False
            )

        ],
        style={
            'width': '20%',
            'minWidth': '220px'
        })

    ],
    style={
        'display': 'flex',
        'flexDirection': 'row',
        'gap': '20px',
        'alignItems': 'center',
        'marginBottom': '20px',
        'flexWrap': 'wrap',
        'width': '100%'
    }),

    dcc.Graph(
        id='balance-chart',
        config={
            'responsive': True
        },
        style={
            'width': '100%',
            'height': '90vh'
        }
    ),

    html.Div(
        id='trade-summary-modal',
        children=[

            html.Div([

                html.Div([

                    html.H3(
                        "Trade Summary",
                        style={
                            'margin': '0',
                            'fontSize': '20px'
                        }
                    ),

                    html.Button(
                        "Close",
                        id='trade-summary-close',
                        n_clicks=0,
                        style=modal_button_style
                    )

                ],
                style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center',
                    'gap': '20px',
                    'marginBottom': '16px'
                }),

                html.Div(
                    id='trade-summary-content'
                )

            ],
            style={
                **modal_panel_style,
                'width': '760px',
                'maxHeight': '75vh'
            })

        ],
        style=modal_overlay_style
    ),

    html.Div(
        id='swap-holding-modal',
        children=[

            html.Div([

                html.Div([

                    html.H3(
                        "Swap & Holding Analysis",
                        style={
                            'margin': '0',
                            'fontSize': '20px'
                        }
                    ),

                    html.Button(
                        "Close",
                        id='swap-holding-close',
                        n_clicks=0,
                        style=modal_button_style
                    )

                ],
                style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center',
                    'gap': '20px',
                    'marginBottom': '16px'
                }),

                html.Div(
                    id='swap-holding-content'
                )

            ],
            style=modal_panel_style)

        ],
        style=modal_overlay_style
    ),

    html.Div(
        id='trades-modal',
        children=[

            html.Div([

                html.Div([

                    html.H3(
                        "Trades",
                        style={
                            'margin': '0',
                            'fontSize': '20px'
                        }
                    ),

                    html.Button(
                        "Close",
                        id='trades-close',
                        n_clicks=0,
                        style=modal_button_style
                    )

                ],
                style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center',
                    'gap': '20px',
                    'marginBottom': '16px'
                }),

                html.Div(
                    id='trades-content',
                    style={
                        'flex': '1',
                        'overflow': 'auto',
                        'minHeight': '0'
                    }
                )

            ],
            style={
                **modal_panel_style,
                'width': '95vw',
                'maxWidth': '1500px',
                'maxHeight': '75vh',
                'overflow': 'hidden',
                'display': 'flex',
                'flexDirection': 'column'
            })

        ],
        style=modal_overlay_style
    )

])

# =========================
# CALLBACK
# =========================

register_callbacks(app, df)

# =========================
# RUN
# =========================

if __name__ == '__main__':

    app.run(
        debug=True
    )
