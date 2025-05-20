# PepeScripts
Various python scripts for trading PEPE on Coinbase

![image](https://github.com/user-attachments/assets/d43bd744-d0d3-4c87-bd1a-93f9df163d6a)

## `pepe_balance.py`
Monitors the balance of a specified portfolio, tracks PEPE profit and loss over time, and records the data for later analysis. It also fetches the current PEPE market price and logs transaction fees/tier

Usage: `python pepe_balance.py --startingbalance 2800.00`

## `pepe_buy_at_market.py`
Creates a market buy order for PEPE

Usage: `python pepe_buy_at_market.py --amount 10` (in dollars)

## `pepe_cancel_and_sell_order.py`
Cancels and then sells a specified sell order at market price

Usage: `python pepe_cancel_and_sell_order.py --order-id <order UUID>`

Note: Get order you want to cancel UUID from `pepe_order_book.py`.

## `pepe_cancel_order.py`
Just cancels a sell order

Usage: `python pepe_cancel_order.py --order-id <order UUID>`

Note: Get order you want to cancel UUID from `pepe_order_book.py`.

## `pepe_order_book.py`
Monitors your open PEPE sell orders in the Coinbase order book and retrieves and displays the most recent open sell orders, including the base size and limit price, and identifies the five closest orders based on limit price.

Usage: `python pepe_order_book.py`

## `pepe_sell_mon.py`
Scans previously executed buy orders and places corresponding sell limit orders at a user-defined percentage above the purchase price.

Usage: `python pepe_sell_mon.py --percentage 5`

Supported percentage targets for placing limit orders:

- 0.8%
- 1%
- 1.3%
- 1.5%
- 2%
- 3%
- 5%

## `config-example.json`
This is the config file. Rename it to `config.json` and add your `PORTFOLIO_UUID`, private key name (`NEW_KEY_NAME`) and secret (`NEW_KEY_SECRET`). 

```json
{
    "PRODUCT": "PEPE-USD",
    "PORTFOLIO_UUID": "",
    "USER_AGENT": "",
    "NEW_KEY_NAME": "",
    "NEW_KEY_SECRET": "",
    "CB_PRODUCT_DECIMALS": "8",
    "NUM_ORDERS": "1",
    "ENABLE_PROXY": "false",
    "PROXY_IP": "",
    "SELLMON_AUTO_REFRESH": "false"
}
```

| Field                      | Description                                                                                                                                                                                            |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **`PRODUCT`**              | `"PEPE-USD"` — The trading pair on Coinbase. This specifies the asset you're trading, in this case, PEPE token against USD. Used in API calls like placing orders, retrieving order book data, etc.    |
| **`PORTFOLIO_UUID`**       | Placeholder for a **Coinbase Advanced Trade portfolio UUID** (used in newer Coinbase API v3).                                                        |
| **`USER_AGENT`**           | User-Agent string sent with HTTP requests. Often used to mimic a browser or identify the client app.                                                                                                   |
| **`NEW_KEY_NAME`**         | Name or label of the API key. (Provided with API key from Coinbase)                                                                                              |
| **`NEW_KEY_SECRET`**       | Secret associated with the Coinbase API key. Used to sign requests for authenticated endpoints (placing orders, checking balances, etc.).                                                              |
| **`CB_PRODUCT_DECIMALS`**  | `"8"` — Number of decimal places for the product. Important when placing orders, as precision matters (especially for tokens like PEPE). Coinbase expects quantities/prices in correct decimal format. |
| **`NUM_ORDERS`**           | `"1"` — Defines how many orders the `pepe_buy_at_market.py` script places at a time.                                                                                    |
| **`ENABLE_PROXY`**         | `"false"` — Whether to route API traffic through a proxy (e.g., for privacy or geo-routing).                                                                                                           |
| **`PROXY_IP`**             | The IP address of the proxy server if `ENABLE_PROXY` is `"true"`.                                                                                                                                      |
| **`SELLMON_AUTO_REFRESH`** | `"false"` — Logic toggle related to `pepe_sell_mon.py` that auto-scans for new buy orders rather than using manual mode.                                               |


---

# DISCLAIMER

The trading scripts provided in this repository are for educational and informational purposes only. They are open source and freely available for use, modification, and distribution under the terms of the specified open source license.

No Financial Advice: These scripts are not intended as financial advice, investment advice, or trading recommendations. Users should not rely on these scripts to make financial, investment, or trading decisions. Please consult with a qualified financial advisor before engaging in any trading activities.

Risk of Loss: Trading involves substantial risk and may result in the loss of all invested capital. Past performance of any trading strategy or system does not guarantee future results. The authors and contributors of these scripts shall not be held liable for any losses, damages, or negative consequences resulting from the use or misuse of these scripts.

No Warranty: The scripts are provided "as is," without any warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, or non-infringement. The authors and contributors disclaim all liability for any errors or omissions in the scripts and for any damages arising from their use.

Third-Party Integrations: Some scripts may require integration with third-party services, platforms, or APIs. The authors are not responsible for the availability, accuracy, or security of any third-party services used in conjunction with these scripts.

User Responsibility: Users are solely responsible for complying with all applicable laws, regulations, and exchange rules while using these scripts. It is the user's responsibility to verify the accuracy, legality, and suitability of the scripts before using them in any trading activity.

Acknowledgment: By using these scripts, you acknowledge that you have read, understood, and agree to be bound by the terms of this disclaimer and the associated open source license.
