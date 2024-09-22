import argparse
import asyncio
import json
import os
import random
import socket
import time
import tkinter as tk

import pyautogui
import pygetwindow
import uvicorn
from fastapi import Depends, FastAPI


def parse_args():
    parser = argparse.ArgumentParser(description="Fumbler Time Baby")
    parser.add_argument(
        "--host", default="192.168.1.70", help="Server IP address"
    )
    parser.add_argument("--port", type=int, default=12345, help="Server port")
    parser.add_argument(
        "--username",
        type=str,
        default="DavTF",
        help="Username of runescape account",
    )
    parser.add_argument(
        "--clean", action="store_true", help="Clear the screen postion data"
    )
    parser.add_argument(
        "--slots", type=int, default=8, help="Number of inventory slots"
    )
    return parser.parse_args()


class fumble_opp:
    def __init__(self, name, buy, sell, t):
        self.name = name
        self.buy = buy
        self.sell = sell
        self.time = t
        self.ttl = time.time() + 60

    def show(self):
        print("Name: " + self.name)
        print("Buy At: " + self.buy)
        print("Sell At: " + self.sell)
        print("Time In Pos: " + self.time)

    def to_dict(self):
        return {
            "name": self.name,
            "buy": self.buy,
            "sell": self.sell,
            "time": self.time,
            "ttl": self.ttl,
        }


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
        x = self.buy_coord[0]
        y = self.buy_coord[1]
        pyautogui.moveTo(
            random.randint(x - 10, x + 10),
            random.randint(y - 10, y + 10),
            random.uniform(0.1, 1),
            pyautogui.easeInOutSine,
        )
        pyautogui.click()
        pyautogui.typewrite(self.name)

    def sell(self):
        if self.state != "buying":
            raise Exception("Can't sell if not in buying state")
        self.state = "selling"
        x = self.sel_coord[0]
        y = self.sel_coord[1]
        pyautogui.moveTo(
            random.randint(x - 10, x + 10),
            random.randint(y - 10, y + 10),
            random.uniform(0.1, 1),
            pyautogui.easeInOutSine,
        )
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


app = FastAPI()


class Trader:
    def __init__(self, username, slots=8):
        self.positions: list[Position] = []
        self.trade_opps = []
        self.x = -1
        self.y = -1
        self.w = -1
        self.h = -1
        self.username = username
        self.slots = slots

    def get_sell_buy_positions(self):
        time.sleep(2)
        buy = pyautogui.position()
        print(buy)
        time.sleep(2)
        sell = pyautogui.position()
        print(sell)
        self.positions.append(Position(buy, sell))

    def analyze_window(self):
        # Since it puts your username there might as well search for it.
        windows: list[pygetwindow.Win32Window] = pygetwindow.getAllWindows()
        for window in windows:
            if self.username in window.title:
                self.window = window
                break

        for i in range(0, self.slots):
            print(
                f"Please move your mouse to the buy position for slot {i + 1}"
            )
            self.get_sell_buy_positions()

        self.window.activate()
        return

    async def build_trade_opps(self, savant_input):
        split_string = savant_input.split(":")
        split_string = [s.strip() for s in split_string]
        opp = fumble_opp(
            split_string[0], split_string[1], split_string[2], split_string[3]
        )
        if len(self.trade_opps) > self.slots:
            if time.time() > self.trade_opps[0].ttl:
                stale = self.trade_opps.pop(0)
                print("Stale: " + stale.name)
            else:
                print("No slots available")
                return

        self.trade_opps.append(opp)

    async def update_trade_opps(self, connection):
        try:
            while True:
                data = await asyncio.to_thread(
                    connection.recv, 1024
                )  # use asyncio.to_thread to avoid blocking
                if data:
                    await self.build_trade_opps(data.decode("utf-8"))
                else:
                    print(f"No more data from {self.client_address}")
                    break
        except Exception as e:
            print(f"Error updating trade opportunities: {e}")
        finally:
            connection.close()

    def get_opportunities(self):
        print("Getting opportunities")
        return json.dumps([opp.to_dict() for opp in self.trade_opps])

    def cancel_opportunity(self, number):
        self.trade_opps.pop(number)

    def get_positions(self):
        return json.dumps([position.to_dict() for position in self.positions])

    def function_buy(self, number):
        opp: fumble_opp = self.trade_opps.pop(number)
        self.positions[number].buy(opp)
        print("Buy: " + str(opp.buy))
        print("Sell: " + str(opp.sell))
        print("Name: " + opp.name)
        print(f"Buy on inv slot {number + 1}")

    def function_sell(self, number):
        print(f"Sell on slot {number + 1}")
        self.positions[number].sell()

    def function_collect(self, number):
        print(f"Collect on slot {number}")
        # random sell or buy
        # random click pos

    def function_exit(self, number):
        print(f"Exit on slot {number}")
        # random sell or buy
        # random click pos


def start_server(trader: Trader, host="", port=12345):
    # Create a TCP/IP socket
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )

    # Bind the socket to the address and port
    server_address = (host, port)
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(1)
    print(f"Starting server on {host}:{port}")

    # Wait for a connection
    print("Waiting for a connection...")
    connection, client_address = server_socket.accept()
    trader.client_address = client_address

    # Properly schedule the trader update function
    asyncio.ensure_future(trader.update_trade_opps(connection))

    # Start the uvicorn server as a background task
    asyncio.ensure_future(
        uvicorn.run(app, host=host, port=12346, log_level="info")
    )

    loop = asyncio.get_event_loop()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Closing server...")
    finally:
        # Clean up the connection
        connection.close()


def main():
    args = parse_args()
    trader = Trader(username=args.username, slots=args.slots)

    def get_trader():
        return trader

    @app.get("/opportunities")
    async def get_opportunities(trader: Trader = Depends(get_trader)):
        return trader.get_opportunities()

    @app.post("/delete_opportunity/{number}")
    async def cancel_opportunity(number, trader: Trader = Depends(get_trader)):
        trader.cancel_opportunity(number)

    @app.get("/positions")
    async def get_positions(trader: Trader = Depends(get_trader)):
        return trader.get_positions()

    @app.post("/buy/{number}")
    async def function_buy(number, trader: Trader = Depends(get_trader)):
        trader.function_buy(number)

    @app.post("/sell/{number}")
    async def function_sell(number, trader: Trader = Depends(get_trader)):
        trader.function_sell(number)

    @app.post("/collect/{number}")
    async def function_collect(number, trader: Trader = Depends(get_trader)):
        trader.function_collect(number)

    @app.post("/exit/{number}")
    async def function_exit(number, trader: Trader = Depends(get_trader)):
        trader.function_exit(number)

    if args.clean or not os.path.exists("positions.json"):
        trader.analyze_window()
        with open("positions.json", "w") as f:
            json_positions = [
                position.to_dict() for position in trader.positions
            ]
            json.dump(json_positions, f)
    else:
        with open("positions.json", "r") as f:
            json_positons = json.load(f)
            if len(json_positons) != args.slots:
                print(
                    "Invalid number of positions in file, re-run with --clean"
                )
                exit()
            trader.positions = [
                Position(
                    buy_coord=position["buy_coord"],
                    sell_coord=position["sell_coord"],
                )
                for position in json_positons
            ]

    start_server(trader, args.host)


if __name__ == "__main__":
    main()

"""
Mutex lock for whether or not we're currently executing an action
UI:
1. Store information on the positions of the RS screen
2. "queue of active trade"
3. Enter letter combo "1b" = enter position for queue place 1, lock to queue "1" for that inventory slot
4. Execute in RS
5. Return control immediately back to the terminal for the python interface
6. Enter or exit trades "2b" is another enter, "1b" is exit and collect all regardless of fill
7. Repeat and make tons of fake money


Two queues, one for active trades, one for most recent potential trades from server. As soon as a slot is filled and exited
we repopulate that position from the most active list. 
"""

"""
Window Sizes:
480 x 240 - main
115 x 105 - slot
115 x 105 - slot


"""
