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

---

# DISCLAIMER

The trading scripts provided in this repository are for educational and informational purposes only. They are open source and freely available for use, modification, and distribution under the terms of the specified open source license.

No Financial Advice: These scripts are not intended as financial advice, investment advice, or trading recommendations. Users should not rely on these scripts to make financial, investment, or trading decisions. Please consult with a qualified financial advisor before engaging in any trading activities.

Risk of Loss: Trading involves substantial risk and may result in the loss of all invested capital. Past performance of any trading strategy or system does not guarantee future results. The authors and contributors of these scripts shall not be held liable for any losses, damages, or negative consequences resulting from the use or misuse of these scripts.

No Warranty: The scripts are provided "as is," without any warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, or non-infringement. The authors and contributors disclaim all liability for any errors or omissions in the scripts and for any damages arising from their use.

Third-Party Integrations: Some scripts may require integration with third-party services, platforms, or APIs. The authors are not responsible for the availability, accuracy, or security of any third-party services used in conjunction with these scripts.

User Responsibility: Users are solely responsible for complying with all applicable laws, regulations, and exchange rules while using these scripts. It is the user's responsibility to verify the accuracy, legality, and suitability of the scripts before using them in any trading activity.

Acknowledgment: By using these scripts, you acknowledge that you have read, understood, and agree to be bound by the terms of this disclaimer and the associated open source license.
