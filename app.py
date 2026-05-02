from flask import Flask, jsonify
from binance.client import Client
import pandas as pd
import time
import threading
import os

app = Flask(__name__)

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)

SYMBOL = "BTCUSDT"
QTY = 0.001
INTERVAL = Client.KLINE_INTERVAL_5MINUTE

bot_status = False

# === INDICATORS ===
def get_data():
    klines = client.get_klines(symbol=SYMBOL, interval=INTERVAL, limit=100)
    df = pd.DataFrame(klines, columns=[
        "time","open","high","low","close","volume",
        "ct","qv","n","tbbav","tbqav","ignore"
    ])
    df["close"] = df["close"].astype(float)
    return df

def apply_strategy(df):
    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()

    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    last = df.iloc[-1]
    prev = df.iloc[-2]

    buy = (
        last["ema20"] > last["ema50"] and
        40 < last["rsi"] < 60 and
        last["close"] > prev["high"]
    )

    sell = (
        last["ema20"] < last["ema50"] and
        40 < last["rsi"] < 60 and
        last["close"] < prev["low"]
    )

    return "BUY" if buy else "SELL" if sell else None

# === TRADING LOOP ===
def trading_loop():
    global bot_status

    while True:
        if bot_status:
            try:
                df = get_data()
                signal = apply_strategy(df)

                if signal == "BUY":
                    client.order_market_buy(symbol=SYMBOL, quantity=QTY)
                    print("BUY executed")

                elif signal == "SELL":
                    client.order_market_sell(symbol=SYMBOL, quantity=QTY)
                    print("SELL executed")

            except Exception as e:
                print("Error:", e)

        time.sleep(60)

# === CONTROL ROUTES ===
@app.route("/start", methods=["POST"])
def start():
    global bot_status
    bot_status = True
    return {"status": "Bot started"}

@app.route("/stop", methods=["POST"])
def stop():
    global bot_status
    bot_status = False
    return {"status": "Bot stopped"}

@app.route("/status")
def status():
    return {"bot": bot_status}

# === START THREAD ===
threading.Thread(target=trading_loop).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)