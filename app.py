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

# ------------------ IP ------------------

def get_ip():
    try:
        return requests.get("https://api.ipify.org").text
    except:
        return "Unavailable"

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    return "Bot is running"

@app.route("/start", methods=["POST"])
def start():
    global thread

    data = request.json or {}

    if data.get("password") != PASSWORD:
        return jsonify({"error": "Unauthorized"}), 403

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
    bot.balance = 0.0
    bot.trade_history = []
    bot.current_trade = {}
    return jsonify({"status": "reset"})

@app.route("/status")
def status():

    try:
        balance = bot.get_balance() if bot.mode == "live" else bot.balance
    except:
        balance = 0.0

    try:
        connection = bot.check_connection()
    except:
        connection = "Error"

    return jsonify({
        "running": bool(bot.running),
        "balance": float(balance),
        "connection": connection,
        "trade": bot.current_trade if isinstance(bot.current_trade, dict) else {},
        "history": bot.trade_history if isinstance(bot.trade_history, list) else [],
        "mode": bot.mode if bot.mode else "paper",
        "ip": get_ip()
    })

# ------------------ RUN ------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)