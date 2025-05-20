import json
import time
import os
import requests
import uuid
from colorama import init
from decimal import Decimal
import datetime
import argparse
import jwt
from cryptography.hazmat.primitives import serialization
import secrets
import sys

# X: @owldecoy

init(autoreset=True)


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


def create_sell_limit_order(order):

        save_tokens = float(order['token_amount']) * float(save_tokens_percent) # save 0.1% of the fill_size
        fill_size = round(float(order['token_amount']) - save_tokens) # save some token
        bought_at_price = order['bought_at_price']

        ##### PERCENTAGE MODES ############################################

        #if args.percentage == 0.5:
        #       # 0.5%
        #       up_target_percentage0_5 = float(bought_at_price) * 0.005 # 0.5%
        #       up_target = round(Decimal(bought_at_price), int(config["CB_PRODUCT_DECIMALS"])) + round(Decimal(up_target_percentage0_5), int(config["CB_PRODUCT_DECIMALS"]))                                                                                           
        #       print("-- Mode: 0.5% Sell Target")

        #elif args.percentage == 0.6:
        #       # 0.6%
        #       up_target_percentage0_6 = float(bought_at_price) * 0.006 # 0.6%
        #       up_target = round(Decimal(bought_at_price), int(config["CB_PRODUCT_DECIMALS"])) + round(Decimal(up_target_percentage0_6), int(config["CB_PRODUCT_DECIMALS"]))                                                                                           
        #       print("-- Mode: 0.6% Sell Target")

        if args.percentage == 0.8:
                # 0.8%
                up_target_percentage0_8 = float(bought_at_price) * 0.008 # 0.8%
                up_target = round(Decimal(bought_at_price), int(config["CB_PRODUCT_DECIMALS"])) + round(Decimal(up_target_percentage0_8), int(config["CB_PRODUCT_DECIMALS"]))
                #print("-- Mode: 0.8% Sell Target")

        elif args.percentage == 1:
                # 1%
                up_target_percentage1 = float(bought_at_price) * 0.01 # 1%
                up_target = round(Decimal(bought_at_price), int(config["CB_PRODUCT_DECIMALS"])) + round(Decimal(up_target_percentage1), int(config["CB_PRODUCT_DECIMALS"]))
                #print("-- Mode: 1% Sell Target")

        elif args.percentage == 1.3:
                # 1.3%
                up_target_percentage1_3 = float(bought_at_price) * 0.013 # 1.3%
                up_target = round(Decimal(bought_at_price), int(config["CB_PRODUCT_DECIMALS"])) + round(Decimal(up_target_percentage1_3), int(config["CB_PRODUCT_DECIMALS"]))
                #print("-- Mode: 1.3% Sell Target")

        elif args.percentage == 1.5:
                # 1.5%
                up_target_percentage1_5 = float(bought_at_price) * 0.015 # 1.5%
                up_target = round(Decimal(bought_at_price), int(config["CB_PRODUCT_DECIMALS"])) + round(Decimal(up_target_percentage1_5), int(config["CB_PRODUCT_DECIMALS"]))
                #print("-- Mode: 1.5% Sell Target")

        elif args.percentage == 2:
                # 2%
                up_target_percentage2 = float(bought_at_price) * 0.02 # 2%
                up_target = round(Decimal(bought_at_price), int(config["CB_PRODUCT_DECIMALS"])) + round(Decimal(up_target_percentage2), int(config["CB_PRODUCT_DECIMALS"]))
                #print("-- Mode: 2% Sell Target")

        elif args.percentage == 3:
                # 3%
                up_target_percentage3 = float(bought_at_price) * 0.03 # 3%
                up_target = round(Decimal(bought_at_price), int(config["CB_PRODUCT_DECIMALS"])) + round(Decimal(up_target_percentage3), int(config["CB_PRODUCT_DECIMALS"]))
                #print("-- Mode: 3% Sell Target")

        elif args.percentage == 5:
                # 5%
                up_target_percentage5 = float(bought_at_price) * 0.05 # 5%
                up_target = round(Decimal(bought_at_price), int(config["CB_PRODUCT_DECIMALS"])) + round(Decimal(up_target_percentage5), int(config["CB_PRODUCT_DECIMALS"]))
                #print("-- Mode: 5% Sell Target")


        payload = json.dumps({
        "client_order_id": str(uuid.uuid4()),
        "product_id": config['PRODUCT'],
        "side": "SELL",
        "order_configuration": {
                "limit_limit_gtc": {
                "base_size": str(fill_size),
                "limit_price": str(up_target),
                "post_only": False
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


        data = r.text

        json_data = json.loads(data)

        if debug:
                print(f"create_sell_limit_order debug {json_data}")

        order_status = json_data['success']

        now = datetime.datetime.now()
        print("-------------------------------------------------------")
        print("-- Time:", str(now))
        print("-- Bought at price: $" + str(bought_at_price))
        print(f"-- Mode: {args.percentage}% Sell Target")
        print("-- Amount: " + str(fill_size) + " " + str(config['PRODUCT']))
        print("-- Sell Target: " + str(up_target))
        print(f"-- Saved {save_tokens} {config['PRODUCT']} for the bag. ")

        return order_status, up_target



def get_order_info(order_id):

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

        json_data = json.loads(r.text)

        if debug:
                print(f"get_order_info debug {json_data}")

        return json_data['order']['filled_size'], json_data['order']['average_filled_price']


def scan_order_file(max_entries):

        now = datetime.datetime.now()
        date_str = now.strftime('%Y%m%d')
        orders_file_path = f"{date_str}_bought_orders.json"

        if not os.path.exists(orders_file_path):

                with open(orders_file_path, 'w') as file:

                        file.write('{"bought_orders": []}')
        else:
                pass


        if os.path.exists(orders_file_path):

                try:
                        with open(orders_file_path, 'r') as file:

                                order_data = json.load(file)

                        orders = order_data.get('bought_orders', [])

                        if orders and isinstance(orders, list):

                                if len(orders) >= max_entries:
                                        new_orders = orders[-max_entries:]
                                else:
                                        new_orders = orders

                                orders_in_limbo = []

                                for order in orders:

                                        if not order.get('sell_order_created', True):

                                                try:
                                                        token_amount, bought_at_price_real = get_order_info(order['order_id'])
                                                        token_amount_rounded = round(float(token_amount), 2)

                                                        if token_amount_rounded != 0.0:

                                                                order['bought_at_price'] = str(bought_at_price_real)
                                                                order['token_amount'] = str(token_amount_rounded)

                                                                order_status, up_target = create_sell_limit_order(order)

                                                                if order_status:
                                                                        order['sell_order_created'] = True
                                                                        with open(orders_file_path, 'w') as file:
                                                                                json.dump(order_data, file, indent=4)
                                                                else:
                                                                        print(f"-- Error: Operation failed for order_id: {order['order_id']}. Will retry.")                                                                                                             
                                                                        sys.exit()
                                                        else:
                                                                print("-- Error 5: failed order. try again")
                                                                sys.exit()
                                                except:
                                                        print(f"-- Error: Order {order['order_id'].split("-")[0]} not ready yet. Try again...")                                                                                                                         
                                                        orders_in_limbo.append(order['order_id'])
                                                        continue

                        else:
                                if not orders:
                                        pass
                                else:
                                        print("Data is not in the expected list format under 'bought_orders'.")

                except (json.JSONDecodeError, FileNotFoundError) as e:
                        print(f"-- Error reading or processing file: {e}")

        try:
                if len(orders_in_limbo) > 0:
                        print(f"-- WARN: {len(orders_in_limbo)} orders in limbo. Trading likely degraded.")
        except:
                pass

        print("-------------------------------------------------------")
        print(f"-- Waiting for manual scan... ({args.percentage}% sell target)")
        print("-------------------------------------------------------")


if __name__ == "__main__":

        parser = argparse.ArgumentParser(description="SELLMON")
        parser.add_argument('-p', '--percentage', type=float, help='percentage sell target [0.5/0.6/1/1.3/2/3/5]', required=True)
        args = parser.parse_args()

        session = requests.Session()

        with open('config.json', 'r') as c:

                config = json.load(c)

        debug = False
        enable_proxy = config['ENABLE_PROXY']
        proxy_ip = config['PROXY_IP']
        proxies = {
                'http': f'socks5h://{proxy_ip}',
                'https': f'socks5h://{proxy_ip}'
        }

        sellmon_auto_refresh = config['SELLMON_AUTO_REFRESH']

        save_tokens_percent = 0.001 # 0.1%

        now = datetime.datetime.now()
        date_str = now.strftime('%Y%m%d')
        orders_file_path = f"{date_str}_bought_orders.json"

        if not os.path.exists(orders_file_path):

                with open(orders_file_path, 'w') as file:

                        file.write('{"bought_orders": []}')
        else:
                pass

        if sellmon_auto_refresh == "true":
                while True: 

                        with open('config.json', 'r') as c:

                                config = json.load(c)

                        debug = False
                        enable_proxy = config['ENABLE_PROXY']
                        proxy_ip = config['PROXY_IP']
                        proxies = {
                                'http': f'socks5h://{proxy_ip}',
                                'https': f'socks5h://{proxy_ip}'
                        }

                        sellmon_auto_refresh = config['SELLMON_AUTO_REFRESH']
                        scan_order_file(max_entries=50)
                        time.sleep(5) 

        elif sellmon_auto_refresh == "false":

                scan_order_file(max_entries=50)
