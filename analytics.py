import pandas as pd


def is_all_selected(selected_values):

    return (
        not selected_values or
        'ALL' in selected_values
    )


def build_daily_and_balance(df,
                            start_date,
                            end_date,
                            selected_pair,
                            selected_robo_type,
                            selected_robo_name):

    start_date = pd.to_datetime(start_date)

    # включаем весь последний день
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

    if filtered.empty:
        return (
            filtered,
            filtered
        )

    # =========================
    # Баланс по реальным сделкам
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

    filtered['Robo_Name'] = (
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