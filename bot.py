from binance.client import Client
import time
import os

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
    ticker = client.futures_symbol_ticker(symbol=SYMBOL)
    return float(ticker["price"])


def set_leverage():
    try:
        client.futures_change_leverage(symbol=SYMBOL, leverage=LEVERAGE)
    except:
        pass


def calculate_risk(balance):
    return max(balance * 0.01, 2)


def place_trade(side, qty):
    return client.futures_create_order(
        symbol=SYMBOL,
        side=side,
        type="MARKET",
        quantity=qty
    )


def close_trade():
    global current_trade

    if not current_trade:
        return

    side = "SELL" if current_trade["side"] == "BUY" else "BUY"

    client.futures_create_order(
        symbol=SYMBOL,
        side=side,
        type="MARKET",
        quantity=current_trade["qty"]
    )

    trade_history.append(current_trade)
    current_trade = None


def run_bot(start_capital, target, selected_mode):
    global running, balance, mode, current_trade

    mode = selected_mode
    balance = start_capital

    set_leverage()

    while running:

        price = get_price()

        if mode == "live":
            balance = get_balance()

        risk = calculate_risk(balance)
        qty = (risk * LEVERAGE) / price

        # SIMPLE SIGNAL (placeholder)
        signal = "BUY" if int(time.time()) % 2 == 0 else "SELL"

        if not current_trade:

            if mode == "paper":
                current_trade = {
                    "side": signal,
                    "entry": price,
                    "qty": qty,
                    "status": "OPEN"
                }

            else:
                try:
                    place_trade(signal, qty)

                    current_trade = {
                        "side": signal,
                        "entry": price,
                        "qty": qty,
                        "status": "OPEN"
                    }
                except Exception as e:
                    print("Trade error:", e)

        else:
            # CLOSE TRADE AFTER SMALL MOVE (SIMPLIFIED)
            if abs(price - current_trade["entry"]) / current_trade["entry"] > 0.002:

                current_trade["exit"] = price
                current_trade["status"] = "CLOSED"

                if mode == "live":
                    close_trade()
                else:
                    trade_history.append(current_trade)
                    current_trade = None

        time.sleep(5)

    running = False