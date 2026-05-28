from analytics import build_daily_and_balance
from chart import build_chart
from dash import Input, Output

from filters import get_dependent_filter_options


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