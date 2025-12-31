from app.common.imports import *
from app.api.config.config import FERNET_KEY

import uuid
import hashlib
import jwt
import requests
from urllib.parse import unquote, urlencode

fernet_key = FERNET_KEY.encode()
cipher = Fernet(fernet_key)


async def exchange_information(ticker, currency, access_key, secret_key):
    try:
        url = "https://api.upbit.com/v1/accounts"

        # 복호화
        access_key = cipher.decrypt(access_key.encode()).decode()
        secret_key = cipher.decrypt(secret_key.encode()).decode()

        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
        }
        jwt_token = jwt.encode(payload, secret_key)

        headers = {"Authorization": f"Bearer {jwt_token}"}

        res = requests.get(url, headers=headers, timeout=1) 
        balances = res.json()
        
        # 각 코인별 수량
        coin_list = {coin: float(next((x['balance'] for x in balances if x['currency']==coin), 0))
                    for coin in ticker}
        
        # 각 코인별 평단가
        avg_list = {coin: float(next((x['avg_buy_price'] for x in balances if x['currency']==coin), 0)) for coin in ticker}

        # 잔액
        available_cash = float(next((x['balance'] for x in balances if x['currency']==f'{currency}'), 0))

        trade_history  = {}



        BASE_URL = "https://api.upbit.com"
        PATH = "/v1/orders/closed"

        trade_history = {}
        for coin in ticker:
            params = {
                "market": f"KRW-{coin}",
                "states[]": ["done", "cancel"],
                "limit": 100,       
                "page": 1,         
                "order_by": "desc"  
            }

            query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

            m = hashlib.sha512()
            m.update(query_string)
            query_hash = m.hexdigest()

            payload = {
            "access_key": access_key,
            "nonce": str(uuid.uuid4()),
            "query_hash": query_hash,
            "query_hash_alg": "SHA512",
            }

            jwt_token = jwt.encode(payload, secret_key, algorithm="HS256")

            headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/json",
            }

            res = requests.get(f"{BASE_URL}{PATH}", headers=headers, params=params)

            res_json = res.json()  # 반드시 json() 사용
            if not res_json:
                trade_history[coin] = None
                continue

            latest_order = res_json[0]

            data = {
                "created_at" : latest_order['created_at'],
                "side" : latest_order['side'],
                "executed_volume" : float(latest_order['executed_volume']),
                "executed_funds" : latest_order['executed_funds']
            }
            trade_history[coin] = data
    except Exception as e:
        print(e)
        return 0, {}, {}
    
    return available_cash, coin_list, trade_history


