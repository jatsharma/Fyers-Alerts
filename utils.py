import requests


TELEGRAM_MSG_DIC = dict()

def get_historical_data(fyers_model, symbol, resolution, range_from, range_to, cont_flag = "1", date_format = "0"):
    """
    Get data from Fyers model
    """
    data = {
        "symbol": symbol,
        "resolution": resolution,
        "date_format": date_format,
        "range_from": range_from,
        "range_to": range_to,
        "cont_flag": cont_flag
        }
    resp = fyers_model.history(data)
    if "s" in resp and resp["s"] == "ok":
        return resp["candles"]
    return False

def telegram_bot_sendtext(symbol, bot_message):
    global TELEGRAM_MSG_DIC
    if "&" in bot_message:
       bot_message = bot_message.replace("&", ".")
    bot_token = '1663699329:AAFeC08JwdiihwyRi4gDYne90yX5PYEKy2w'
    bot_chatID = '-528109475'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    if symbol in TELEGRAM_MSG_DIC:
        send_text = "{}&reply_to_message_id={}".format(send_text, TELEGRAM_MSG_DIC[symbol])
    res = requests.get(send_text)
    TELEGRAM_MSG_DIC[symbol] = res.json()['result']['message_id']