from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import requests
import os

from bot import run_bot, running, balance, mode

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

    from bot import running
    if not running:
        import bot
        bot.running = True
        thread = threading.Thread(target=run_bot, args=(capital, target))
        thread.start()

    return jsonify({"status": "started"})

@app.route("/stop", methods=["POST"])
def stop():
    import bot
    bot.running = False
    return jsonify({"status": "stopped"})

@app.route("/reset", methods=["POST"])
def reset():
    import bot
    bot.balance = 0
    return jsonify({"status": "reset"})

@app.route("/status")
def status():
    import bot
    return jsonify({
        "running": bot.running,
        "balance": bot.balance,
        "mode": bot.mode,
        "ip": get_ip()
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)