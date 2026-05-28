def run_check(df):

    print("\n===== CHECK =====")

    print(
        "Сделок:",
        len(df)
    )

    print(
        "Роботов:",
        df['Robo_Name'].nunique()
    )

    print(
        "\nNet_PL total:",
        round(df['Net_PL'].sum(), 2)
    )

    # =========================
    # ИТОГОВЫЙ БАЛАНС (EQUITY)
    # =========================

    df_sorted = df.sort_values('Close Time')

    equity = df_sorted['Net_PL'].cumsum().iloc[-1]

    print(
        "Итоговый баланс:",
        round(equity, 2)
    )

    print("\nПо типам:")

    print(
        df.groupby('Robo_Type')['Net_PL']
        .sum()
        .round(2)
        .to_string()
    )

    print("\n===== FIRST 3 ROWS =====")

    print(
        df.head(3)
        .to_string(index=False)
    )

    print("\n===== LAST 3 ROWS =====")

    print(
        df.tail(3)
        .to_string(index=False)
    )

