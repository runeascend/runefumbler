import argparse
import json
import os
import random
import socket
import time
import threading
import pyautogui
import pygetwindow
import tkinter as tk
from tkinter import messagebox
def input_with_timeout(prompt, timeout):
    def timeout_handler():
        print("\nTimeout! Continuing to the next iteration...")
        raise TimeoutError

    # Start the timer
    timer = threading.Timer(timeout, timeout_handler)
    timer.start()
    
    try:
        # Try to get user input
        user_input = input(prompt)
        timer.cancel()  # Cancel the timer if input is received
        return user_input
    except TimeoutError:
        # Return None if timed out
        return None

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

    def to_json(self):
        return json.dumps(
            {
                "name": self.name,
                "buy": self.buy,
                "sell": self.sell,
                "time": self.time,
            }
        )


class Position:
    def __init__(self, buy_coord, sell_coord):
        self.buy_coord = buy_coord
        self.sell_coord = sell_coord

    def setItem(self, opp: fumble_opp):
        self.name = opp.name
        self.buy_price = opp.buy
        self.sell_price = opp.sell

    def to_dict(self):
        return {
            "buy_coord": self.buy_coord,
            "sell_coord": self.sell_coord,
        }



class TraderUI(tk.Toplevel):
    def __init__(self, app):
        tk.Toplevel.__init__(self,app) #master have to be Toplevel, Tk or subclass of Tk/Toplevel
        self.title("Fumbler UI")
        self.geometry("800x500")  # Set the window size

    def callback(self): pass


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
        app = tk.Tk()
        self.ui = TraderUI(app)
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
            print(f"Please move your mouse to the buy position for slot {i + 1}")
            self.get_sell_buy_positions()

        self.window.activate()
        return

    def position_to_click(self, position: Position):
        x = position.buy_coord[0]
        y = position.buy_coord[1]
        pyautogui.moveTo(
            random.randint(x - 10, x + 10),
            random.randint(y - 10, y + 10),
            random.uniform(0.1, 1),
            pyautogui.easeInOutSine,
        )
        pyautogui.click()
        pyautogui.typewrite(position.name)

    def build_trade_opps(self, savant_input):
        split_string = savant_input.split(":")
        split_string = [s.strip() for s in split_string]
        print(split_string)
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
        index = 1

        for opportunity in self.trade_opps:
            print(self.trade_opps)
            frame = tk.Frame(self.ui, padx=10, pady=5, relief="raised", borderwidth=2)
            frame.pack(fill='x', padx=5, pady=5)

            # Slot label with item information
            slot_label = tk.Label(
                frame,
                text=f"Slot {index}: {opportunity.name} - Buy: {opportunity.buy} / Sell: {opportunity.sell}",
                font=("Arial", 12),
            )
            slot_label.pack(side='left')

            # Buy button
            buy_button = tk.Button(frame, text="Buy", command=(lambda: self.function_buy(index - 1)))
            buy_button.pack(side='left', padx=5)

            # Sell button
            sell_button = tk.Button(frame, text="Sell", command=(lambda: self.function_sell(index - 1)))
            sell_button.pack(side='left', padx=5)

            # Collect button
            collect_button = tk.Button(frame, text="Collect", command=(lambda: self.function_collect(index - 1)))
            collect_button.pack(side='left', padx=5)

            # Exit button
            exit_button = tk.Button(frame, text="Exit", command=(lambda: self.function_exit(index - 1)))
            exit_button.pack(side='left', padx=5)

            print("Inv Slot: " + str(index))
            print("Name: " + opportunity.name)
            print("Buy: " + str(opportunity.buy))
            print("Sell: " + str(opportunity.sell))
            index += 1
        self.ui.update()


    def function_buy(self, number):
        opp: fumble_opp = self.trade_opps.pop(number)
        self.positions[number].setItem(opp)
        print("Buy: " + str(opp.buy))
        print("Sell: " + str(opp.sell))
        print("Name: " + opp.name)
        print(f"Buy on inv slot {number + 1}")
        self.position_to_click(self.positions[number])

    def function_sell(self, number):
        print(f"Sell on slot {number + 1}")
        self.position_to_click(number * 2 + 1)

    def function_collect(self, number):
        print(f"Collect on slot {number}")
        # random sell or buy
        # random click pos

    def function_exit(self, number):
        print(f"Exit on slot {number}")
        # random sell or buy
        # random click pos

    def exit_app(self):
        print("Exiting...")
        exit()

def start_server(trader: Trader, host="", port=12345):
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, )

    # Bind the socket to the address and port
    server_address = (host, port)
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(1)
    print(f"Starting server on {host}:{port}")
    try:
        while True:
            # Wait for a connection
            print("Waiting for a connection...")
            connection, client_address = server_socket.accept()
            try:
                print(f"Connection from {client_address}")

                # Receive the data in small chunks and print it
                while True:
                    now = time.time()
                    data = connection.recv(1024)
                    if data:
                        os.system("cls")
                        trader.build_trade_opps(f'{data.decode("utf-8")}')
                        time.sleep(1)
                    else:
                        print("No more data from", client_address)
                        break
            finally:
                # Clean up the connection
                connection.close()
    except KeyboardInterrupt:
        print("Closing server...")
        server_socket.close()


def main():
    args = parse_args()
    trader = Trader(username=args.username, slots=args.slots)
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
                print("Invalid number of positions in file, re-run with --clean")
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
