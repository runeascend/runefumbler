import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import json
 
class Position:
    def __init__(
        self,
        buy_coord,
        sell_coord,
        set_price_coord,
        set_quantity_coord,
        confirm_coord,
        inventory_coord,
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

with open("positions.json", "r") as f:
    json_positons = json.load(f)
    positions = [
        Position(
            buy_coord=position["buy_coord"],
            sell_coord=position["sell_coord"],
            set_price_coord=position["set_price_coord"],
            set_quantity_coord=position["set_quantity_coord"],
            confirm_coord=position["confirm_coord"],
            inventory_coord=position["inventory_coord"],
        )
        for position in json_positons
    ]

    main_positions = positions



def match_template(img_rgb, img_gray, template, color):
    w, h = template.shape[::-1]
    res = cv.matchTemplate(img_gray,template,cv.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = np.where( res >= threshold)
    for pt in zip(*loc[::-1]):
        cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), color, 2)

def match_template_update_all_confirm(img_rgb, img_gray, template, color):
    w, h = template.shape[::-1]
    res = cv.matchTemplate(img_gray,template,cv.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = np.where( res >= threshold)
    for pt in zip(*loc[::-1]):
        cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), color, 2)
        for i in range(0,8):
            main_positions[i].confirm_coord[0] = (int)(pt[0] + (w / 2))
            main_positions[i].confirm_coord[1] = (int)(pt[1] + (h / 2))

def match_template_update_all_set_price(img_rgb, img_gray, template, color):
    w, h = template.shape[::-1]
    res = cv.matchTemplate(img_gray,template,cv.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = np.where( res >= threshold)
    for pt in zip(*loc[::-1]):
        cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), color, 2)
        for i in range(0,8):
            main_positions[i].set_price_coord[0] = (int)(pt[0] + (w / 2))
            main_positions[i].set_price_coord[1] = (int)(pt[1] + (h / 2))

def match_template_update_all_quantity(img_rgb, img_gray, template, color):
    w, h = template.shape[::-1]
    res = cv.matchTemplate(img_gray,template,cv.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = np.where( res >= threshold)
    for pt in zip(*loc[::-1]):
        cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), color, 2)
        for i in range(0,8):
            main_positions[i].set_quantity_coord[0] = (int)(pt[0] + (w / 2))
            main_positions[i].set_quantity_coord[1] = (int)(pt[1] + (h / 2))

    
def match_buy_template(img_rgb, img_gray, template, color):
    w, h = template.shape[::-1]
    res = cv.matchTemplate(img_gray,template,cv.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = np.where( res >= threshold)
    index = 0
    for pt in zip(*loc[::-1]):
        cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), color, 2)
        main_positions[index].buy_coord[0] = (int)(pt[0] + (w / 2))
        main_positions[index].buy_coord[1] = (int)(pt[1] + (h / 2))
        index += 1
        
def match_sell_template(img_rgb, img_gray, template, color):
    w, h = template.shape[::-1]
    res = cv.matchTemplate(img_gray,template,cv.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = np.where( res >= threshold)
    index = 0
    for pt in zip(*loc[::-1]):
        cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), color, 2)
        main_positions[index].sell_coord[0] = (int)(pt[0] + (w / 2))
        main_positions[index].sell_coord[1] = (int)(pt[1] + (h / 2))
        index += 1

def build_main_window():
    img_rgb = cv.imread('photos/full_main_window.png')
    assert img_rgb is not None, "file could not be read, check with os.path.exists()"
    img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
    template_buy = cv.imread('photos/buy_slot.png', cv.IMREAD_GRAYSCALE)
    assert template_buy is not None, "file could not be read, check with os.path.exists()"

    template_sell = cv.imread('photos/sell_slot.png', cv.IMREAD_GRAYSCALE)
    assert template_sell is not None, "file could not be read, check with os.path.exists()"

    template_slot = cv.imread('photos/ge_slot.png', cv.IMREAD_GRAYSCALE)
    assert template_slot is not None, "file could not be read, check with os.path.exists()"

    match_buy_template(img_rgb, img_gray, template_buy, (0,0,255))
    match_sell_template(img_rgb, img_gray, template_sell, (0,255,0))
    match_template(img_rgb, img_gray, template_slot, (255,0,0))

    cv.imwrite('identify_main.png',img_rgb)

def build_ge_offer():
    img_rgb = cv.imread('photos/full_offer.png')
    assert img_rgb is not None, "file could not be read, check with os.path.exists()"
    img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
    template_set_price = cv.imread('photos/set_price.png', cv.IMREAD_GRAYSCALE)
    assert template_set_price is not None, "file could not be read, check with os.path.exists()"

    template_confirm = cv.imread('photos/confirm.png', cv.IMREAD_GRAYSCALE)
    assert template_confirm is not None, "file could not be read, check with os.path.exists()"

    template_quantity = cv.imread('photos/quantity.png', cv.IMREAD_GRAYSCALE)
    assert template_quantity is not None, "file could not be read, check with os.path.exists()"

    match_template_update_all_set_price(img_rgb, img_gray, template_set_price, (0,0,255))
    match_template_update_all_confirm(img_rgb, img_gray, template_confirm, (0,255,0))
    match_template_update_all_quantity(img_rgb, img_gray, template_quantity, (255,0,0))

    cv.imwrite('identify_offer.png',img_rgb)

build_main_window()
build_ge_offer()

with open("updated_positions.json", "w") as f:
    json_positions = [
        position.to_dict() for position in main_positions
    ]
    json.dump(json_positions, f)