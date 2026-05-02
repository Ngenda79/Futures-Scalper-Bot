from binance.client import Client
import pandas as pd
import time
import os

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)

running = False
balance = 0
mode = "paper"

SYMBOL = "BTCUSDT"
LEVERAGE = 3

def set_leverage():
    try:
        client.futures_change_leverage(symbol=SYMBOL, leverage=LEVERAGE)
    except:
        pass

def get_price():
    ticker = client.futures_symbol_ticker(symbol=SYMBOL)
    return float(ticker["price"])

def calculate_risk(balance):
    return max(balance * 0.01, 2)

def place_trade(side, qty):
    return client.futures_create_order(
        symbol=SYMBOL,
        side=side,
        type="MARKET",
        quantity=qty
    )

def run_bot(start_capital, target):
    global running, balance, mode

    balance = float(start_capital)

    set_leverage()

    while running and balance < target:

        price = get_price()
        risk = calculate_risk(balance)
        qty = (risk * LEVERAGE) / price

        # SIMPLE SIGNAL (placeholder)
        signal = "BUY" if int(time.time()) % 2 == 0 else "SELL"

        if mode == "paper":
            profit = risk * 0.5
            balance += profit

        else:
            try:
                order = place_trade(signal, qty)

                # simulate TP hit
                profit = risk * 0.021
                balance += profit

            except Exception as e:
                print("Trade error:", e)

        time.sleep(10)

    running = False