import argparse
import json
import os
import random
import signal
import socket
import time

import pyautogui
import pygetwindow


def alarm_handler(signum, frame):
    raise TimeoutError


def input_with_timeout(prompt, timeout):
    # set signal handler
    signal.signal(signal.SIG_DFL, alarm_handler)
    signal.alarm(timeout)  # produce SIGALRM in `timeout` seconds

    try:
        return input(prompt)
    except TimeoutError:
        print("Continuing, no user input")
        return ""
    finally:
        signal.alarm(0)  # cance


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
    return parser.parse_args()


class fumble_opp:
    def __init__(self, name, buy, sell, time):
        self.name = name
        self.buy = buy
        self.sell = sell
        self.time = time

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


class Trader:

    def __init__(self, username):
        self.positions: list[Position] = []
        self.trade_opps = []
        self.x = -1
        self.y = -1
        self.w = -1
        self.h = -1
        self.username = username

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

        for i in range(0, 8):
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
        if len(self.trade_opps) > 8:
            self.trade_opps.pop(0)

        self.trade_opps.append(opp)
        index = 1
        for opportunity in self.trade_opps:
            print("Inv Slot: " + str(index))
            print("Name: " + opportunity.name)
            print("Buy: " + str(opportunity.buy))
            print("Sell: " + str(opportunity.sell))
            index += 1

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

    def process_input(self, user_input):
        number = int(user_input[0])
        char = user_input[1].lower()

        if char == "b":
            self.function_buy(number - 1)
        elif char == "s":
            self.function_sell(number - 1)
        elif char == "c":
            self.function_collect(number - 1)
        elif char == "e":
            self.function_exit(number - 1)
        else:
            print("Invalid character input. Please use 'b', 's', 'c', or 'e'.")

    def execute_trades(self):
        user_input = input_with_timeout("Action: ", 3).strip()
        if (
            len(user_input) == 2
            and user_input[0].isdigit()
            and int(user_input[0]) in range(1, 9)
        ):
            self.process_input(user_input)
        else:
            print(
                "Invalid input format. Please enter a number (1-8) followed by a character (b, s, c, e)."
            )
        time.sleep(0.001)


def start_server(trader: Trader, host="192.168.1.70", port=12345):
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the address and port
    server_address = (host, port)
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(1)
    print(f"Starting server on {host}:{port}")

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
                    trader.execute_trades()

                else:
                    print("No more data from", client_address)
                    break
        finally:
            # Clean up the connection
            connection.close()


def main():
    args = parse_args()
    trader = Trader(username=args.username)
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
            trader.positions = [
                Position(
                    buy_coord=position["buy_coord"],
                    sell_coord=position["sell_coord"],
                )
                for position in json_positons
            ]

    start_server(trader)


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
