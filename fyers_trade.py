import os
import requests
from urllib.parse import urlparse, parse_qs
from fyers_api import accessToken
from fyers_api import fyersModel
from dotenv import load_dotenv
import pandas as pd
import time

DOTENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(DOTENV_PATH)


class FyersTrade:
    def __init__(self):
        self._username = os.environ.get("FYERS_USERNAME")
        self._password = os.environ.get("FYERS_PASSWORD")
        self._pin = os.environ.get("FYERS_PIN")
        self._client_id = os.environ.get("FYERS_CLIENT_ID")
        self._secret_key = os.environ.get("FYERS_SECRET_KET")
        self._redirect_uri = os.environ.get("FYERS_REDIRECT_URI")
        self._bot_token = os.environ.get('TEL_BOT_TOKEN')
        self._chat_id = os.environ.get('TEL_CHAT_ID')

        self._telegram_msg_dic = dict()

        self._timeframe_dict = {
            "1" : 86400 * 99,
            "2": 86400 * 99,
            "3": 86400 * 99,
            "5": 86400 * 99,
            "10": 86400 * 99,
            "15": 86400 * 99,
            "20": 86400 * 99,
            "30": 86400 * 99,
            "60": 86400 * 99,
            "120": 86400 * 99,
            "240": 86400 * 99,
            "D": 86400 * 300
        }
        self._fyers_obj = self._get_fyers_model()

    def login(self):
        self._fyer_obj = self._get_fyers_model()

    def _get_fyers_model(self):
        s = requests.Session()

        data1 = f'{{"fy_id":"{self._username}","password":"{self._password}","app_id":"2","imei":"","recaptcha_token":""}}'
        r1 = s.post("https://api.fyers.in/vagator/v1/login", data=data1)
        assert r1.status_code == 200, f"Error in r1:\n {r1.json()}"

        request_key = r1.json()["request_key"]
        data2 = f'{{"request_key":"{request_key}","identity_type":"pin","identifier":"{self._pin}","recaptcha_token":""}}'
        r2 = s.post("https://api.fyers.in/vagator/v1/verify_pin", data=data2)
        assert r2.status_code == 200, f"Error in r2:\n {r2.json()}"

        headers = {"authorization": f"Bearer {r2.json()['data']['access_token']}", "content-type": "application/json; charset=UTF-8"}
        data3 = f'{{"fyers_id":"{self._username}","app_id":"{self._client_id[:-4]}","redirect_uri":"{self._redirect_uri}","appType":"100","code_challenge":"","state":"abcdefg","scope":"","nonce":"","response_type":"code","create_cookie":true}}'
        r3 = s.post("https://api.fyers.in/api/v2/token", headers=headers, data=data3)
        assert r3.status_code == 308, f"Error in r3:\n {r3.json()}"

        parsed = urlparse(r3.json()["Url"])
        auth_code = parse_qs(parsed.query)["auth_code"][0]

        session = accessToken.SessionModel(client_id=self._client_id, secret_key=self._secret_key, redirect_uri=self._redirect_uri, response_type="code", grant_type="authorization_code")
        session.set_token(auth_code)
        response = session.generate_token()
        token = response["access_token"]
        print("Got the fyers access token!")

        fyers = fyersModel.FyersModel(client_id=self._client_id, token=token, log_path=os.getcwd())
        return fyers

    def get_historical_data(self, symbol, resolution, range_from, range_to, cont_flag = "1", date_format = "0"):
        """
        Get data from Fyers model
        """
        # Check resoltion
        if resolution not in self._timeframe_dict:
            print(f"Resolution not allowed: {resolution}")
            return None
        # Check if range is more than allowed
        req_range = range_to - range_from
        if req_range > self._timeframe_dict[resolution]:
            print("Requested range is more than allowed.")
            final_df = None
            new_range_to = range_from
            while new_range_to < range_to:
                new_range_from = new_range_to
                new_range_to = new_range_from + self._timeframe_dict[resolution]
                if new_range_to > range_to:
                    new_range_to = range_to
                df = self.get_historical_data(symbol, resolution, new_range_from, new_range_to)
                if df is not None and not df.empty:
                    if final_df is None:
                        final_df = df
                    else:
                        final_df = pd.concat([final_df, df]).drop_duplicates()
            if final_df is not None and not final_df.empty:
                final_df['datetime'] = pd.to_datetime(final_df['datetime'],unit='s')
                final_df['datetime'] = final_df['datetime'].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
            return final_df
        data = {
            "symbol": symbol,
            "resolution": resolution,
            "date_format": date_format,
            "range_from": range_from,
            "range_to": range_to,
            "cont_flag": cont_flag
            }
        resp = self._fyers_obj.history(data)
        if resp and "s" in resp and resp["s"] == "ok":
            return pd.DataFrame(resp["candles"], columns=["datetime", "open", "high", "low", "close", "vol"])
        elif resp and "s" in resp and resp["s"] == "error" and "Limit" in resp["message"]:
            time.sleep(30)
            resp = self._fyers_obj.history(data)
            if resp and "s" in resp and resp["s"] == "ok":
                return pd.DataFrame(resp["candles"], columns=["datetime", "open", "high", "low", "close", "vol"])
            elif resp and "s" in resp and resp["s"] == "error" and "Limit" in resp["message"]:
                print("TOO MANY ERRORS")
                exit()
        print(resp)
        return None

    def telegram_bot_sendtext(self, symbol, bot_message):
        if "&" in bot_message:
            bot_message = bot_message.replace("&", ".")
        send_text = 'https://api.telegram.org/bot' + self._bot_token + '/sendMessage?chat_id=' + self._chat_id + '&parse_mode=Markdown&text=' + bot_message
        if symbol in self._telegram_msg_dic:
            send_text = "{}&reply_to_message_id={}".format(send_text, self._telegram_msg_dic[symbol])
        res = requests.get(send_text)
        self._telegram_msg_dic[symbol] = res.json()['result']['message_id']