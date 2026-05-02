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

balance = 0.0
trade_history = []
current_trade = {}

# ------------------ CONNECTION ------------------

def check_connection():
    try:
        client.ping()
        return "Connected"
    except Exception:
        return "Disconnected"

# ------------------ BALANCE ------------------

def get_balance():
    try:
        balances = client.futures_account_balance()
        for b in balances:
            if b["asset"] == "USDT":
                return float(b["balance"])
    except Exception:
        return 0.0

# ------------------ PRICE ------------------

def get_price():
    try:
        return float(client.futures_symbol_ticker(symbol=SYMBOL)["price"])
    except Exception:
        return 0.0

# ------------------ RISK ------------------

def calculate_risk(bal):
    try:
        return max(bal * 0.01, 2)
    except:
        return 2

# ------------------ ORDER ------------------

def place_trade(side, qty):
    try:
        return client.futures_create_order(
            symbol=SYMBOL,
            side=side,
            type="MARKET",
            quantity=round(qty, 3)
        )
    except Exception as e:
        print("Order error:", e)
        return None

# ------------------ BOT LOOP ------------------

def run_bot(start_capital, target, selected_mode):
    global running, balance, mode, current_trade, trade_history

    mode = selected_mode
    balance = float(start_capital)

    while running:

        price = get_price()

        # update live balance
        if mode == "live":
            balance = get_balance()

        risk = calculate_risk(balance)

        qty = (risk * LEVERAGE) / price if price > 0 else 0

        signal = "BUY" if int(time.time()) % 2 == 0 else "SELL"

        # ------------------ OPEN TRADE ------------------
        if not current_trade:

            if mode == "live" and qty > 0:
                order = place_trade(signal, qty)
                if order is None:
                    time.sleep(5)
                    continue

            current_trade = {
                "side": signal,
                "entry": price,
                "qty": qty,
                "status": "OPEN",
                "time": int(time.time())
            }

        # ------------------ CLOSE TRADE ------------------
        else:
            entry = current_trade.get("entry", 0)

            if entry > 0:
                move = abs(price - entry) / entry
            else:
                move = 0

            if move > 0.002:  # ~0.2% move

                current_trade["exit"] = price
                current_trade["status"] = "CLOSED"

                trade_history.append(current_trade)

                current_trade = {}

        time.sleep(5)

    running = False