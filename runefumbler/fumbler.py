import os
import random
import socket
import time

import pyautogui as mouse
import win32gui

positions = []

test_string = "Swordfish : 178 : 183 : 100 : Gold amulet (u) : 122 : 137 : 100 : Swamp paste : 5 : 10 : 100 : Steam rune : 110 : 116 : 13 : Lava rune : 20 : 25 : 90 : Amethyst dart : 237 : 244 : 46 : Lantern lens : 13 : 18 : 125 : Dragon javelin : 883 : 907 : 117 :"


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


def build_trade_opps(savant_input):
    split_string = savant_input.split(":")
    split_string = [s.strip() for s in split_string]
    print(split_string)
    trade_opps = []
    for i in range(0, 32, 4):
        opp = fumble_opp(
            split_string[0 + i],
            split_string[1 + i],
            split_string[2 + i],
            split_string[3 + i],
        )
        trade_opps.append(opp)
    for opp in trade_opps:
        opp.show()


def start_server(host="192.168.1.70", port=12345):
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
                data = connection.recv(1024)
                if data:
                    os.system("cls")
                    build_trade_opps(f'{data.decode("utf-8")}')

                else:
                    print("No more data from", client_address)
                    break
        finally:
            # Clean up the connection
            connection.close()


def get_sell_buy_positions(positions):
    time.sleep(2)
    positions.append(mouse.position())
    print(mouse.position())
    time.sleep(2)
    positions.append(mouse.position())
    print(mouse.position())


# Don't move your window after setting the positions we aren't that advanced
def print_window(hwnd, wildcard):
    window_text = win32gui.GetWindowText(hwnd)
    if wildcard in window_text:
        print(window_text)
        rect = win32gui.GetWindowRect(hwnd)
        x = rect[0]
        y = rect[1]
        w = rect[2] - x
        h = rect[3] - y
        win32gui.SetForegroundWindow(hwnd)

        for i in range(0, 8):
            get_sell_buy_positions(positions)

        print(positions)

        return True


def analyze_window():
    # Since it puts your username there might as well search for it.
    win32gui.EnumWindows(print_window, "DavTF")
    return


def position_to_click(index):
    x = positions[index][0]
    y = positions[index][1]
    mouse.moveTo(
        random.randint(x - 10, x + 10),
        random.randint(y - 10, y + 10),
        random.uniform(0.1, 1),
        mouse.easeInOutSine,
    )
    mouse.click()


def function_buy(number):
    print(f"Buy on inv slot {number + 1}")
    position_to_click(number * 2)


def function_sell(number):
    print(f"Sell on slot {number + 1}")
    position_to_click(number * 2 + 1)


def function_collect(number):
    print(f"Collect on slot {number}")
    # random sell or buy
    # random click pos


def function_exit(number):
    print(f"Exit on slot {number}")
    # random sell or buy
    # random click pos


def process_input(user_input):
    number = int(user_input[0])
    char = user_input[1].lower()

    if char == "b":
        function_buy(number - 1)
    elif char == "s":
        function_sell(number - 1)
    elif char == "c":
        function_collect(number - 1)
    elif char == "e":
        function_exit(number - 1)
    else:
        print("Invalid character input. Please use 'b', 's', 'c', or 'e'.")


def execute_trades():
    while True:
        user_input = input("Action: ").strip()
        if (
            len(user_input) == 2
            and user_input[0].isdigit()
            and int(user_input[0]) in range(1, 9)
        ):
            process_input(user_input)
        else:
            print(
                "Invalid input format. Please enter a number (1-8) followed by a character (b, s, c, e)."
            )


def main():
    start_server()
    # analyze_window()
    # execute_trades()


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
