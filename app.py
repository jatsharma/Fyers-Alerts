# from login_sys import get_fyers_model
# from utils import get_historical_data
from time import time
import pandas as pd

from fyers_trade import FyersTrade

def main():
    FYERS = FyersTrade()
    now_time = int(time())
    symbol = "MCX:SILVERMIC22AUGFUT"
    resolution = "1"
    range_from = now_time - (86400 * 3000)
    range_to = now_time
    print(range_from, range_to)
    data_df = FYERS.get_historical_data(symbol, resolution, range_from, range_to)
    if data_df is not None:
        print(data_df)
        pd.DataFrame.to_csv(data_df, f"{symbol}.csv")

if __name__ == "__main__":
    main()