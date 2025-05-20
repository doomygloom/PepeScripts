import json
import time
import requests
from decimal import Decimal
from colorama import init
import sys
import argparse
import logging
import os
import jwt
from cryptography.hazmat.primitives import serialization
import secrets

# X: @owldecoy

logging.basicConfig(
        filename='logs/PEPE_BALANCE.log', 
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


def get_balance():

        # get portfolio UUID for config file
        # GET https://api.coinbase.com/api/v3/brokerage/portfolios

        request_method = "GET"
        request_host = "api.coinbase.com"
        request_path = "/api/v3/brokerage/portfolios/" + config['PORTFOLIO_UUID']

        uri = f"{request_method} {request_host}{request_path}"
        jwt_token = build_jwt(uri)

        headers = {
                'Authorization': "Bearer " + str(jwt_token),
                'User-Agent': config['USER_AGENT']
        }

        if enable_proxy == "true":
                r = session.get("https://api.coinbase.com/api/v3/brokerage/portfolios/" + config['PORTFOLIO_UUID'], headers=headers, proxies=proxies)                                                                                                                   
        elif enable_proxy == "false":
                r = session.get("https://api.coinbase.com/api/v3/brokerage/portfolios/" + config['PORTFOLIO_UUID'], headers=headers)

        data = r.text

        if debug:
                print(f"get_balance() debug: {data} ")

        json_data = json.loads(data)

        breakdown = json_data['breakdown']['portfolio_balances']

        return breakdown


def get_current_price():

        headers = {
                'User-Agent': config['USER_AGENT']
        }

        if enable_proxy == "true":
                r = session.get('https://api.exchange.coinbase.com/products/' + config['PRODUCT'] + '/ticker', headers=headers, proxies=proxies)
        elif enable_proxy == "false":
                r = session.get('https://api.exchange.coinbase.com/products/' + config['PRODUCT'] + '/ticker', headers=headers)
        try:
                json_data = r.json()

        except Exception as e:
                print("Error:", str(e))
                sys.exit()

        current_price = round(Decimal(json_data['price']), int(config["CB_PRODUCT_DECIMALS"]))

        return current_price


def get_fees():

        request_method = "GET"
        request_host = "api.coinbase.com"
        request_path = "/api/v3/brokerage/transaction_summary"

        uri = f"{request_method} {request_host}{request_path}"
        jwt_token = build_jwt(uri)

        headers = {
                'Authorization': "Bearer " + str(jwt_token),
                'User-Agent': config['USER_AGENT']
        }

        if enable_proxy == "true":
                r = session.get("https://api.coinbase.com/api/v3/brokerage/transaction_summary", headers=headers, proxies=proxies)
        elif enable_proxy == "false":
                r = session.get("https://api.coinbase.com/api/v3/brokerage/transaction_summary", headers=headers)

        data = r.text
        if debug:
                print(f"get_fees() debug: {data} ")

        json_data = json.loads(data)

        fees = json_data

        return fees


def prune_pnl_prices_file(filename, max_lines=500000):
    """
    Prunes the .pnl_prices file to keep only the last 'max_lines' of entries.
    """
    if not os.path.exists(filename):
        print(f"-- File {filename} does not exist.")
        return

    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    if len(lines) > max_lines:
        lines_to_keep = lines[-max_lines:]

        with open(filename, 'w', encoding='utf-8') as file:
            file.writelines(lines_to_keep)
    else:
        pass
                #print("File already has fewer or equal lines than max_lines, no pruning needed.")


def read_every_nth_line(filename):

        with open(filename, 'r') as file:
                for line_number, line in enumerate(file, 1):
                        if line_number % nth_line == 0:
                                yield line.strip()



if __name__ == "__main__":


        try:

                parser = argparse.ArgumentParser(description="BALANCE")
                parser.add_argument('-sb', '--startingbalance', type=str, help='starting balance', required=True)
                args = parser.parse_args()

                sb = args.startingbalance

                debug = False
                nth_line = 100
                init(autoreset=True)
                session = requests.Session()

                #print(f"Proxy enabled: {enable_proxy}")


                lsb_filename = '.last_starting_balance'
                if not os.path.exists(lsb_filename):

                        with open('.last_starting_balance', 'w') as l:

                                pass

                with open('.last_starting_balance', 'w') as l:

                        l.write(sb)

                while True:

                        with open('config.json', 'r') as s:
                                config = json.load(s)

                        enable_proxy = config["ENABLE_PROXY"]
                        proxy_ip = config['PROXY_IP']

                        proxies = {
                                'http': f'socks5h://{proxy_ip}',
                                'https': f'socks5h://{proxy_ip}'
                        }

                        try:

                                fees = get_fees()
                                bb = get_balance()

                        except:
                                print("[+] Failed to get either fees or balance.")
                                print("[+] Trying again...")
                                time.sleep(5)
                                continue

                        current_cash_balance = bb['total_balance']['value']
                        current_crypto_balance = bb['total_crypto_balance']['value']
                        available_cash = round(Decimal(current_cash_balance),2) - round(Decimal(current_crypto_balance),2)


                        #print(f"-- MARKET PRICE: ${current_price}")
                        #print("-------------------------------------------------------")
                        print(f"-- STARTING BALANCE: ${sb}")
                        print(f"-- PROFITS/LOSSES: ${round(Decimal(current_cash_balance), 2) - round(Decimal(sb), 2)}")
                        print(f"-- CASH BALANCE: ${current_cash_balance}")
                        print(f"-- CRYPTO BALANCE: ${round(Decimal(current_crypto_balance), 2)}")
                        print(f"-- AVAILABLE CASH: ${available_cash}")

                        # write pnl chart files ####################################################
                        prices_for_chart_file = '.pnl_prices'
                        prices_for_chart_file2 = '.pnl_prices_use_this_one'
                        if not os.path.exists(prices_for_chart_file):

                                with open(prices_for_chart_file, 'w') as p:

                                        pass

                        prune_pnl_prices_file(prices_for_chart_file)

                        with open(prices_for_chart_file, 'a') as p:

                                p.write(str(round(Decimal(current_cash_balance), 2) - round(Decimal(sb), 2)) + '\n')

                        with open(prices_for_chart_file2, 'w+') as p2:
                                for line in read_every_nth_line(prices_for_chart_file):
                                        p2.write(line + '\n')

                        ########################################################################

                        try:
                                if round(Decimal(fees['total_volume']), 0) < float(60000.00):
                                        print(f"-- VOL: ${round(Decimal(fees['total_volume']), 0)} !!! <----")
                                else:
                                        print(f"-- VOL: ${round(Decimal(fees['total_volume']), 0)} | {fees['fee_tier']['pricing_tier']} ({fees['fee_tier']['usd_from']} --> {fees['fee_tier']['usd_to']})")                                                             
                        except:
                                print("-- error calculating total volume, retrying")
                                time.sleep(1)
                                continue
                        print("-------------------------------------------------------")
                        time.sleep(2)
                        try:

                                current_price = get_current_price()

                        except:
                                print("[+] Failed to get current price.")
                                print("[+] Trying again...")
                                time.sleep(5)
                                continue

                        # we write the current price to a file which is read by a route in pepe-term.py. 
                        # this api is then queried from the index.html file, which we display the price in
                        # some div somewhere
                        with open('.current_price', 'w+') as f:
                                f.write(str(current_price))

                        continue

        except:
                print("Error in PEPE_BALANCE_PY. See log.")
                print("Task stopped.")
                logging.exception("Error in PEPE_BALANCE")
                sys.exit()
