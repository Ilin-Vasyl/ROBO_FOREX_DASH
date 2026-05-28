from dash import Dash, dcc, html



from data_loader import load_data
from filters import get_filter_options
from callbacks import register_callbacks

# =========================
# ЗАГРУЗКА
# =========================

file_path = "t1_data.htm"

df = load_data(file_path)


# =========================
# СПИСКИ ДЛЯ ФИЛЬТРОВ
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

app.layout = html.Div([

    html.H2(
        "Forex Robot Performance Analysis",
        style={
            'width':'80%',
            'textAlign':'center'
        }
    ),

    html.Div([

        html.Div([

            html.Div([

                html.Div([

                    dcc.DatePickerRange(

                        id='date-picker',

                        start_date=
                        df['Close Time']
                        .min()
                        .date(),

                        end_date=
                        df['Close Time']
                        .max()
                        .date(),

                        display_format=
                        'YYYY-MM-DD'

                    )

                ],
                style={
                    'width':'10%',
                    'minWidth':'220px'
                }),

                html.Div([

                    dcc.Dropdown(

                        id='pair-dropdown',
                        options=pair_options,
                        value='ALL',
                        clearable=False

                    )

                ],
                style={
                    'width':'10%',
                    'minWidth':'180px'
                }),

                html.Div([

                    dcc.Dropdown(

                        id='robo-type-dropdown',
                        options=robo_type_options,
                        value='ALL',
                        clearable=False

                    )

                ],
                style={
                    'width':'10%',
                    'minWidth':'180px'
                }),

                html.Div([

                    dcc.Dropdown(

                        id='robo-name-dropdown',
                        options=robo_name_options,
                        value='ALL',
                        clearable=False

                    )

                ],
                style={
                    'width':'10%',
                    'minWidth':'220px'
                })

            ],
            style={
                'display':'flex',
                'flexDirection':'row',
                'gap':'20px',
                'alignItems':'center',
                'justifyContent':'center',
                'flexWrap':'wrap',
                'width':'100%'
            })

        ],
        style={
            'flex':'1'
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
            'width':'20%',
            'minWidth':'220px'
        })

    ],

    style={

        'display':'flex',
        'flexDirection':'row',
        'gap':'20px',
        'alignItems':'center',
        'marginBottom':'20px',
        'flexWrap':'wrap',
        'width':'100%'

    }),

    dcc.Graph(
        id='balance-chart',
        config={
            'responsive': True
        },
        style={
            'width':'100%',
            'height':'90vh'
        }
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