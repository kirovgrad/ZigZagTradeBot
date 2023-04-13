import datetime
import threading
import time

from binance.client import Client

from config import *
from symbols import *
from zigzag import zigzag

binance_client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)


def async_binance_downloader(symbol, result, timeframe, time_from):
    response = {"o": [], "h": [], "l": [], "c": []}
    try:
        klines = binance_client.get_historical_klines(
            symbol, timeframe, f"{time_from} day ago UTC"
        )
    except Exception as ex:
        print(ex)
        time.sleep(3)
        return

    for i in klines:
        response["o"].append(float(i[1]))
        response["h"].append(float(i[2]))
        response["l"].append(float(i[3]))
        response["c"].append(float(i[4]))

    result[symbol] = response


def binance_downloader(symbols, timeframe):
    threads_list = []
    result = {}
    time_from = "2" if timeframe == "15m" else "8" if timeframe == "1h" else "32"

    for symbol in symbols:
        get_candle = threading.Thread(
            target=async_binance_downloader, args=(symbol, result, timeframe, time_from)
        )
        get_candle.start()
        threads_list.append(get_candle)

    for t in threads_list:
        t.join()

    return result


def async_zigzag(candle_data, strategy_entries, symbol, mode):
    result = zigzag(candle_data, mode)
    if result != -1:
        strategy_entries.append([symbol] + result)


def start_zigzag(candles, mode):
    threads_list = []
    strategy_entries = []

    for symbol in candles:
        get_hhll = threading.Thread(
            target=async_zigzag, args=(candles[symbol], strategy_entries, symbol, mode)
        )
        get_hhll.start()
        threads_list.append(get_hhll)

    for t in threads_list:
        t.join()

    return strategy_entries


def main_parser(message, coins, zigzag_mode):
    timeframe = message.split(" ")[1]

    parsed_candles = binance_downloader(coins, timeframe)

    strategy_entries = start_zigzag(parsed_candles, zigzag_mode)

    return strategy_entries
