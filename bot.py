import time

running = False
balance = 0
mode = "paper"

def calculate_risk(balance):
    return max(balance * 0.01, 2)

def run_bot(start_capital, target):
    global running, balance

    balance = float(start_capital)

    while running and balance < target:
        risk = calculate_risk(balance)

        # PAPER MODE SIMULATION
        profit = risk * 0.5

        balance += profit

        time.sleep(5)

    running = False