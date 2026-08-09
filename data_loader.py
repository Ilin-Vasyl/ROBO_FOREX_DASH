import pandas as pd


def load_data(file_path):

    tables = pd.read_html(file_path)

    df = None

    # =========================
    # НАХОДИМ БЛОК Closed Transactions -> Open Trades
    # =========================

    for table in tables:

        table = table.copy()

        start_idx = None
        end_idx = None

        for i in range(len(table)):

            row_text = " ".join(
                table.iloc[i]
                .astype(str)
                .fillna("")
                .values
            )

            if "Closed Transactions:" in row_text:
                start_idx = i

            if "Open Trades:" in row_text:
                end_idx = i
                break

        if start_idx is not None:

            if end_idx is None:
                end_idx = len(table)

            df = table.iloc[
                start_idx + 1:end_idx
            ].reset_index(drop=True)

            break

    if df is None:
        raise ValueError(
            "Блок Closed Transactions не найден"
        )

    # =========================
    # HEADER
    # =========================

    df.columns = df.iloc[0]
    df = df[2:].reset_index(drop=True)
    df = df.iloc[:-2]

    df['Robo_Name'] = ""

    # =========================
    # УНИФИКАЦИЯ PRICE
    # =========================

    df.columns = [str(c).strip() for c in df.columns]

    cols = list(df.columns)

    price_count = 0
    new_cols = []

    for col in cols:

        if col == "Price":

            price_count += 1

            if price_count == 1:
                new_cols.append("Open_Price")

            elif price_count == 2:
                new_cols.append("Close_Price")

            else:
                new_cols.append(f"Price_{price_count}")

        else:
            new_cols.append(col)

    df.columns = new_cols

    # =========================
    # ПЕРЕНОС ROBO_NAME
    # =========================

    for i in range(1, len(df)):

        row = df.loc[i].astype(str)

        ticket = str(row['Ticket']).strip()

        is_trade = (
            ticket != "" and
            ticket.lower() != "nan" and
            ticket.replace('.', '', 1).isdigit()
        )

        if not is_trade:

            robo_name = None

            for v in reversed(row.values):

                v = str(v).strip()

                if v and v != "nan":
                    robo_name = v
                    break

            if robo_name:

                df.loc[i - 1, 'Robo_Name'] = robo_name

    df.columns = [
        str(c).strip()
        for c in df.columns
    ]

    # =========================
    # ТИПЫ ДАННЫХ
    # =========================

    df['Ticket'] = pd.to_numeric(
        df['Ticket'],
        errors='coerce'
    )

    df = df[
        df['Ticket'].notna()
    ].reset_index(drop=True)

    df['Ticket'] = df['Ticket'].astype('int64')

    df['Open_Price'] = pd.to_numeric(
        df['Open_Price'],
        errors='coerce'
    )

    df['Close_Price'] = pd.to_numeric(
        df['Close_Price'],
        errors='coerce'
    )

    df['Profit'] = pd.to_numeric(
        df['Profit'],
        errors='coerce'
    )

    df['Size'] = pd.to_numeric(
        df['Size'],
        errors='coerce'
    )

    df['Swap'] = pd.to_numeric(
        df['Swap'],
        errors='coerce'
    )

    df['Commission'] = pd.to_numeric(
        df['Commission'],
        errors='coerce'
    )

    df['Open Time'] = pd.to_datetime(
        df['Open Time']
    )

    df['Close Time'] = pd.to_datetime(
        df['Close Time']
    )

    df = df.drop(
        columns=['Taxes'],
        errors='ignore'
    )

    df['Robo_Name'] = df['Robo_Name'].str.replace(
        r'^(Sell by |Buy by )',
        '',
        regex=True
    )

    # =========================
    # ИСПРАВЛЕНИЯ ROBO NAMES
    # =========================

    fixes = {

        ('0_AUD_JPY_1', 'nzdjpy.mm'): '0_NZD_JPY_1',
        ('0_NZD_USD', 'gbpusd.mm'): '0_GBP_USD',
        ('RA_', 'eurjpy.mm'): 'RA_EUR_JPY',
        ('R_', 'eurjpy.mm'): 'R_EUR_JPY',
        ('R_', 'audjpy.mm'): 'R_AUD_JPY',
        ('0_GBP_USD_1', 'eurusd.mm'): '0_EUR_USD_1',
        ('R_GBP_USD', 'gbpjpy.mm'): 'R_GBP_JPY',
        ('Reversed Sell', 'audusd.mm'): 'R_AUD_USD',
        ('RA_USD_JPY', 'eurusd.mm'): 'RA_EUR_USD',
        ('R_USD_JPY_2', 'eurusd.mm'): 'R_EUR_USD',
        ('R_M_EUR_GBP', 'gbpusd.mm'): 'R_M_GBP_USD'
    }

    for (robo, item), new_name in fixes.items():

        mask = (
            (df['Robo_Name'] == robo) &
            (df['Item'] == item)
        )

        df.loc[mask, 'Robo_Name'] = new_name

    # =========================
    # ТИПЫ РОБОТОВ
    # =========================

    df['Robo_Type'] = ""

    df.loc[
        df['Robo_Name'].str.startswith('R_M_'),
        'Robo_Type'
    ] = 'ContrTrend_M'

    df.loc[
        df['Robo_Name'].str.startswith('REM'),
        'Robo_Type'
    ] = 'ContrTrend_M'

    df.loc[
        df['Robo_Name'].str.match(r'^R_[A-Z]{3}_'),
        'Robo_Type'
    ] = 'ContrTrend'

    df.loc[
        df['Robo_Type'] == "",
        'Robo_Type'
    ] = 'Trend'

    # =========================
    # NET P/L (КОРРЕКТНО КАК В METATRADER)
    # =========================

    df['Net_PL'] = (
        df['Profit'].fillna(0) +
        df['Swap'].fillna(0) +
        df['Commission'].fillna(0)
    )

    # =========================
    # SWAP / HOLDING METRICS
    # =========================

    df['Holding_Hours'] = (
        df['Close Time'] - df['Open Time']
    ).dt.total_seconds() / 3600

    df['Holding_Days'] = df['Holding_Hours'] / 24

    df['Net_PL_No_Swap'] = (
        df['Net_PL'] -
        df['Swap'].fillna(0)
    )

    df['Swap_Per_Day'] = (
        df['Swap'].fillna(0) /
        df['Holding_Days'].where(df['Holding_Days'] > 0)
    ).fillna(0)

    df['Swap_Share'] = (
        df['Swap'].fillna(0) /
        df['Net_PL'].abs().where(df['Net_PL'].abs() > 0)
    ).fillna(0)

    df['Close_Date'] = df['Close Time'].dt.date

    return df
