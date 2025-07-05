import argparse
import asyncio
import json
import os
import random
import socket
import threading
import time
import tkinter as tk
from enum import StrEnum

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
    parser.add_argument(
        "--auto", action="store_true", help="Let the trader function on its own"
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


class PositionStates(StrEnum):
    PENDING = "pending"
    BUYING = "buying"
    COLLECTING = "collecting"
    SELLING = "selling"


class Position:
    def __init__(
        self,
        buy_coord,
        sell_coord,
        set_price_coord,
        set_quantity_coord,
        confirm_coord,
        inventory_coord,
        collect_coord,
        parent_window,
    ):
        self.buy_coord = buy_coord
        self.sell_coord = sell_coord
        self.set_price_coord = set_price_coord
        self.set_quantity_coord = set_quantity_coord
        self.confirm_coord = confirm_coord
        self.inventory_coord = inventory_coord
        self.collect_coord = collect_coord
        self.state = PositionStates.PENDING
        self.name = ""
        self.buy_price = 0
        self.sell_price = 0
        self.parent_window = parent_window

    def buy(self, opp: fumble_opp):
        self.name = opp.name
        self.buy_price = opp.buy
        self.sell_price = opp.sell
        self.state = PositionStates.BUYING
        x = self.buy_coord[0]
        y = self.buy_coord[1]
        self.trade(x, y, self.buy_price)

    def sell(self):
        if self.state != PositionStates.COLLECTING:
            raise Exception("Can't sell if not in collecting state")
        self.state = PositionStates.SELLING
        x = self.sell_coord[0]
        y = self.sell_coord[1]
        self.trade(x, y, self.sell_price)

    def collect(self):
        # how do we want to do this
        self.state = PositionStates.COLLECTING
        x = self.collect_coord[0]
        y = self.collect_coord[1]
        self.move_to_x_y(x, y, 1)
        pyautogui.click()

    def to_dict(self):
        # If you add a field - Make sure to add it here
        return {
            "buy_coord": self.buy_coord,
            "sell_coord": self.sell_coord,
            "set_price_coord": self.set_price_coord,
            "set_quantity_coord": self.set_quantity_coord,
            "confirm_coord": self.confirm_coord,
            "inventory_coord": self.inventory_coord,
            "collect_coord": self.collect_coord,
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
            tween=pyautogui.easeInOutElastic,
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
    def __init__(self, username, slots=8, auto=False):
        self.window = None
        self.positions: list[Position] = []
        self.trade_opps = list[fumble_opp] = []
        self.x = -1
        self.y = -1
        self.w = -1
        self.h = -1
        self.username = username
        self.slots = slots
        self.client_address = None
        self.auto = auto
        self.trade_mutex = threading.Lock()

    def get_sell_buy_positions(
        self, set_price, set_quantity, confirm, inventory, collect
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
                collect,
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
        time.sleep(5)
        print(
            "Please move your mouse to the collect position - 3 pixels above the top right edge of slot 4"
        )
        time.sleep(2)
        collect = pyautogui.position()
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
                collect=collect,
            )

        self.window.activate()
        return

    async def build_trade_opps(self, savant_input):
        # Message is in the fomrmat of (name:buy:sell:time|)
        ops = savant_input.split("|")
        for s_i in ops:
            if not s_i:
                continue
            split_string = s_i.split(":")
            split_string = [s.strip() for s in split_string]
            if len(split_string) != 4:
                print(f"Invalid input: {split_string}")
                continue
            opp = fumble_opp(
                split_string[0],
                split_string[1],
                split_string[2],
                split_string[3],
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
            exit()
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

    def function_buy(self, position_number, opp_number):
        self.trade_mutex.acquire()
        opp: fumble_opp = self.trade_opps.pop(opp_number)
        self.positions[position_number].buy(opp)
        self.trade_mutex.release()
        print("Buy: " + str(opp.buy))
        print("Sell: " + str(opp.sell))
        print("Name: " + opp.name)
        print(f"Buy on inv slot {position_number + 1}")

    def function_sell(self, number):
        number = int(number)
        print(f"Sell on slot {number + 1}")
        self.trade_mutex.acquire()
        self.positions[number].sell()
        self.trade_mutex.release()

    def function_collect(self, number):
        number = int(number)
        print(f"Collect on slot {number}")
        self.trade_mutex.acquire()
        self.positions[number].collect()
        self.trade_mutex.release()

    def instatiate_pos(self, number):
        self.positions[number] = Position(
            self.positions[number].buy_coord,
            self.positions[number].sell_coord,
            self.positions[number].set_price_coord,
            self.positions[number].set_quantity_coord,
            self.positions[number].confirm_coord,
            self.positions[number].inventory_coord,
            self.positions[number].collect_coord,
            parent_window=self.window,
        )

    def function_exit(self, number):
        number = int(number)
        # reinstatiate the position as a new position
        print(f"Exit on slot {number}")
        self.instatiate_pos(number)

    def auto_trade(self):
        pos: Position
        opp: fumble_opp
        for slot, pos in enumerate(self.positions):
            match pos.state:
                case PositionStates.BUYING:
                    # Need to see if our buy has finished (Requires CV)
                    buy_finished = True
                    if buy_finished:
                        self.function_collect(slot)
                        self.function_sell(slot)
                case PositionStates.SELLING:
                    # Need to use CV to see if its finished
                    sell_finished = True
                    if sell_finished:
                        # Get that money money
                        self.function_collect(slot)
                        # Clear pos now:
                        self.instatiate_pos(slot)
                case PositionStates.PENDING:
                    # Get the opp on the back of the queue
                    number_of_opps = len(self.trade_opps)
                    # TODO: We could make this smarter
                    self.function_buy(slot, number_of_opps - 1)


def run_autotrader(trader):
    while True:
        trader.auto_trade()
        time.sleep(1)


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

    # Start autotrade if set
    if trader.auto:
        trading_thread = threading.Thread(target=run_autotrader)
        trading_thread.start()
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
    trader = Trader(username=args.username, slots=args.slots, auto=args.auto)

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
        # Find an open position if we have one other return Position is not in pending state
        number = int(number)
        idx = 0
        position_number = None
        for position in trader.positions:
            if position.state == "pending":
                position_number = idx
                break
            idx += 1
        if position_number is None:
            return "Position is not in pending state"
        trader.function_buy(opp_number=number, position_number=position_number)

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
        # TODO: Move to using opencv_positions.py @Connor
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
                    collect_coord=position["collect_coord"],
                    inventory_coord=position["inventory_coord"],
                    parent_window=trader.window,
                )
                for position in json_positons
            ]

    asyncio.run(main_server(trader, args.host, args.port))


if __name__ == "__main__":
    main()
