import json
import time
import requests
from colorama import init
import sys
import argparse
import logging
import threading
import simpleaudio as sa
import jwt
from cryptography.hazmat.primitives import serialization
import secrets


logging.basicConfig(
        filename='logs/CANCEL_ORDER.log', 
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



def cancel_order(order_to_cancel):

        payload = json.dumps({
                "order_ids": [
                str(order_to_cancel)
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


def play_sound_non_blocking(sound_file):
        def run():
                wave_obj = sa.WaveObject.from_wave_file(sound_file)
                play_obj = wave_obj.play()
                play_obj.wait_done()

        thread = threading.Thread(target=run)
        thread.start()


if __name__ == "__main__":

        try:

                with open('config.json', 'r') as s:
                        config = json.load(s)

                error_sound = "audio/error.wav"
                parser = argparse.ArgumentParser(description="CANCEL ORDER")
                parser.add_argument('-id', '--order_id', type=str, help='order id', required=True)
                args = parser.parse_args()

                session = requests.Session()
                init(autoreset=True)

                debug = False

                enable_proxy = config['ENABLE_PROXY']
                proxy_ip = config['PROXY_IP']
                proxies = {
                        'http': f'socks5h://{proxy_ip}',
                        'https': f'socks5h://{proxy_ip}'
                }

                order_to_cancel = args.order_id.split()
                for order in order_to_cancel:
                        cancel_order(order)
                        print(f"-- Cancelled {order}")
                        time.sleep(2)

        except Exception as e:
                print("Error in CANCEL. See log.")
                print(f"{e}")
                logging.exception("Error in CANCEL")
                play_sound_non_blocking(error_sound)
                sys.exit()
