import json
import time
import requests
import uuid
import sys
import logging
import threading
from colorama import init
import sys
import argparse
import jwt
from cryptography.hazmat.primitives import serialization
import secrets

# X: @owldecoy

logging.basicConfig(
        filename='logs/PEPE_CANCEL_AND_SELL_ORDER.log', 
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


def get_open_sell_order(order_id):

        request_method = "GET"
        request_host = "api.coinbase.com"
        request_path = "/api/v3/brokerage/orders/historical/" + str(order_id)

        uri = f"{request_method} {request_host}{request_path}"
        jwt_token = build_jwt(uri)

        headers = {
                'Authorization': "Bearer " + str(jwt_token),
                'User-Agent': config['USER_AGENT']
        }

        if enable_proxy == "true":
                r = session.get("https://api.coinbase.com/api/v3/brokerage/orders/historical/" + str(order_id), headers=headers, proxies=proxies)
        elif enable_proxy == "false":
                r = session.get("https://api.coinbase.com/api/v3/brokerage/orders/historical/" + str(order_id), headers=headers)

        data = r.text

        json_data = json.loads(data)

        if debug:
                print(f"get_open_sell_order() debug: {json_data}")

        sell_order = json_data['order']

        return sell_order


def cancel_order(order_id):

        payload = json.dumps({
                "order_ids": [
                str(order_id)
                ]
        })

        request_method = "POST"
        request_host = "api.coinbase.com"
        request_path = "/api/v3/brokerage/orders/batch_cancel"

        uri = f"{request_method} {request_host}{request_path}"
        jwt_token = build_jwt(uri)

        headers = {
                'Authorization': "Bearer " + str(jwt_token),
                'User-Agent': config['USER_AGENT']
        }

        if enable_proxy == "true":
                r = session.post("https://api.coinbase.com/api/v3/brokerage/orders/batch_cancel", data=payload, headers=headers, proxies=proxies)
        elif enable_proxy == "false":
                r = session.post("https://api.coinbase.com/api/v3/brokerage/orders/batch_cancel", data=payload, headers=headers)

        if debug:
                print(f"cancel_order() debug: {r.text}")

        print(f"-- Sold {order_id}")



def create_sell_market_order(sell_amt):


        payload = json.dumps({
        "client_order_id": str(uuid.uuid4()),
        "product_id": str(config['PRODUCT']),
        "side": "SELL",
        "order_configuration": {
                "market_market_ioc": {
                "base_size": str(sell_amt)
                }
        }
        })

        request_method = "POST"
        request_host = "api.coinbase.com"
        request_path = "/api/v3/brokerage/orders"

        uri = f"{request_method} {request_host}{request_path}"
        jwt_token = build_jwt(uri)

        headers = {
                'Authorization': "Bearer " + str(jwt_token),
                'User-Agent': config['USER_AGENT']
        }

        if enable_proxy == "true":
                r = session.post("https://api.coinbase.com/api/v3/brokerage/orders", data=payload, headers=headers, proxies=proxies)
        elif enable_proxy == "false":
                r = session.post("https://api.coinbase.com/api/v3/brokerage/orders", data=payload, headers=headers)

        if debug:
                print(f"create_sell_market_order() debug: {r.text}")


if __name__ == "__main__":

        parser = argparse.ArgumentParser(description="SELL ORDER")
        parser.add_argument('--order-id', type=str, help='Order ID to cancel', required=True)
        args = parser.parse_args()

        try:

                with open('config.json', 'r') as s:

                        config = json.load(s)

                debug = False
                enable_proxy = config['ENABLE_PROXY']
                proxy_ip = config['PROXY_IP']

                proxies = {
                        'http': f'socks5h://{proxy_ip}',
                        'https': f'socks5h://{proxy_ip}'
                }

                session = requests.Session()
                init(autoreset=True)

                order_id = args.order_id.split()


                for order in order_id:

                        sell_order = get_open_sell_order(order)

                        #print(sell_order['order_id'])

                        # get base size from the order_id
                        sell_amt = sell_order['order_configuration']['limit_limit_gtc']['base_size']

                        # cancel the order
                        cancel_order(order)

                        time.sleep(2)

                        # place a sell market order for sell_amt (base_size)
                        create_sell_market_order(sell_amt)


        except Exception as e:
                logging.exception("------------error in escape pod----------")
                print("-- Error see SELL_ORDER log... exiting.")
                print(f"{e}")
                time.sleep(5)
                sys.exit()
