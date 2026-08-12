import pandas as pd

from analytics import (
    build_daily_and_balance,
    build_swap_holding_analysis,
    filter_trades
)
from chart import build_chart, build_swap_holding_chart
from dash import Input, Output, State, ctx, dash_table, dcc, html, no_update

from filters import get_dependent_filter_options


def get_zoom_range(relayout_data):

    if not relayout_data:
        return (
            None,
            None
        )

    if relayout_data.get('xaxis.autorange'):
        return (
            None,
            None
        )

    if 'xaxis.range[0]' in relayout_data and 'xaxis.range[1]' in relayout_data:
        return (
            pd.to_datetime(relayout_data['xaxis.range[0]']),
            pd.to_datetime(relayout_data['xaxis.range[1]'])
        )

    if 'xaxis.range' in relayout_data:
        return (
            pd.to_datetime(relayout_data['xaxis.range'][0]),
            pd.to_datetime(relayout_data['xaxis.range'][1])
        )

    return (
        None,
        None
    )


def normalize_multi_value(current_values, previous_values):

    current_values = current_values or []
    previous_values = previous_values or ['ALL']

    if not current_values:
        return ['ALL']

    current_set = set(current_values)
    previous_set = set(previous_values)

    all_was_added = (
        'ALL' in current_set and
        'ALL' not in previous_set
    )

    if all_was_added:
        return ['ALL']

    if 'ALL' in current_set and len(current_values) > 1:
        return [
            value
            for value in current_values
            if value != 'ALL'
        ]

    return current_values


def format_money(value):

    return f"{value:,.2f}"


def get_value_color(value):

    if value > 0:
        return '#0a7a28'

    if value < 0:
        return '#b00020'

    return '#333'


def build_summary_table(filtered, end_date):

    if filtered.empty:
        return html.Div(
            "No trades for selected filters.",
            style={
                'fontSize': '14px',
                'color': '#555'
            }
        )

    end_day = pd.to_datetime(end_date).normalize()
    end_datetime = (
        end_day +
        pd.Timedelta(days=1) -
        pd.Timedelta(seconds=1)
    )

    current_week_start = (
        end_day -
        pd.Timedelta(days=end_day.weekday())
    )

    current_month_start = end_day.replace(day=1)

    periods = [
        (
            'Last 6 days',
            end_day - pd.Timedelta(days=5)
        ),
        (
            'Last 3 weeks',
            current_week_start - pd.Timedelta(weeks=2)
        ),
        (
            'Last 3 months',
            current_month_start - pd.DateOffset(months=2)
        )
    ]

    order = [
        'Trend',
        'ContrTrend',
        'ContrTrend_M'
    ]

    robo_types = [
        robo_type
        for robo_type in order
        if robo_type in filtered['Robo_Type'].unique()
    ]

    rows = []

    for robo_type in robo_types:

        row_values = []

        for _, period_start in periods:

            period_df = filtered[
                (filtered['Close Time'] >= period_start) &
                (filtered['Close Time'] <= end_datetime)
            ]

            value = period_df[
                period_df['Robo_Type'] == robo_type
            ]['Net_PL'].sum()

            row_values.append(value)

        rows.append(
            (
                robo_type,
                row_values
            )
        )

    total_values = []

    for _, period_start in periods:

        period_df = filtered[
            (filtered['Close Time'] >= period_start) &
            (filtered['Close Time'] <= end_datetime)
        ]

        total_values.append(
            period_df['Net_PL'].sum()
        )

    rows.append(
        (
            'TOTAL',
            total_values
        )
    )

    return html.Table([

        html.Thead(
            html.Tr([
                html.Th(
                    'Strategy',
                    style={
                        'textAlign': 'left',
                        'padding': '10px',
                        'backgroundColor': 'black',
                        'color': 'white',
                        'borderBottom': '1px solid #d8d8d8'
                    }
                ),
                *[
                    html.Th(
                        label,
                        style={
                            'textAlign': 'right',
                            'padding': '10px',
                            'backgroundColor': 'black',
                            'color': 'white',
                            'borderBottom': '1px solid #d8d8d8'
                        }
                    )
                    for label, _ in periods
                ]
            ])
        ),

        html.Tbody([
            html.Tr([
                html.Td(
                    robo_type,
                    style={
                        'padding': '10px',
                        'fontWeight': '700' if robo_type == 'TOTAL' else '400',
                        'backgroundColor': '#f2f2f2' if robo_type == 'TOTAL' else 'white',
                        'borderBottom': '1px solid #eeeeee'
                    }
                ),
                *[
                    html.Td(
                        format_money(value),
                        style={
                            'padding': '10px',
                            'textAlign': 'right',
                            'fontWeight': '700' if robo_type == 'TOTAL' else '400',
                            'backgroundColor': '#f2f2f2' if robo_type == 'TOTAL' else 'white',
                            'color': get_value_color(value),
                            'borderBottom': '1px solid #eeeeee'
                        }
                    )
                    for value in values
                ]
            ])
            for robo_type, values in rows
        ])

    ],
    style={
        'width': '100%',
        'borderCollapse': 'collapse',
        'fontSize': '14px'
    })


def build_swap_holding_table(summary):

    if summary.empty:
        return html.Div(
            "No trades for selected filters.",
            style={
                'fontSize': '14px',
                'color': '#555'
            }
        )

    columns = [
        (
            'Robo_Type',
            'Strategy'
        ),
        (
            'Trades',
            'Trades'
        ),
        (
            'Net_PL',
            'Net P/L'
        ),
        (
            'Swap',
            'Swap'
        ),
        (
            'Net_PL_No_Swap',
            'Net P/L no swap'
        ),
        (
            'Avg_Holding_Days',
            'Avg hold days'
        ),
        (
            'Median_Holding_Days',
            'Median hold days'
        ),
        (
            'Avg_Swap',
            'Avg swap'
        ),
        (
            'Avg_Swap_Per_Day',
            'Avg swap/day'
        ),
        (
            'Swap_Impact_Pct',
            'Swap impact %'
        )
    ]

    def format_cell(column, value):

        if column in ['Robo_Type']:
            return value

        if column == 'Trades':
            return f"{int(value)}"

        if column == 'Swap_Impact_Pct':
            return f"{value:.2f}%"

        return format_money(value)

    return html.Table([

        html.Thead(
            html.Tr([
                html.Th(
                    label,
                    style={
                        'textAlign': 'right' if key != 'Robo_Type' else 'left',
                        'padding': '9px',
                        'backgroundColor': 'black',
                        'color': 'white',
                        'borderBottom': '1px solid #d8d8d8'
                    }
                )
                for key, label in columns
            ])
        ),

        html.Tbody([
            html.Tr([
                html.Td(
                    format_cell(key, row[key]),
                    style={
                        'padding': '9px',
                        'textAlign': 'right' if key != 'Robo_Type' else 'left',
                        'fontWeight': '700' if row['Robo_Type'] == 'TOTAL' else '400',
                        'backgroundColor': '#f2f2f2' if row['Robo_Type'] == 'TOTAL' else 'white',
                        'color': (
                            get_value_color(row[key])
                            if key in [
                                'Net_PL',
                                'Swap',
                                'Net_PL_No_Swap',
                                'Avg_Swap',
                                'Avg_Swap_Per_Day',
                                'Swap_Impact_Pct'
                            ]
                            else '#333'
                        ),
                        'borderBottom': '1px solid #eeeeee'
                    }
                )
                for key, _ in columns
            ])
            for _, row in summary.iterrows()
        ])

    ],
    style={
        'width': '100%',
        'borderCollapse': 'collapse',
        'fontSize': '13px',
        'marginBottom': '18px'
    })


def build_trades_table(filtered):

    if filtered.empty:
        return html.Div(
            "No trades for selected filters.",
            style={
                'fontSize': '14px',
                'color': '#555'
            }
        )

    display_df = filtered.drop(
        columns=[
            'Holding_Hours',
            'Holding_Days',
            'Net_PL_No_Swap',
            'Swap_Per_Day',
            'Swap_Share'
        ],
        errors='ignore'
    ).copy()

    for column in display_df.select_dtypes(
        include=['datetime', 'datetimetz']
    ).columns:
        display_df[column] = display_df[column].dt.strftime(
            '%Y-%m-%d %H:%M:%S'
        )

    for column, decimals in [
        ('Net_PL', 2),
        ('Holding_Days', 1)
    ]:
        if column in display_df.columns:
            display_df[column] = display_df[column].map(
                lambda value: round(value, decimals)
                if pd.notna(value)
                else None
            )

    column_widths = []

    for column in display_df.columns:
        value_width = display_df[column].fillna('').astype(str).str.len().max()
        width = max(len(column), value_width) + 2

        column_widths.append({
            'if': {
                'column_id': column
            },
            'minWidth': f'{width}ch',
            'width': f'{width}ch',
            'maxWidth': f'{width}ch'
        })

    return dash_table.DataTable(
        columns=[
            {
                'name': column,
                'id': column
            }
            for column in display_df.columns
        ],
        data=display_df.to_dict('records'),
        page_action='native',
        page_current=0,
        page_size=100,
        fixed_rows={'headers': True},
        style_table={
            'minWidth': '100%',
            'overflowX': 'auto'
        },
        style_header={
            'backgroundColor': 'black',
            'color': 'white',
            'fontWeight': 'bold',
            'padding': '9px',
            'textAlign': 'left',
            'whiteSpace': 'nowrap'
        },
        style_cell={
            'padding': '8px 9px',
            'textAlign': 'left',
            'whiteSpace': 'nowrap',
            'fontSize': '13px'
        },
        style_cell_conditional=column_widths,
        style_data={
            'borderBottom': '1px solid #eeeeee'
        }
    )


def register_callbacks(app, df):

    @app.callback(
        Output('pair-dropdown', 'options'),
        Output('robo-type-dropdown', 'options'),
        Output('robo-name-dropdown', 'options'),
        Output('pair-dropdown', 'value'),
        Output('robo-type-dropdown', 'value'),
        Output('robo-name-dropdown', 'value'),
        Output('filter-values-store', 'data'),
        Input('pair-dropdown', 'value'),
        Input('robo-type-dropdown', 'value'),
        Input('robo-name-dropdown', 'value'),
        State('filter-values-store', 'data')
    )
    def update_filter_options(
        selected_pair,
        selected_robo_type,
        selected_robo_name,
        previous_values
    ):

        previous_values = previous_values or {}

        selected_pair = normalize_multi_value(
            selected_pair,
            previous_values.get('pair')
        )

        selected_robo_type = normalize_multi_value(
            selected_robo_type,
            previous_values.get('robo_type')
        )

        selected_robo_name = normalize_multi_value(
            selected_robo_name,
            previous_values.get('robo_name')
        )

        (
            pair_options,
            robo_type_options,
            robo_name_options
        ) = get_dependent_filter_options(
            df,
            selected_pair,
            selected_robo_type,
            selected_robo_name
        )

        new_values = {
            'pair': selected_pair,
            'robo_type': selected_robo_type,
            'robo_name': selected_robo_name
        }

        return (
            pair_options,
            robo_type_options,
            robo_name_options,
            selected_pair,
            selected_robo_type,
            selected_robo_name,
            new_values
        )

    @app.callback(
        Output('date-picker', 'start_date'),
        Output('date-picker', 'end_date'),
        Input('balance-chart', 'relayoutData')
    )
    def update_date_picker_from_zoom(relayout_data):

        zoom_start, zoom_end = get_zoom_range(relayout_data)

        if zoom_start is None or zoom_end is None:

            if relayout_data and relayout_data.get('xaxis.autorange'):
                return (
                    df['Close Time'].min().date(),
                    df['Close Time'].max().date()
                )

            return (
                no_update,
                no_update
            )

        return (
            zoom_start.date(),
            zoom_end.date()
        )

    @app.callback(
        Output('balance-chart', 'figure'),
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('pair-dropdown', 'value'),
        Input('robo-type-dropdown', 'value'),
        Input('robo-name-dropdown', 'value'),
        Input('combo-metric-dropdown', 'value')
    )
    def update_chart(
        start_date,
        end_date,
        selected_pair,
        selected_robo_type,
        selected_robo_name,
        selected_combo_metric
    ):

        filtered, daily = build_daily_and_balance(
            df,
            start_date,
            end_date,
            selected_pair,
            selected_robo_type,
            selected_robo_name
        )

        return build_chart(
            filtered,
            daily,
            selected_pair,
            selected_combo_metric
        )

    @app.callback(
        Output('trade-summary-modal', 'style'),
        Output('trade-summary-content', 'children'),
        Input('trade-summary-button', 'n_clicks'),
        Input('trade-summary-close', 'n_clicks'),
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('pair-dropdown', 'value'),
        Input('robo-type-dropdown', 'value'),
        Input('robo-name-dropdown', 'value'),
        State('trade-summary-modal', 'style')
    )
    def update_trade_summary_modal(
        open_clicks,
        close_clicks,
        start_date,
        end_date,
        selected_pair,
        selected_robo_type,
        selected_robo_name,
        modal_style
    ):

        modal_style = dict(modal_style or {})

        triggered_id = ctx.triggered_id

        if triggered_id == 'trade-summary-close':
            modal_style['display'] = 'none'
            return (
                modal_style,
                no_update
            )

        if triggered_id == 'trade-summary-button':
            modal_style['display'] = 'flex'

        filtered, _ = build_daily_and_balance(
            df,
            start_date,
            end_date,
            selected_pair,
            selected_robo_type,
            selected_robo_name
        )

        content = build_summary_table(
            filtered,
            end_date
        )

        return (
            modal_style,
            content
        )

    @app.callback(
        Output('swap-holding-modal', 'style'),
        Output('swap-holding-content', 'children'),
        Input('swap-holding-button', 'n_clicks'),
        Input('swap-holding-close', 'n_clicks'),
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('pair-dropdown', 'value'),
        Input('robo-type-dropdown', 'value'),
        Input('robo-name-dropdown', 'value'),
        State('swap-holding-modal', 'style')
    )
    def update_swap_holding_modal(
        open_clicks,
        close_clicks,
        start_date,
        end_date,
        selected_pair,
        selected_robo_type,
        selected_robo_name,
        modal_style
    ):

        modal_style = dict(modal_style or {})

        triggered_id = ctx.triggered_id

        if triggered_id == 'swap-holding-close':
            modal_style['display'] = 'none'
            return (
                modal_style,
                no_update
            )

        if triggered_id == 'swap-holding-button':
            modal_style['display'] = 'flex'

        filtered, summary = build_swap_holding_analysis(
            df,
            start_date,
            end_date,
            selected_pair,
            selected_robo_type,
            selected_robo_name
        )

        content = html.Div([

            build_swap_holding_table(
                summary
            ),

            dcc.Graph(
                figure=build_swap_holding_chart(
                    filtered,
                    summary
                ),
                config={
                    'responsive': True
                },
                style={
                    'width': '100%'
                }
            )

        ])

        return (
            modal_style,
            content
        )

    @app.callback(
        Output('trades-modal', 'style'),
        Output('trades-content', 'children'),
        Input('trades-button', 'n_clicks'),
        Input('trades-close', 'n_clicks'),
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('pair-dropdown', 'value'),
        Input('robo-type-dropdown', 'value'),
        Input('robo-name-dropdown', 'value'),
        State('trades-modal', 'style')
    )
    def update_trades_modal(
        open_clicks,
        close_clicks,
        start_date,
        end_date,
        selected_pair,
        selected_robo_type,
        selected_robo_name,
        modal_style
    ):

        modal_style = dict(modal_style or {})

        if ctx.triggered_id == 'trades-close':
            modal_style['display'] = 'none'
            return (
                modal_style,
                no_update
            )

        if ctx.triggered_id == 'trades-button':
            modal_style['display'] = 'flex'

        filtered = filter_trades(
            df,
            start_date,
            end_date,
            selected_pair,
            selected_robo_type,
            selected_robo_name
        )

        return (
            modal_style,
            build_trades_table(filtered)
        )
