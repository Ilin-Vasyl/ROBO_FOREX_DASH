from data_loader import load_data


def run_check(df):

    print("\n===== CHECK =====")

    print("Rows:", len(df))
    print("Robots:", df['Robo_Name'].nunique())

    print("\nNet_PL total:", round(df['Net_PL'].sum(), 2))

    print("\nBy Robo_Type:")
    print(
        df.groupby('Robo_Type')['Net_PL']
        .sum()
        .round(2)
        .to_string()
    )


def run_report(df):

    print("\n===== REPORT =====")

    report = df.groupby('Robo_Type').agg(
        trades=('Net_PL', 'count'),
        lots=('Size', 'sum'),
        net_pl=('Net_PL', 'sum')
    )

    # =========================
    # ROI per $1 invested
    # =========================

    report['roi_per_1usd'] = (
        report['net_pl'] / (report['lots'] * 100)
    )

    print(report.to_string())

    print("\n===== TOTAL =====")

    total_trades = len(df)
    total_lots = df['Size'].sum()
    total_net = df['Net_PL'].sum()

    print("Trades:", total_trades)
    print("Lots:", total_lots)
    print("Net PL:", total_net)

    total_roi = total_net / (total_lots * 100) if total_lots else 0

    print("ROI per $1 invested:", total_roi)


# =========================
# MAIN
# =========================

file_path = r"C:\Users\User\Desktop\Forex Tester\RoboAnalytics\t_data.htm"

df = load_data(file_path)

run_check(df)

run_report(df)