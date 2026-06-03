import pandas as pd

from analytics import build_daily_and_balance
from chart import build_chart
from dash import Input, Output, no_update

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


def register_callbacks(app, df):

    @app.callback(
        Output('pair-dropdown', 'options'),
        Output('robo-type-dropdown', 'options'),
        Output('robo-name-dropdown', 'options'),
        Input('pair-dropdown', 'value'),
        Input('robo-type-dropdown', 'value'),
        Input('robo-name-dropdown', 'value')
    )
    def update_filter_options(
        selected_pair,
        selected_robo_type,
        selected_robo_name
    ):

        return get_dependent_filter_options(
            df,
            selected_pair,
            selected_robo_type,
            selected_robo_name
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