import json
import time
import requests
from decimal import Decimal
import sys
import logging
import threading
from colorama import init
import jwt
from cryptography.hazmat.primitives import serialization
import secrets

# X: @owldecoy

logging.basicConfig(
        filename='logs/PEPE_ORDER_BOOK.log', 
        filemode='w', 
        format='%(name)s - %(levelname)s - %(message)s', 
        level=logging.ERROR
)


def build_jwt(uri): # new API auth method, for Authorization: Bearer

        private_key_bytes = config["NEW_KEY_SECRET"].encode('utf-8')
        private_key = serialization.load_pem_private_key(private_key_bytes, password=None)

        jwt_payload = {
                'sub': config["NEW_KEY_NAME"],
                'iss': "cdp",
                'nbf': int(time.time()),
                'exp': int(time.time()) + 120,
                'uri': uri,
        }

        jwt_token = jwt.encode(
                jwt_payload,
                private_key,
                algorithm='ES256',
                headers={'kid': config["NEW_KEY_NAME"], 'nonce': secrets.token_hex()},
        )

        return jwt_token


def get_open_sell_orders():

        ''' returns last N orders JSON'''

        request_method = "GET"
        request_host = "api.coinbase.com"
        request_path = "/api/v3/brokerage/orders/historical/batch"

        uri = f"{request_method} {request_host}{request_path}"
        jwt_token = build_jwt(uri)

        headers = {
                'Authorization': "Bearer " + str(jwt_token),
                'User-Agent': config['USER_AGENT']
        }

        if enable_proxy == "true":
                r = session.get("https://api.coinbase.com/api/v3/brokerage/orders/historical/batch?product_id=" + config['PRODUCT'] + "&limit=500&order_side=SELL&order_status=OPEN", headers=headers, proxies=proxies)                                                 
        elif enable_proxy == "false":
                r = session.get("https://api.coinbase.com/api/v3/brokerage/orders/historical/batch?product_id=" + config['PRODUCT'] + "&limit=500&order_side=SELL&order_status=OPEN", headers=headers)                                                                  

        data = r.text

        json_data = json.loads(data)

        if debug:
                print(f"get_open_sell_orders() debug: {json_data}")

        sell_orders = json_data['orders']

        return sell_orders



if __name__ == "__main__":

        with open('config.json', 'r') as s:
                config = json.load(s)

        debug = False

        session = requests.Session()
        init(autoreset=True)

        enable_proxy = config['ENABLE_PROXY']
        proxy_ip = config['PROXY_IP']
        proxies = {
                'http': f'socks5h://{proxy_ip}',
                'https': f'socks5h://{proxy_ip}'
        }

        oso = []
        limit_prices = []
        order_ids = []

        try:
                s_orders = get_open_sell_orders()
                for s in s_orders:

                        limit_prices.append(s['order_configuration']['limit_limit_gtc']['limit_price'])
                        order_ids.append(s['order_id'])

                combined = list(zip(limit_prices, order_ids))
                sorted_combined = sorted(combined, key=lambda x: x[0])

                closest_5 = sorted_combined[:5]

        except:
                print("-- error with get_open_sell_orders. stale order? retrying...")
                logging.exception("error-----------------------")
                sys.exit()

        try:
                for s in s_orders:

                        oso.append(s['order_configuration']['limit_limit_gtc']['base_size'])
                        print(s['order_id'], s['order_configuration']['limit_limit_gtc']['base_size'] + str(" @ ") + s['order_configuration']['limit_limit_gtc']['limit_price'] + '\n')                                                                                 

        except Exception as e:
                print(f" Error: {e}")
                sys.exit()

        print("-------------------------------------------------------")
        sumOfElements2 = 0
        for element in oso:
                sumOfElements2 = sumOfElements2 + float(element)

        print(f"{config['PRODUCT']} HOLDING:", sumOfElements2, "| OPEN: ", str(len(s_orders)))
        print("-------------------------------------------------------")

        closest_5_ids = [str(id) for value, id in sorted_combined[:5]]
        print(f"[Closest 5]: {' '.join(closest_5_ids)}")
        print("-------------------------------------------------------")
