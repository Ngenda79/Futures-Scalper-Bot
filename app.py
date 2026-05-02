from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import bot
import os
import requests

app = Flask(__name__)
CORS(app)

thread = None
PASSWORD = os.getenv("BOT_PASSWORD")


def get_ip():
    try:
        return requests.get("https://api.ipify.org").text
    except:
        return "Unavailable"


@app.route("/start", methods=["POST"])
def start():
    global thread

    data = request.json

    if data.get("password") != PASSWORD:
        return jsonify({"error": "Wrong password"}), 403

    capital = float(data.get("capital", 10))
    target = float(data.get("target", 1000))
    mode = data.get("mode", "paper")

    if not bot.running:
        bot.running = True
        thread = threading.Thread(
            target=bot.run_bot,
            args=(capital, target, mode)
        )
        thread.start()

    return jsonify({"status": "started"})


@app.route("/stop", methods=["POST"])
def stop():
    bot.running = False
    return jsonify({"status": "stopped"})


@app.route("/reset", methods=["POST"])
def reset():
    bot.balance = 0
    bot.trade_history = []
    bot.current_trade = {}
    return jsonify({"status": "reset"})


@app.route("/status")
def status():
    return jsonify({
        "running": bot.running,
        "balance": float(bot.balance),
        "connection": bot.check_connection(),
        "trade": bot.current_trade if bot.current_trade else {},
        "history": bot.trade_history if bot.trade_history else [],
        "mode": bot.mode,
        "ip": get_ip()
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)