
import os
import requests
from urllib.parse import urlparse, parse_qs
from fyers_api import accessToken
from fyers_api import fyersModel
from dotenv import load_dotenv

DOTENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(DOTENV_PATH)

username = os.environ.get("FYERS_USERNAME")
password = os.environ.get("FYERS_PASSWORD")
pin = os.environ.get("FYERS_PIN")
client_id = os.environ.get("FYERS_CLIENT_ID")
secret_key = os.environ.get("FYERS_SECRET_KET")
redirect_uri = os.environ.get("FYERS_REDIRECT_URI")


def get_fyers_model():
    s = requests.Session()

    data1 = f'{{"fy_id":"{username}","password":"{password}","app_id":"2","imei":"","recaptcha_token":""}}'
    r1 = s.post("https://api.fyers.in/vagator/v1/login", data=data1)
    assert r1.status_code == 200, f"Error in r1:\n {r1.json()}"

    request_key = r1.json()["request_key"]
    data2 = f'{{"request_key":"{request_key}","identity_type":"pin","identifier":"{pin}","recaptcha_token":""}}'
    r2 = s.post("https://api.fyers.in/vagator/v1/verify_pin", data=data2)
    assert r2.status_code == 200, f"Error in r2:\n {r2.json()}"

    headers = {"authorization": f"Bearer {r2.json()['data']['access_token']}", "content-type": "application/json; charset=UTF-8"}
    data3 = f'{{"fyers_id":"{username}","app_id":"{client_id[:-4]}","redirect_uri":"{redirect_uri}","appType":"100","code_challenge":"","state":"abcdefg","scope":"","nonce":"","response_type":"code","create_cookie":true}}'
    r3 = s.post("https://api.fyers.in/api/v2/token", headers=headers, data=data3)
    assert r3.status_code == 308, f"Error in r3:\n {r3.json()}"

    parsed = urlparse(r3.json()["Url"])
    auth_code = parse_qs(parsed.query)["auth_code"][0]

    session = accessToken.SessionModel(client_id=client_id, secret_key=secret_key, redirect_uri=redirect_uri, response_type="code", grant_type="authorization_code")
    session.set_token(auth_code)
    response = session.generate_token()
    token = response["access_token"]
    print("Got the fyers access token!")

    fyers = fyersModel.FyersModel(client_id=client_id, token=token, log_path=os.getcwd())
    return fyers


if __name__ == "__main__":
    FYERS = get_fyers_model()
    print(FYERS.get_profile())