import argparse
import asyncio
import json
import os
import random
import socket
import threading
import time
import tkinter as tk

import pyautogui
import pygetwindow
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

DEFAULT_QUANTITY = "1000"


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
        self.buy = int(buy)
        self.sell = int(sell)
        self.time = int(t)
        self.ttl = time.time() + 10

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
    def __init__(
        self,
        buy_coord,
        sell_coord,
        set_price_coord,
        set_quantity_coord,
        confirm_coord,
        inventory_coord,
        parent_window,
    ):
        self.buy_coord = buy_coord
        self.sell_coord = sell_coord
        self.set_price_coord = set_price_coord
        self.set_quantity_coord = set_quantity_coord
        self.confirm_coord = confirm_coord
        self.inventory_coord = inventory_coord
        self.state = "pending"
        self.name = ""
        self.buy_price = 0
        self.sell_price = 0
        self.parent_window = parent_window

    def buy(self, opp: fumble_opp):
        self.name = opp.name
        self.buy_price = opp.buy
        self.sell_price = opp.sell
        self.state = "buying"
        x = self.buy_coord[0]
        y = self.buy_coord[1]
        self.trade(x, y, self.buy_price)

    def sell(self):
        if self.state != "buying":
            raise Exception("Can't sell if not in buying state")
        self.state = "selling"
        x = self.sel_coord[0]
        y = self.sel_coord[1]
        self.trade(x, y, self.sell_price)

    def collect(self):
        # how do we want to do this
        print("Hello")

    def to_dict(self):
        return {
            "buy_coord": self.buy_coord,
            "sell_coord": self.sell_coord,
            "set_price_coord": self.set_price_coord,
            "set_quantity_coord": self.set_quantity_coord,
            "confirm_coord": self.confirm_coord,
            "inventory_coord": self.inventory_coord,
            "state": self.state,
            "name": self.name,
            "buy_price": self.buy_price,
            "sell_price": self.sell_price,
        }

    def trade(self, x: int, y: int, price: int):
        self.move_to_x_y(x, y, 10)
        pyautogui.click()
        # activate window and type name
        self.price_and_enter(self.name)
        # Go to set price
        self.move_to_x_y(self.set_price_coord[0], self.set_price_coord[1], 3)
        pyautogui.click()
        self.price_and_enter(str(price))
        # Go to set quantity
        self.move_to_x_y(
            self.set_quantity_coord[0], self.set_quantity_coord[1], 3
        )
        pyautogui.click()
        self.price_and_enter(DEFAULT_QUANTITY)
        # Go to confirm
        self.move_to_x_y(self.confirm_coord[0], self.confirm_coord[1], 5)
        pyautogui.click()
        self.parent_window.activate()
        time.sleep(random.uniform(0.25, 1))

    def price_and_enter(self, input: str):
        self.parent_window.activate()
        time.sleep(random.uniform(0.5, 1))
        pyautogui.typewrite(input, interval=random.uniform(0.2, 0.3))
        time.sleep(random.uniform(0.5, 1))
        pyautogui.typewrite(["enter"])
        time.sleep(random.uniform(0.5, 1))

    def move_to_x_y(self, x: int, y: int, adjustment: int):
        pyautogui.moveTo(
            x=random.randint(x - adjustment, x + adjustment),
            y=random.randint(y - adjustment, y + adjustment),
            duration=random.uniform(0.5, 1),
            tween=pyautogui.easeInOutSine,
        )


app = FastAPI()
# Define the allowed origins
origins = [
    "http://localhost",
    "http://localhost:5173",
]
# Add CORS middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Origins that are allowed to make requests
    allow_credentials=True,  # Allow cookies and authorization headers
    allow_methods=["*"],  # HTTP methods allowed (e.g., GET, POST)
    allow_headers=["*"],  # HTTP headers allowed
)


class Trader:
    def __init__(self, username, slots=8):
        self.window = None
        self.positions: list[Position] = []
        self.trade_opps = []
        self.x = -1
        self.y = -1
        self.w = -1
        self.h = -1
        self.username = username
        self.slots = slots
        self.client_address = None

    def get_sell_buy_positions(
        self, set_price, set_quantity, confirm, inventory
    ):
        time.sleep(2)
        buy = pyautogui.position()
        print(buy)
        print("Please move your mouse to the sell position")
        time.sleep(2)
        sell = pyautogui.position()
        print(sell)
        self.positions.append(
            Position(
                buy,
                sell,
                set_price,
                set_quantity,
                confirm,
                inventory,
                self.window,
            )
        )

    def get_runescape_window(self):
        # Since it puts your username there might as well search for it.
        # Get set price coord
        windows: list[pygetwindow.Win32Window] = pygetwindow.getAllWindows()
        for window in windows:
            if self.username in window.title:
                self.window = window
                break

    def analyze_window(self):
        self.get_runescape_window()
        if self.window is None:
            raise Exception("Window not found - Run runescape Nerd")
        self.window.activate()
        print("Please move your mouse to the set price position")
        time.sleep(5)
        set_price = pyautogui.position()
        print(set_price)
        print("Please move your mouse to set quantity position")
        time.sleep(2)
        set_quantity = pyautogui.position()
        print(set_quantity)
        print("Please move your mouse to the confirm position")
        time.sleep(2)
        confirm = pyautogui.position()
        print(confirm)
        print("Please move your mouse to the inventory position")
        time.sleep(2)
        inventory = pyautogui.position()
        print(inventory)
        print("Please go back to the main trading screen")
        time.sleep(2)
        for i in range(0, self.slots):
            print(
                f"Please move your mouse to the buy position for slot {i + 1}"
            )
            self.get_sell_buy_positions(
                set_price=set_price,
                set_quantity=set_quantity,
                confirm=confirm,
                inventory=inventory,
            )

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
        print(f"Added trade opportunity: {opp.to_dict()}")  # Debugging log

    async def update_trade_opps(self, connection):
        try:
            while True:
                data = await asyncio.to_thread(connection.recv, 1024)
                if data:
                    print(
                        f"Received data: {data.decode('utf-8')}"
                    )  # Debugging log
                    await self.build_trade_opps(data.decode("utf-8"))
                else:
                    print("No more data from", self.client_address)
                    break
        except asyncio.CancelledError:
            print("Task cancelled")
        except Exception as e:
            print(f"Error in update_trade_opps: {e}")
        finally:
            connection.close()

    def get_opportunities(self):
        print("Getting opportunities")
        return [opp.to_dict() for opp in self.trade_opps]

    def cancel_opportunity(self, number):
        number = int(number)
        print(f"Canceling opportunity {number}")
        self.trade_opps.pop(number)

    def get_positions(self):
        return [position.to_dict() for position in self.positions]

    def function_buy(self, number):
        number = int(number)
        opp: fumble_opp = self.trade_opps.pop(number)
        # Find the next open position
        position_number = -1
        for position in self.positions:
            if position.state == "pending":
                position_number = self.positions.index(position)
                break
        if position_number == -1:
            print("No open positions")
            return
        else:
            self.positions[number].buy(opp)
            print("Buy: " + str(opp.buy))
            print("Sell: " + str(opp.sell))
            print("Name: " + opp.name)
            print(f"Buy on inv slot {number + 1}")

    def function_sell(self, number):
        number = int(number)
        print(f"Sell on slot {number + 1}")
        self.positions[number].sell()

    def function_collect(self, number):
        number = int(number)
        print(f"Collect on slot {number}")
        # random sell or buy
        # random click pos

    def function_exit(self, number):
        number = int(number)
        # reinstatiate the position as a new position
        print(f"Exit on slot {number}")
        self.positions[number] = Position(
            self.positions[number].buy_coord,
            self.positions[number].sell_coord,
            self.positions[number].set_price_coord,
            self.positions[number].set_quantity_coord,
            self.positions[number].confirm_coord,
            self.positions[number].inventory_coord,
            parent_window=self.window,
        )


def run_uvicorn():
    """Run the web server in a separate thread."""
    uvicorn.run(app, host="localhost", port=12346, log_level="info")


async def start_update_trade_opps(trader, connection):
    """Start the update_trade_opps coroutine."""
    try:
        await trader.update_trade_opps(connection)
    except asyncio.CancelledError:
        print("update_trade_opps cancelled")
    except Exception as e:
        print(f"Error in update_trade_opps: {e}")


async def main_server(trader, host, port):
    """Main function to manage server socket and async tasks."""
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the address and port
    server_address = (host, port)
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(1)
    server_socket.settimeout(1)
    print(f"Starting server on {host}:{port}")
    print("Waiting for a connection...")

    # Start Uvicorn server in a thread
    uvicorn_thread = threading.Thread(target=run_uvicorn, daemon=True)
    uvicorn_thread.start()
    try:
        while True:
            try:
                connection, client_address = server_socket.accept()
                print(f"Connection accepted from {client_address}")
                trader.client_address = client_address
                # Start the update_trade_opps coroutine forever
                while True:
                    await start_update_trade_opps(trader, connection)

            except socket.timeout:
                pass
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        print("Server socket closed.")


def main():
    args = parse_args()
    trader = Trader(username=args.username, slots=args.slots)

    def get_trader():
        return trader

    @app.get("/opportunities")
    async def get_opportunities(trader: Trader = Depends(get_trader)):
        print(
            f"Trade opportunities: {trader.get_opportunities()}"
        )  # Debugging log
        return trader.get_opportunities()

    @app.post("/delete_opportunity/{number}")
    async def cancel_opportunity(number, trader: Trader = Depends(get_trader)):
        print(f"Canceling opportunity {number}")
        trader.cancel_opportunity(number)

    @app.get("/positions")
    async def get_positions(trader: Trader = Depends(get_trader)):
        return trader.get_positions()

    @app.post("/buy/{number}")
    async def function_buy(number, trader: Trader = Depends(get_trader)):
        if trader.positions[int(number)].state != "pending":
            return "Position is not in pending state"
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
            trader.get_runescape_window()
            trader.positions = [
                Position(
                    buy_coord=position["buy_coord"],
                    sell_coord=position["sell_coord"],
                    set_price_coord=position["set_price_coord"],
                    set_quantity_coord=position["set_quantity_coord"],
                    confirm_coord=position["confirm_coord"],
                    inventory_coord=position["inventory_coord"],
                    parent_window=trader.window,
                )
                for position in json_positons
            ]

    asyncio.run(main_server(trader, args.host, args.port))


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
