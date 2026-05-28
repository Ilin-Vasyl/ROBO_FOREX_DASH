import pandas as pd
import plotly.express as px

def filter_df(df, start_date, end_date, pair, robo_type, robo_name):

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    filtered = df[
        (df['Close Time'] >= start_date) &
        (df['Close Time'] <= end_date)
    ]

    if pair != 'ALL':
        filtered = filtered[filtered['Item'] == pair]

    if robo_type != 'ALL':
        filtered = filtered[filtered['Robo_Type'] == robo_type]

    if robo_name != 'ALL':
        filtered = filtered[filtered['Robo_Name'] == robo_name]

    return filtered


def build_chart(filtered):

    if filtered.empty:
        return px.line(title="Нет данных")

    daily = filtered.groupby(
        ['Close_Date', 'Robo_Type']
    )['Net_PL'].sum().reset_index()

    daily['Balance'] = daily.groupby('Robo_Type')['Net_PL'].cumsum()

    final_balance = daily.groupby('Robo_Type')['Balance'].last().to_dict()

    daily['Robo_Name'] = daily['Robo_Type'].apply(
        lambda x: f"{x} ({final_balance.get(x,0):.2f})"
    )

    color_map = {
        f"Trend ({final_balance.get('Trend',0):.2f})": "#1f77b4",
        f"ContrTrend ({final_balance.get('ContrTrend',0):.2f})": "#ff7f0e",
        f"ContrTrend_M ({final_balance.get('ContrTrend_M',0):.2f})": "#2ca02c"
    }

    fig = px.line(
        daily,
        x='Close_Date',
        y='Balance',
        color='Robo_Name',
        color_discrete_map=color_map,
    )

    fig.update_layout(hovermode='x unified')

    return fig