import json
import time
import requests
import uuid
import datetime
from decimal import Decimal
from colorama import init
import sys
import argparse
import logging
import threading
import simpleaudio as sa
import jwt
from cryptography.hazmat.primitives import serialization
import secrets
import os
import random

logging.basicConfig(
        filename='logs/PEPE_BUY_AT_MARKET.log', 
        filemode='w', 
        format='%(name)s - %(levelname)s - %(message)s', 
        level=logging.ERROR
)

def build_jwt(uri):

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


def create_buy_market_order(total_cost_rounded):

        payload = json.dumps({
        "client_order_id": str(uuid.uuid4()),
        "product_id": config['PRODUCT'],
        "side": "BUY",
        "order_configuration": {
                "market_market_ioc": {
                "quote_size": str(total_cost_rounded)
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

        json_data = json.loads(r.text)

        if debug == True:
                print(f"create_buy_market_order debug {json_data}")


        order_status = json_data['success']
        order_id = json_data['success_response']['order_id']
        order_quote_size = json_data['order_configuration']['market_market_ioc']['quote_size']


        return order_status, order_id, order_quote_size



def play_sound_non_blocking(sound_file):
        def run():
                wave_obj = sa.WaveObject.from_wave_file(sound_file)
                play_obj = wave_obj.play()
                play_obj.wait_done()

        thread = threading.Thread(target=run)
        thread.start()


def thread_target(total_cost_rounded, result_list, index):

        result_list[index] = create_buy_market_order(total_cost_rounded)
        time.sleep(0.3)


def pick_nearby_amt_to_buy_number(original_number, range=5):
        # Ensure the range is positive
        range = abs(range)
        # Generate a number within the range [original_number, original_number + range]
        return random.randint(original_number, original_number + range)


def pick_nearby_num_orders_number(original_number, range=3):
        # Ensure the range is positive
        range = abs(range)
        # Generate a number within the range [original_number, original_number + range]
        return random.randint(original_number, original_number + range)

if __name__ == "__main__":

        try:

                debug = False
                success_sound = 'audio/success_buy.wav'
                error_sound = 'audio/error.wav'
                session = requests.Session()
                init(autoreset=True)

                with open('config.json', 'r') as s:
                        config = json.load(s)

                enable_proxy = config["ENABLE_PROXY"]
                proxy_ip = config['PROXY_IP']
                proxies = {
                        'http': f'socks5h://{proxy_ip}',
                        'https': f'socks5h://{proxy_ip}'
                }

                parser = argparse.ArgumentParser(description="BUY AT PRICE")
                parser.add_argument('-a', '--amount', type=str, help='amount to buy in USD', required=True)
                args = parser.parse_args()

                amt_to_buy1 = args.amount
                #num_orders1 = config["NUM_ORDERS"]
                num_orders = config["NUM_ORDERS"] # uncomment to disable order count randomization
                #num_orders = pick_nearby_num_orders_number(int(num_orders1)) # comment to disable order count randomization

                try:
                        results = [None] * int(num_orders)

                        threads = []
                        for i in range(int(num_orders)):

                                now = datetime.datetime.now()
                                amt_to_buy = pick_nearby_amt_to_buy_number(int(amt_to_buy1))
                                total_cost = int(amt_to_buy)
                                total_cost_rounded = round(Decimal(total_cost), 0)

                                t = threading.Thread(target=thread_target, args=(total_cost_rounded, results, i), name=f"Thread-{i}")
                                threads.append(t)
                                t.start()

                        for t in threads:
                                t.join()

                except Exception as e:

                        print("-- error creating BUY order. see log")
                        logging.exception("error creating BUY order")
                        play_sound_non_blocking(error_sound) # script will exit here

                for i, (order_status, order_id, order_quote_size) in enumerate(results):
                        #print(f"Thread-{i} returned: {order_status}, {order_id}, {order_quote_size}")

                        if order_status == True:

                                bought_orders_data = {
                                        "order_id": str(order_id),
                                        "time": str(datetime.datetime.now()),
                                        "quote_size": str(order_quote_size),
                                        "bought_at_price": None,
                                        "token_amount": None,
                                        "sell_order_created": False
                                }

                                now = datetime.datetime.now()
                                date_str = now.strftime('%Y%m%d')
                                orders_file_path = f"{date_str}_bought_orders.json"

                                if not os.path.exists(orders_file_path):

                                        with open(orders_file_path, 'w') as file:

                                                file.write('{"bought_orders": []}')

                                with open(orders_file_path,'r+') as file:

                                        file_data = json.load(file)
                                        file_data["bought_orders"].append(bought_orders_data)
                                        file.seek(0)
                                        json.dump(file_data, file, indent = 4)

                                now = datetime.datetime.now()
                                print("-- Time:", str(now))
                                print("-- Product:", config['PRODUCT'])
                                print("-- New BUY Order Filled")
                                print(f"-- Bought ${order_quote_size} at market")
                                print(f"-- Order Status: {order_status}")
                                print("-- Task Completed OK")
                                print("-------------------------------------------------------")

                        elif order_status == False:

                                print("-- Order failed")
                                play_sound_non_blocking(error_sound) # script will exit here

                        else:

                                print("-- some error happened. Try again.")
                                logging.exception("----------- error ------------------")
                                play_sound_non_blocking(error_sound) # script will exit here

        except Exception as e:
                logging.exception("BUY_AT_MARKET ERROR 2")
                print("Error. Exiting. See BUY_AT_MARKET.log")
                print(e)
                play_sound_non_blocking(error_sound) # script will exit here
