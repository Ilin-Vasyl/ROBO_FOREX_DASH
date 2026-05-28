import pandas as pd


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

    if selected_pair != 'ALL':
        filtered = filtered[
            filtered['Item'] == selected_pair
        ]

    if selected_robo_type != 'ALL':
        filtered = filtered[
            filtered['Robo_Type'] == selected_robo_type
        ]

    if selected_robo_name != 'ALL':
        filtered = filtered[
            filtered['Robo_Name'] == selected_robo_name
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
            f"{x} ({final_balance.get(x,0):.2f})"
        )
    )

    return (
        filtered,
        filtered
    )