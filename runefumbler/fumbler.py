import argparse
import asyncio
import json
import os
import uvicorn

import random
import socket
import time
import pyautogui
import pygetwindow
from fastapi import FastAPI, Depends, HTTPException

app = FastAPI()

# Define the fumble_opp class for trading opportunities
class fumble_opp:
    def __init__(self, name, buy, sell, t):
        self.name = name
        self.buy = buy
        self.sell = sell
        self.time = t
        self.ttl = time.time() + 60

    def to_dict(self):
        return {
            "name": self.name,
            "buy": self.buy,
            "sell": self.sell,
            "time": self.time,
            "ttl": self.ttl,
        }

# Define Position class for tracking buy/sell positions
class Position:
    def __init__(self, buy_coord, sell_coord):
        self.buy_coord = buy_coord
        self.sell_coord = sell_coord
        self.state = "pending"
        self.name = ""
        self.buy_price = 0
        self.sell_price = 0

    def buy(self, opp: fumble_opp):
        self.name = opp.name
        self.buy_price = opp.buy
        self.sell_price = opp.sell
        self.state = "buying"
        x, y = self.buy_coord
        pyautogui.moveTo(random.randint(x - 10, x + 10), random.randint(y - 10, y + 10), random.uniform(0.1, 1), pyautogui.easeInOutSine)
        pyautogui.click()
        pyautogui.typewrite(self.name)

    def sell(self):
        if self.state != "buying":
            raise Exception("Can't sell if not in buying state")
        self.state = "selling"
        x, y = self.sell_coord
        pyautogui.moveTo(random.randint(x - 10, x + 10), random.randint(y - 10, y + 10), random.uniform(0.1, 1), pyautogui.easeInOutSine)
        pyautogui.click()
        pyautogui.typewrite(self.name)

    def to_dict(self):
        return {
            "buy_coord": self.buy_coord,
            "sell_coord": self.sell_coord,
            "state": self.state,
            "name": self.name,
            "buy_price": self.buy_price,
            "sell_price": self.sell_price,
        }

# Define the Trader class to handle trade management
class Trader:
    def __init__(self, username, slots=8):
        self.positions = []
        self.trade_opps = []
        self.username = username
        self.slots = slots

    def get_sell_buy_positions(self):
        time.sleep(2)
        buy = pyautogui.position()
        time.sleep(2)
        sell = pyautogui.position()
        self.positions.append(Position(buy, sell))

    def analyze_window(self):
        windows = pygetwindow.getAllWindows()
        for window in windows:
            if self.username in window.title:
                self.window = window
                break
        for i in range(self.slots):
            print(f"Please move your mouse to the buy position for slot {i + 1}")
            self.get_sell_buy_positions()
        self.window.activate()

    async def build_trade_opps(self, savant_input):
        split_string = savant_input.split(":")
        split_string = [s.strip() for s in split_string]
        opp = fumble_opp(split_string[0], split_string[1], split_string[2], split_string[3])
        if len(self.trade_opps) > self.slots and time.time() > self.trade_opps[0].ttl:
            stale = self.trade_opps.pop(0)
            print(f"Stale: {stale.name}")
        self.trade_opps.append(opp)

    async def update_trade_opps(self, connection):
        while True:
            data = connection.recv(1024)
            if data:
                await self.build_trade_opps(data.decode("utf-8"))
            else:
                print(f"No more data from {self.client_address}")
                break

    def get_opportunities(self):
        return json.dumps([opp.to_dict() for opp in self.trade_opps])

    def cancel_opportunity(self, number):
        self.trade_opps.pop(number)

    def get_positions(self):
        return json.dumps([position.to_dict() for position in self.positions])

    def function_buy(self, number):
        opp = self.trade_opps.pop(number)
        self.positions[number].buy(opp)

    def function_sell(self, number):
        self.positions[number].sell()

# Start server function
def start_server(trader, host="", port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (host, port)
    server_socket.bind(server_address)
    server_socket.listen(1)
    print(f"Starting server on {host}:{port}")
    print("Waiting for a connection...")
    connection, client_address = server_socket.accept()
    trader.client_address = client_address
    asyncio.create_task(trader.update_trade_opps(connection))
    asyncio.create_task(uvicorn.run(app, host=host, port=12346, log_level="info"))
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Closing server...")
    finally:
        connection.close()
        server_socket.close()

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Fumbler Time Baby")
    parser.add_argument("--host", default="192.168.1.70", help="Server IP address")
    parser.add_argument("--port", type=int, default=12345, help="Server port")
    parser.add_argument("--username", type=str, default="DavTF", help="Username of runescape account")
    parser.add_argument("--clean", action="store_true", help="Clear the screen position data")
    parser.add_argument("--slots", type=int, default=8, help="Number of inventory slots")
    return parser.parse_args()

# Main function to run the application
def main():
    args = parse_args()
    trader = Trader(username=args.username, slots=args.slots)

    # Define FastAPI routes
    def get_trader():
        return trader

    @app.get("/opportunities")
    async def get_opportunities(trader: Trader = Depends(get_trader)):
        return trader.get_opportunities()

    @app.post("/delete_opportunity/{number}")
    async def cancel_opportunity(number: int, trader: Trader = Depends(get_trader)):
        trader.cancel_opportunity(number)

    @app.get("/positions")
    async def get_positions(trader: Trader = Depends(get_trader)):
        return trader.get_positions()

    @app.post("/buy/{number}")
    async def function_buy(number: int, trader: Trader = Depends(get_trader)):
        trader.function_buy(number)

    @app.post("/sell/{number}")
    async def function_sell(number: int, trader: Trader = Depends(get_trader)):
        trader.function_sell(number)

    # Analyze the RuneScape window and get positions
    if args.clean or not os.path.exists("positions.json"):
        trader.analyze_window()
        with open("positions.json", "w") as f:
            json.dump([position.to_dict() for position in trader.positions], f)
    else:
        with open("positions.json", "r") as f:
            json_positions = json.load(f)
            if len(json_positions) != args.slots:
                print("Invalid number of positions in file, re-run with --clean")
                exit()
            trader.positions = [Position(**position) for position in json_positions]

    start_server(trader, args.host, args.port)

if __name__ == "__main__":
    main()