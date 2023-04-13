import datetime
import time
import math

from binance.helpers import round_step_size

from binance_util_funcs import *
from symbols import valuable_coins
from calculate_long import calculateLong
from zigzag import zigzag


def main_create_limit_order(message):
    message_list = message.split(" ")
    symbol = message_list[0].upper()
    asset = "USDT" if symbol.endswith("USDT") else "BUSD"
    divide = int(message_list[2])

    if symbol not in valuable_coins:
        return -9

    if 1 < divide > 4:
        return -10

    symbol_candles = get_symbol_candles(symbol)
    if symbol_candles == -1:
        return -1

    get_zigzag = zigzag(symbol_candles)
    if get_zigzag == -1:
        return -2

    deposit = get_deposit(asset)
    if deposit == -1:
        return -3

    order_info = calculateLong(
        get_zigzag[2], get_zigzag[3], math.floor(deposit / divide)
    )

    symbol_info = get_symbol_info(symbol)
    if symbol_info == -1:
        return -4

    if "SPOT" not in symbol_info["permissions"]:
        return -8

    minNotional = float(symbol_info["filters"][3]["minNotional"])
    stepSize = float(symbol_info["filters"][2]["stepSize"])

    if order_info["firstBuyPrice"] * order_info["firstQty"] < minNotional:
        return -5

    order_info["firstQty"] = round_step_size(order_info["firstQty"], stepSize)
    order_info["secondQty"] = round_step_size(order_info["secondQty"], stepSize)

    first_order = buy_order(symbol, order_info["firstQty"], order_info["firstBuyPrice"])
    second_order = buy_order(
        symbol, order_info["secondQty"], order_info["secondBuyPrice"]
    )

    orders_filled = 0

    if first_order != -1:
        orders_filled += 1
    if second_order != -1:
        orders_filled += 1

    if orders_filled == 0:
        return -7
    elif orders_filled == 1:
        if first_order == -1:
            cancel_order(second_order["symbol"], second_order["orderId"])
            return -6
        elif second_order == -1:
            cancel_order(first_order["symbol"], first_order["orderId"])
            return -6
    else:
        return {
            "first_order": first_order,
            "second_order": second_order,
            "order_info": order_info,
        }
