from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import os
import requests
import bot

app = Flask(__name__)
CORS(app)

thread = None


def get_ip():
    try:
        return requests.get("https://api.ipify.org").text
    except:
        return "Unavailable"


@app.route("/")
def home():
    return "Bot is running"


@app.route("/start", methods=["POST"])
def start():
    global thread

    data = request.json
    capital = float(data.get("capital", 10))
    target = float(data.get("target", 1000))
    mode = data.get("mode", "paper")

    if not bot.running:
        bot.running = True
        thread = threading.Thread(target=bot.run_bot, args=(capital, target, mode))
        thread.start()

    return jsonify({"status": "started"})


@app.route("/stop", methods=["POST"])
def stop():
    bot.running = False
    return jsonify({"status": "stopped"})


@app.route("/reset", methods=["POST"])
def reset():
    bot.balance = 0
    bot.trade_history.clear()
    return jsonify({"status": "reset"})


@app.route("/status")
def status():
    return jsonify({
        "running": bot.running,
        "balance": bot.get_balance() if bot.mode == "live" else bot.balance,
        "connection": bot.check_connection(),
        "trade": bot.current_trade,
        "history": bot.trade_history,
        "mode": bot.mode,
        "ip": get_ip()
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)