import pandas as pd

FILE_PATH = r"C:\Users\User\Desktop\Forex Tester\RoboAnalytics\t_data.htm"

def load_tables():
    return pd.read_html(FILE_PATH)

