import pandas as pd

from filters import is_all_selected


def filter_trades(df,
                  start_date,
                  end_date,
                  selected_pair,
                  selected_robo_type,
                  selected_robo_name):

    start_date = pd.to_datetime(start_date)

    # Ð²ÐºÐ»ÑŽÑ‡Ð°ÐµÐ¼ Ð²ÐµÑÑŒ Ð¿Ð¾ÑÐ»ÐµÐ´Ð½Ð¸Ð¹ Ð´ÐµÐ½ÑŒ
    end_date = (
        pd.to_datetime(end_date)
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

    filtered = df[
        (df['Close Time'] >= start_date) &
        (df['Close Time'] <= end_date)
    ].copy()

    if not is_all_selected(selected_pair):
        filtered = filtered[
            filtered['Item'].isin(selected_pair)
        ]

    if not is_all_selected(selected_robo_type):
        filtered = filtered[
            filtered['Robo_Type'].isin(selected_robo_type)
        ]

    if not is_all_selected(selected_robo_name):
        filtered = filtered[
            filtered['Robo_Name'].isin(selected_robo_name)
        ]

    return filtered


def build_daily_and_balance(df,
                            start_date,
                            end_date,
                            selected_pair,
                            selected_robo_type,
                            selected_robo_name):

    filtered = filter_trades(
        df,
        start_date,
        end_date,
        selected_pair,
        selected_robo_type,
        selected_robo_name
    )

    if filtered.empty:
        return (
            filtered,
            filtered
        )

    # =========================
    # Ð‘Ð°Ð»Ð°Ð½Ñ Ð¿Ð¾ Ñ€ÐµÐ°Ð»ÑŒÐ½Ñ‹Ð¼ ÑÐ´ÐµÐ»ÐºÐ°Ð¼
    # =========================

    filtered = filtered.sort_values(
        'Close Time'
    )

    filtered['Balance'] = (
        filtered.groupby(
            'Robo_Type'
        )['Net_PL']
        .cumsum()
    )

    final_balance = (
        filtered.groupby(
            'Robo_Type'
        )['Balance']
        .last()
        .to_dict()
    )

    filtered['Robo_Label'] = (
        filtered['Robo_Type']
        .apply(
            lambda x:
            f"{x} ({final_balance.get(x, 0):.2f})"
        )
    )

    return (
        filtered,
        filtered
    )


def build_swap_holding_analysis(df,
                                start_date,
                                end_date,
                                selected_pair,
                                selected_robo_type,
                                selected_robo_name):

    filtered = filter_trades(
        df,
        start_date,
        end_date,
        selected_pair,
        selected_robo_type,
        selected_robo_name
    )

    if filtered.empty:
        return (
            filtered,
            pd.DataFrame()
        )

    filtered = filtered.copy()

    if 'Holding_Days' not in filtered.columns:
        filtered['Holding_Days'] = (
            filtered['Close Time'] - filtered['Open Time']
        ).dt.total_seconds() / 86400

    if 'Net_PL_No_Swap' not in filtered.columns:
        filtered['Net_PL_No_Swap'] = (
            filtered['Net_PL'] -
            filtered['Swap'].fillna(0)
        )

    if 'Swap_Per_Day' not in filtered.columns:
        filtered['Swap_Per_Day'] = (
            filtered['Swap'].fillna(0) /
            filtered['Holding_Days'].where(filtered['Holding_Days'] > 0)
        ).fillna(0)

    summary = (
        filtered
        .groupby(
            'Robo_Type',
            as_index=False
        )
        .agg(
            Trades=('Net_PL', 'count'),
            Net_PL=('Net_PL', 'sum'),
            Swap=('Swap', 'sum'),
            Net_PL_No_Swap=('Net_PL_No_Swap', 'sum'),
            Avg_Holding_Days=('Holding_Days', 'mean'),
            Median_Holding_Days=('Holding_Days', 'median'),
            Avg_Swap=('Swap', 'mean'),
            Avg_Swap_Per_Day=('Swap_Per_Day', 'mean')
        )
    )

    summary['Swap_Impact_Pct'] = (
        summary['Swap'] /
        summary['Net_PL'].abs().where(summary['Net_PL'].abs() > 0) *
        100
    ).fillna(0)

    total = pd.DataFrame([{
        'Robo_Type': 'TOTAL',
        'Trades': filtered['Net_PL'].count(),
        'Net_PL': filtered['Net_PL'].sum(),
        'Swap': filtered['Swap'].sum(),
        'Net_PL_No_Swap': filtered['Net_PL_No_Swap'].sum(),
        'Avg_Holding_Days': filtered['Holding_Days'].mean(),
        'Median_Holding_Days': filtered['Holding_Days'].median(),
        'Avg_Swap': filtered['Swap'].mean(),
        'Avg_Swap_Per_Day': filtered['Swap_Per_Day'].mean()
    }])

    total['Swap_Impact_Pct'] = (
        total['Swap'] /
        total['Net_PL'].abs().where(total['Net_PL'].abs() > 0) *
        100
    ).fillna(0)

    order = [
        'Trend',
        'ContrTrend',
        'ContrTrend_M'
    ]

    summary['Sort_Order'] = summary['Robo_Type'].apply(
        lambda value:
        order.index(value)
        if value in order
        else len(order)
    )

    summary = (
        summary
        .sort_values('Sort_Order')
        .drop(columns=['Sort_Order'])
    )

    summary = pd.concat(
        [
            summary,
            total
        ],
        ignore_index=True
    )

    return (
        filtered,
        summary
    )

