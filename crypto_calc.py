from binance.client import Client

from config import *
from symbols import valuable_coins

from zigzag import zigzag
from calculate_long import calculateLong

binance_client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)


def calculations(message):
    asset = message.split(" ")[0].upper()
    div = int(message.split(" ")[2])

    if asset in valuable_coins:
        response = {"o": [], "h": [], "l": [], "c": []}
        try:
            klines = binance_client.get_historical_klines(asset, "1h", "8 day ago UTC")
        except Exception as ex:
            return -2

        for i in klines:
            response["o"].append(float(i[1]))
            response["h"].append(float(i[2]))
            response["l"].append(float(i[3]))
            response["c"].append(float(i[4]))

        get_zigzag = zigzag(response)

        try:
            balance = binance_client.get_asset_balance("USDT")
            deposit = float(balance["free"]) / div
        except Exception as ex:
            return -3

        if get_zigzag != -1:
            return calculateLong(get_zigzag[2], get_zigzag[3], deposit)
        else:
            return -4
    else:
        return -1
