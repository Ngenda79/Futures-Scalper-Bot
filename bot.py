from binance.client import Client
import os
import time

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)

running = False
mode = "paper"

SYMBOL = "BTCUSDT"
LEVERAGE = 3

balance = 0
trade_history = []
current_trade = None


def check_connection():
    try:
        client.ping()
        return "Connected"
    except:
        return "Disconnected"


def get_balance():
    try:
        balances = client.futures_account_balance()
        for b in balances:
            if b["asset"] == "USDT":
                return float(b["balance"])
    except:
        return 0


def get_price():
    return float(client.futures_symbol_ticker(symbol=SYMBOL)["price"])


def calculate_risk(balance):
    return max(balance * 0.01, 2)


def place_trade(side, qty):
    return client.futures_create_order(
        symbol=SYMBOL,
        side=side,
        type="MARKET",
        quantity=round(qty, 3)
    )


def run_bot(start_capital, target, selected_mode):
    global running, balance, mode, current_trade

    mode = selected_mode
    balance = float(start_capital)

    while running:

        price = get_price()

        if mode == "live":
            balance = get_balance()

        risk = calculate_risk(balance)
        qty = (risk * LEVERAGE) / price

        signal = "BUY" if int(time.time()) % 2 == 0 else "SELL"

        # OPEN TRADE
        if current_trade is None:

            if mode == "live":
                try:
                    place_trade(signal, qty)
                except Exception as e:
                    print("Trade error:", e)
                    time.sleep(5)
                    continue

            current_trade = {
                "side": signal,
                "entry": price,
                "qty": qty,
                "status": "OPEN"
            }

        # CLOSE TRADE (simple movement)
        else:
            move = abs(price - current_trade["entry"]) / current_trade["entry"]

            if move > 0.002:
                current_trade["exit"] = price
                current_trade["status"] = "CLOSED"

                trade_history.append(current_trade)
                current_trade = None

        time.sleep(5)

    running = False