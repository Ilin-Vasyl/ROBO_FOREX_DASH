import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def get_streaks(df):

    max_loss_run = 0
    max_win_run = 0

    max_loss_sum = 0
    max_win_sum = 0

    curr_loss = 0
    curr_win = 0

    curr_loss_sum = 0
    curr_win_sum = 0

    for pl in df['Net_PL']:

        if pl > 0:

            curr_win += 1
            curr_loss = 0

            curr_win_sum += pl
            curr_loss_sum = 0

        elif pl < 0:

            curr_loss += 1
            curr_win = 0

            curr_loss_sum += pl
            curr_win_sum = 0

        else:

            curr_win = 0
            curr_loss = 0

            curr_win_sum = 0
            curr_loss_sum = 0

        max_win_run = max(max_win_run, curr_win)
        max_loss_run = max(max_loss_run, curr_loss)

        max_win_sum = max(max_win_sum, curr_win_sum)
        max_loss_sum = min(max_loss_sum, curr_loss_sum)

    return (
        max_loss_run,
        max_win_run,
        round(max_loss_sum, 2),
        round(max_win_sum, 2)
    )


def get_value_color(value):

    if value > 0:
        return "#0a7a28"

    if value < 0:
        return "#b00020"

    return "#333"


def build_chart(filtered, daily, selected_pair, selected_combo_metric):

    stats_daily = daily.groupby('Robo_Type').agg(
        net_pl=('Net_PL', 'sum'),
        win_rate=('Net_PL', lambda x: (x > 0).mean() * 100),
        gross_profit=('Net_PL', lambda x: x[x > 0].sum()),
        gross_loss=('Net_PL', lambda x: x[x < 0].sum()),
        total_volume=('Size', 'sum')
    )

    stats_trades = filtered.groupby('Robo_Type').agg(
        trades=('Net_PL', 'count')
    )

    stats = stats_daily.join(stats_trades)

    combo_stats = (
        filtered
        .groupby(
            ['Item', 'Robo_Type'],
            as_index=False
        )
        .agg(
            Balance=('Net_PL', 'sum'),
            total_volume=('Size', 'sum'),
            gross_profit=('Net_PL', lambda x: x[x > 0].sum()),
            gross_loss=('Net_PL', lambda x: x[x < 0].sum())
        )
    )

    combo_stats['Expected Payoff'] = combo_stats.apply(
        lambda row:
        row['Balance'] / (row['total_volume'] * 100)
        if row['total_volume'] != 0 else 0,
        axis=1
    )

    combo_stats['Profit Factor'] = combo_stats.apply(
        lambda row:
        row['gross_profit'] / abs(row['gross_loss'])
        if row['gross_loss'] != 0 else 0,
        axis=1
    )

    best_combos = combo_stats.sort_values(
        selected_combo_metric,
        ascending=False
    ).head(3)

    worst_combos = combo_stats.sort_values(
        selected_combo_metric,
        ascending=True
    ).head(3)

    order = ["Trend", "ContrTrend", "ContrTrend_M"]
    robo_types = [r for r in order if r in stats.index]

    roi_vals = []
    profit_factor_vals = []

    max_loss_run_vals = []
    max_win_run_vals = []

    max_loss_sum_vals = []
    max_win_sum_vals = []

    best_trade_vals = []
    worst_trade_vals = []

    for r in robo_types:

        row = stats.loc[r]

        net = row['net_pl']
        vol = row['total_volume']
        gp = row['gross_profit']
        gl = row['gross_loss']

        roi_vals.append(
            round(net / (vol * 100), 4)
            if vol != 0 else 0
        )

        profit_factor_vals.append(
            round(gp / abs(gl), 2)
            if gl != 0 else 0
        )

        df_sub = filtered[filtered['Robo_Type'] == r]

        (
            loss_run,
            win_run,
            loss_sum,
            win_sum
        ) = get_streaks(df_sub)

        max_loss_run_vals.append(loss_run)
        max_win_run_vals.append(win_run)

        max_loss_sum_vals.append(loss_sum)
        max_win_sum_vals.append(win_sum)

        best_trade_vals.append(
            round(df_sub['Net_PL'].max(), 2)
            if len(df_sub) else 0
        )

        worst_trade_vals.append(
            round(df_sub['Net_PL'].min(), 2)
            if len(df_sub) else 0
        )

    balance_vals = [round(stats.loc[r, 'net_pl'], 2) for r in robo_types]
    win_rate_vals = [round(stats.loc[r, 'win_rate'], 2) for r in robo_types]
    trade_vals = [stats.loc[r, 'trades'] for r in robo_types]
    volume_vals = [round(stats.loc[r, 'total_volume'], 2) for r in robo_types]

    total_net = stats['net_pl'].sum()
    total_trades = stats['trades'].sum()
    total_volume = stats['total_volume'].sum()

    total_win_rate = (
        (daily['Net_PL'] > 0).sum()
        / len(daily) * 100
        if len(daily) != 0 else 0
    )

    total_gross_profit = stats['gross_profit'].sum()
    total_gross_loss = stats['gross_loss'].sum()

    total_profit_factor = (
        total_gross_profit / abs(total_gross_loss)
        if total_gross_loss != 0
        else 0
    )

    total_roi = (
        total_net / (total_volume * 100)
        if total_volume != 0 else 0
    )

    (
        total_loss_run,
        total_win_run,
        total_loss_sum,
        total_win_sum
    ) = get_streaks(filtered)

    table_robo_types = robo_types + ["TOTAL"]

    balance_vals.append(round(total_net, 2))
    win_rate_vals.append(round(total_win_rate, 2))
    trade_vals.append(total_trades)
    volume_vals.append(round(total_volume, 2))
    roi_vals.append(round(total_roi, 4))
    profit_factor_vals.append(round(total_profit_factor, 2))

    max_loss_run_vals.append(total_loss_run)
    max_win_run_vals.append(total_win_run)

    max_loss_sum_vals.append(total_loss_sum)
    max_win_sum_vals.append(total_win_sum)

    best_trade_vals.append(
        round(filtered['Net_PL'].max(), 2)
        if len(filtered) else 0
    )

    worst_trade_vals.append(
        round(filtered['Net_PL'].min(), 2)
        if len(filtered) else 0
    )

    roi_vals = [round(x, 2) for x in roi_vals]

    daily = daily.copy()
    daily['Robo_Name'] = daily['Robo_Type']

    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.75, 0.25],
        vertical_spacing=0.08,
        specs=[[{"type": "xy"}], [{"type": "table"}]]
    )

    fig.update_layout(
        legend=dict(
            x=1.02,
            y=1,
            xanchor="left",
            yanchor="top"
        )
    )

    all_x = []
    all_y = []

    if len(filtered) != 0:
        chart_end_date = pd.to_datetime(
            filtered['Close_Date']
        ).max()
    else:
        chart_end_date = None

    for name in robo_types:

        df_sub = daily[daily['Robo_Name'] == name].copy()
        df_sub = df_sub.sort_values('Close_Date')

        df_curve = df_sub.groupby(
            'Close_Date',
            as_index=False
        )['Net_PL'].sum()

        df_curve['Close_Date'] = pd.to_datetime(
            df_curve['Close_Date']
        )

        if len(df_curve) == 0:
            continue

        date_index = pd.date_range(
            start=df_curve['Close_Date'].min(),
            end=chart_end_date,
            freq='D'
        )

        df_curve = (
            df_curve
            .set_index('Close_Date')
            .reindex(date_index, fill_value=0)
            .rename_axis('Close_Date')
            .reset_index()
        )

        df_curve['Balance'] = df_curve['Net_PL'].cumsum()

        all_x.extend(df_curve['Close_Date'].tolist())
        all_y.extend(df_curve['Balance'].tolist())

        fig.add_trace(
            go.Scatter(
                x=df_curve['Close_Date'],
                y=df_curve['Balance'],
                mode='lines',
                name=name
            ),
            row=1,
            col=1
        )

    df_total = filtered.copy().sort_values('Close_Date')

    df_total_curve = df_total.groupby(
        'Close_Date',
        as_index=False
    )['Net_PL'].sum()

    df_total_curve['Close_Date'] = pd.to_datetime(
        df_total_curve['Close_Date']
    )

    if len(df_total_curve) != 0:

        total_date_index = pd.date_range(
            start=df_total_curve['Close_Date'].min(),
            end=chart_end_date,
            freq='D'
        )

        df_total_curve = (
            df_total_curve
            .set_index('Close_Date')
            .reindex(total_date_index, fill_value=0)
            .rename_axis('Close_Date')
            .reset_index()
        )

        df_total_curve['Balance'] = df_total_curve['Net_PL'].cumsum()

        all_x.extend(df_total_curve['Close_Date'].tolist())
        all_y.extend(df_total_curve['Balance'].tolist())

        fig.add_trace(
            go.Scatter(
                x=df_total_curve['Close_Date'],
                y=df_total_curve['Balance'],
                mode='lines',
                name='TOTAL EQUITY',
                line=dict(color='black', dash='dash', width=2)
            ),
            row=1,
            col=1
        )

    legend_info = [
        '',
        'Deposit: 3000,00 USD',
        'Trading leverage: 1:1000',
        'Server: NMarkets-Demo - NMarkets Limited',
        'Login: 511285',
        'Investor Password: 855660',
        '',
        f'BEST 3 BY {selected_combo_metric.upper()}',
    ]

    for _, row in best_combos.iterrows():

        legend_info.append(
            (
                f"{row['Item']} | "
                f"{row['Robo_Type']} | "
                f"{row[selected_combo_metric]:.2f}"
            )
        )

    legend_info.append('')
    legend_info.append(f'WORST 3 BY {selected_combo_metric.upper()}')

    for _, row in worst_combos.iterrows():

        legend_info.append(
            (
                f"{row['Item']} | "
                f"{row['Robo_Type']} | "
                f"{row[selected_combo_metric]:.2f}"
            )
        )

    for info in legend_info:

        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode='lines',
                name=info,
                showlegend=True,
                line=dict(
                    color='rgba(0,0,0,0)'
                )
            ),
            row=1,
            col=1
        )

    if len(all_x) == 0 or len(all_y) == 0:
        return fig

    y_min = min(all_y)
    y_max = max(all_y)

    x_min = min(all_x)
    x_max = max(all_x)

    y_pad = (y_max - y_min) * 0.08 if y_max != y_min else 1
    x_pad = pd.Timedelta(days=3)

    fig.update_yaxes(
        range=[y_min - y_pad, y_max + y_pad],
        row=1,
        col=1
    )

    fig.update_xaxes(
        range=[x_min - x_pad, x_max + x_pad],
        row=1,
        col=1
    )

    table_fill_colors = [
        [
            "#f2f2f2" if robo_type == "TOTAL" else "white"
            for robo_type in table_robo_types
        ]
        for _ in range(13)
    ]

    table_font_colors = [
        [
            "black"
            for _ in table_robo_types
        ],
        [
            get_value_color(value)
            for value in balance_vals
        ],
        [
            "black"
            for _ in table_robo_types
        ],
        [
            "black"
            for _ in table_robo_types
        ],
        [
            "black"
            for _ in table_robo_types
        ],
        [
            get_value_color(value)
            for value in roi_vals
        ],
        [
            "#0a7a28" if value > 1 else "#b00020" if value < 1 else "#333"
            for value in profit_factor_vals
        ],
        [
            "black"
            for _ in table_robo_types
        ],
        [
            "black"
            for _ in table_robo_types
        ],
        [
            get_value_color(value)
            for value in max_loss_sum_vals
        ],
        [
            get_value_color(value)
            for value in max_win_sum_vals
        ],
        [
            get_value_color(value)
            for value in best_trade_vals
        ],
        [
            get_value_color(value)
            for value in worst_trade_vals
        ]
    ]

    fig.add_trace(
        go.Table(
            header=dict(
                values=[
                    "Robo_Type",
                    "Balance",
                    "Profit Trades (% of total)",
                    "Trades",
                    "Volume (Lots)",
                    "Expected Payoff",
                    "Profit Factor",
                    "Max Loss Trade Run",
                    "Max Win Trade Run",
                    "Max.consecutive Loss($)",
                    "Max.consecutive Wins($)",
                    "Largest Profit Trade",
                    "Largest Loss Trade"
                ],
                fill_color="black",
                font=dict(
                    color="white",
                    size=11
                ),
                align="center"
            ),
            cells=dict(
                values=[
                    table_robo_types,
                    balance_vals,
                    win_rate_vals,
                    trade_vals,
                    volume_vals,
                    roi_vals,
                    profit_factor_vals,
                    max_loss_run_vals,
                    max_win_run_vals,
                    max_loss_sum_vals,
                    max_win_sum_vals,
                    best_trade_vals,
                    worst_trade_vals
                ],
                fill_color=table_fill_colors,
                font=dict(
                    color=table_font_colors,
                    size=11
                ),
                align="center"
            )
        ),
        row=2,
        col=1
    )

    fig.add_shape(
        type="line",
        x0=pd.to_datetime("2026-02-26"),
        x1=pd.to_datetime("2026-02-26"),
        y0=0,
        y1=1,
        xref="x",
        yref="y domain",
        line=dict(
            color="yellow",
            width=2,
            dash="dash"
        ),
        layer="above"
    )

    return fig