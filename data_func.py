

def get_historical_data(fyers_model, cont_flag = "1"):
    """
    Get data from Fyers model
    """
    data = {
        "symbol":"NSE:SBIN-EQ",
        "resolution":"240",
        "date_format":"0",
        "range_from":"1622097600",
        "range_to":"1622097685",
        "cont_flag":"1"
        }
    return fyers_model.history(data)
    
