from login_sys import get_fyers_model
from utils import get_historical_data
from time import time
import pandas as pd

def main():
    FYERS = get_fyers_model()
    now_time = int(time())
    symbol = "MCX:SILVERMIC22AUGFUT"
    resolution = "D"
    range_from = now_time - (86400 * 30)
    range_to = now_time
    data = get_historical_data(FYERS, symbol, resolution, range_from, range_to)
    if data:
        data_df = pd.DataFrame(data, columns=["datetime", "open", "high", "low", "close", "vol"])
        # print(json.dumps(data, indent=1, sort_keys=True))
        print(data_df)

if __name__ == "__main__":
    main()