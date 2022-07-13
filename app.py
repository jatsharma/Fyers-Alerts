from login_sys import get_fyers_model
from data_func import get_historical_data

def main():
    FYERS = get_fyers_model()
    data = get_historical_data(FYERS)
    print(data)


if __name__ == "__main__":
    main()