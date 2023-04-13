from config import *

from binance.client import Client

binance_client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)


def get_balances():
    try:
        my_balance = binance_client.get_account()
    except Exception as ex:
        print(ex)
        return -1
    balance = []
    for i in my_balance["balances"]:
        if float(i["free"]) != 0 or float(i["locked"]) != 0:
            balance.append(i)
    return balance


def get_order_status(symbol, orderId):
    try:
        order_status = binance_client.get_order(symbol=symbol, orderId=str(orderId))
        return order_status
    except Exception as ex:
        print(ex)
        return -1


def get_open_orders(symbol):
    try:
        open_orders = binance_client.get_open_orders(symbol=symbol)
        return open_orders
    except Exception as ex:
        print(ex)
        return -1


def sell_order(symbol, quantity, price):
    try:
        sell_order = binance_client.order_limit_sell(
            symbol=symbol, quantity=float(quantity), price=str(price)
        )
        return sell_order
    except Exception as ex:
        print(ex)
        return -1


def get_asset_balance(asset):
    try:
        asset_balance = binance_client.get_asset_balance(asset=asset)
        return asset_balance
    except Exception as ex:
        print(ex)
        return -1


def cancel_order(symbol, orderId):
    try:
        cancel_order = binance_client.cancel_order(symbol=symbol, orderId=str(orderId))
        return cancel_order
    except Exception as ex:
        print(ex)
        return -1


def get_symbol_candles(symbol):
    response = {"o": [], "h": [], "l": [], "c": []}
    try:
        symbol_candles = binance_client.get_historical_klines(
            symbol, "1h", "8 days ago UTC"
        )
    except Exception as ex:
        return -1

    for i in symbol_candles:
        response["o"].append(float(i[1]))
        response["h"].append(float(i[2]))
        response["l"].append(float(i[3]))
        response["c"].append(float(i[4]))

    return response


def get_deposit(asset):
    try:
        balance = binance_client.get_asset_balance(asset=asset)
        return float(balance["free"])
    except Exception as ex:
        return -1


def buy_order(symbol, quantity, price):
    try:
        order = binance_client.order_limit_buy(
            symbol=symbol, quantity=quantity, price=str(price)
        )
        return order
    except Exception as ex:
        print(ex)
        return -1


def get_symbol_info(symbol):
    try:
        symbol_info = binance_client.get_symbol_info(symbol)
        return symbol_info
    except Exception:
        return -1
