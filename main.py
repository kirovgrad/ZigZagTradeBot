import time
import threading
import json

import telebot
from telebot import types

from config import *
from symbols import *

from util import *
from binance_util_funcs import *

from create_order import main_create_limit_order
from crypto_parser import main_parser
from crypto_calc import calculations

bot = telebot.TeleBot(TG_TOKEN)

global scan_status
global night_mode

scan_status = False
night_mode = False


def start_scan():
    bot.send_message(CHAT_ID, "Starting scan...")

    potential_entries = []
    potential_entries.extend(main_parser("Crypto 1h", valuable_coins, "parse"))
    noticed = []

    if len(potential_entries) == 0:
        bot.send_message(CHAT_ID, "There is no entries to strategy. Try later.")
        return
    else:
        bot.send_message(
            CHAT_ID,
            f"There is {len(potential_entries)} potential entries to strategy.",
        )

    while True:

        if scan_status == False:
            bot.send_message(CHAT_ID, "Scanning was stopped.")
            break

        scanning_result = []
        scanning_result.extend(
            main_parser("Crypto 1h", [i[0] for i in potential_entries], "scan")
        )

        if len(scanning_result) != 0:
            scanning_result.sort(key=lambda a: float(a[2][:-1]))
            for i in scanning_result[::-1]:
                if i[0] in noticed:
                    continue
                noticed.append(i[0])
                bot.send_message(CHAT_ID, f"{i[0]} {i[1]} {i[2]}")

        time.sleep(15)


def start_parse(message):
    bot.send_message(CHAT_ID, "Please wait...")

    parsing_result = []
    parsing_result.extend(main_parser(message, valuable_coins, "parse"))

    if len(parsing_result) != 0:
        parsing_result.sort(key=lambda a: float(a[2][:-1]))
        for i in parsing_result[::-1]:
            bot.send_message(
                CHAT_ID,
                f"{i[0]} {i[1]} {i[2]}",
            )
    else:
        bot.send_message(
            message.chat.id,
            "There is no strategy entries. Try another timeframe.",
        )


def scan_orders(parsed_prices):
    orders = {}

    for i in parsed_prices:
        tp_prices = get_TP_prices(parsed_prices[i][0], parsed_prices[i][1])
        orders[i] = {"firstTP": tp_prices[0], "secondTP": tp_prices[1]}

    while True:
        global night_mode
        if night_mode == False:
            bot.send_message(CHAT_ID, "Stop multiposition.")
            break

        if len(orders) == 0:
            bot.send_message(CHAT_ID, "All orders were managed. Stop multiposition.")
            break

        for i in orders:
            all_orders = get_open_orders(i)
            balance = get_asset_balance(i[:-4])

            if all_orders == -1 or balance == -1:
                continue

            if len(all_orders) == 0:
                orders.pop(i, None)
                time.sleep(2)
                break

            elif (
                len(all_orders) == 2
                and all_orders[0]["side"] == "BUY"
                and all_orders[1]["side"] == "BUY"
            ):
                time.sleep(2)
                continue

            elif (
                len(all_orders) == 1
                and all_orders[0]["side"] == "BUY"
                and float(balance["free"]) > 0
            ):
                sell_order(i, balance["free"], orders[i]["firstTP"])
                time.sleep(2)
                continue

            elif (
                len(all_orders) == 2
                and all_orders[0]["side"] == "BUY"
                and all_orders[1]["side"] == "SELL"
            ):
                time.sleep(2)
                continue

            elif (
                len(all_orders) == 1
                and all_orders[0]["side"] == "SELL"
                and float(balance["free"]) > 0
                and float(balance["locked"]) > 0
            ):
                cancel_order(i, all_orders[0]["orderId"])
                time.sleep(1)
                current_balance = get_asset_balance(i[:-4])
                time.sleep(1)
                sell_order(
                    i,
                    str(float(current_balance["free"])),
                    orders[i]["secondTP"],
                )
                orders.pop(i, None)
                break

        time.sleep(10)


######################################################################


def main_bot():
    @bot.message_handler(commands="start")
    def start(message):
        if message.chat.id != int(CHAT_ID):
            return

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [
            "Crypto 15m",
            "Crypto 1h",
            "Crypto 4h",
        ]
        keyboard.add(*buttons)
        bot.send_message(CHAT_ID, "Choose option", reply_markup=keyboard)

    @bot.message_handler(commands="balance")
    def balance(message):
        if message.chat.id != int(CHAT_ID):
            return

        my_balance = get_balances()
        for i in my_balance:
            bot.send_message(
                CHAT_ID,
                f"Asset: {i['asset']}\nFree: {i['free']}\nLocked: {i['locked']}",
            )

    @bot.message_handler(commands="scan")
    def scanning(message):
        if message.chat.id != int(CHAT_ID):
            return

        global scan_status

        if scan_status == True:
            bot.send_message(CHAT_ID, "Already scanning. Turn it off first.")
            return

        scan_status = True
        thread1 = threading.Thread(target=start_scan)
        thread1.start()

    @bot.message_handler(commands="stop_scan")
    def stop_scan(message):
        global scan_status
        scan_status = False

    @bot.message_handler(commands="multiposition")
    def multiposition(message):
        if message.chat.id != int(CHAT_ID):
            return

        msg = bot.send_message(
            CHAT_ID, "Enter current active symbols and high/low prices."
        )
        bot.register_next_step_handler(msg, night_mode)

    def night_mode(message):
        global night_mode
        night_mode = True

        bot.send_message(CHAT_ID, "Night mode activated. Good night.")

        parsed_prices = parse_enter_prices(message.text)

        thread2 = threading.Thread(target=scan_orders, args=(parsed_prices,))
        thread2.start()

    @bot.message_handler(commands="stop_multiposition")
    def stop_multiposition(message):
        global night_mode
        night_mode = False

    @bot.message_handler(commands="parse")
    def parse(message):
        start_parse("Crypto 1h")

    @bot.message_handler(content_types=["text"])
    def main_functions(message):
        if message.chat.id != int(CHAT_ID):
            return

        elif "open" in message.text:  # Create Limit order for Symbol

            if len(message.text.split()) != 3:
                bot.send_message(CHAT_ID, "🟥 Incorrect command. ~symbol open division~")
                return

            limit_order = main_create_limit_order(message.text)

            if limit_order == -1:
                bot.send_message(CHAT_ID, "🟥 Failed to download candles.")
            elif limit_order == -2:
                bot.send_message(CHAT_ID, "🟥 There is no strategy enter.")
            elif limit_order == -3:
                bot.send_message(CHAT_ID, "🟥 Failed to get USDT balance.")
            elif limit_order == -4:
                bot.send_message(CHAT_ID, "🟥 Failed to get symbol info.")
            elif limit_order == -5:
                bot.send_message(CHAT_ID, "🟥 You don't have enough money for order.")
            elif limit_order == -6:
                bot.send_message(
                    CHAT_ID, "🟥 Only one order was created, so it was cancelled!"
                )
            elif limit_order == -7:
                bot.send_message(CHAT_ID, "🟥 Orders wasn't created!")
            elif limit_order == -8:
                bot.send_message(CHAT_ID, "🟥 Symbol is not for SPOT trading!")
            elif limit_order == -9:
                bot.send_message(CHAT_ID, "🟥 There is no such Symbol.")
            elif limit_order == -10:
                bot.send_message(CHAT_ID, "🟥 Incorrect division. Must be 1, 2, 3 or 4.")
            else:
                bot.send_message(
                    CHAT_ID,
                    "🟩 Limit orders are set!\n"
                    + "Potential profit: "
                    + f"{limit_order['order_info']['firstProfit']} USDT, "
                    + f"{limit_order['order_info']['secondProfit']} USDT",
                )

        elif "profit" in message.text:
            calc = calculations(message.text)

            if calc == -1:
                bot.send_message(CHAT_ID, "🟥 There is no such Symbol.")
            elif calc == -2:
                bot.send_message(CHAT_ID, "🟥 Failed to download candles.")
            elif calc == -3:
                bot.send_message(CHAT_ID, "🟥 Failed to get USDT balance.")
            elif calc == -4:
                bot.send_message(CHAT_ID, "🟥 There is no strategy enter.")

            else:
                symbol = message.text.split(" ")[0].upper()
                all_orders = get_open_orders(symbol)
                balance = get_asset_balance(symbol[:-4])

                if (
                    len(all_orders) == 1
                    and all_orders[0]["side"] == "BUY"
                    and float(balance["free"]) > 0
                ):
                    sell_order(symbol, balance["free"], calc["firstTakeProfit"])
                    bot.send_message(CHAT_ID, "🟩 First Take Profit Limit set.")
                    return

                elif (
                    len(all_orders) == 1
                    and all_orders[0]["side"] == "SELL"
                    and float(balance["free"]) > 0
                    and float(balance["locked"]) > 0
                ):
                    cancel_order(symbol, all_orders[0]["orderId"])
                    time.sleep(1)
                    current_balance = get_asset_balance(symbol[:-4])
                    time.sleep(1)
                    sell_order(
                        symbol,
                        str(float(current_balance["free"])),
                        calc["secondTakeProfit"],
                    )
                    bot.send_message(CHAT_ID, "🟩 Second Take Profit Limit set.")
                    return

                elif (
                    len(all_orders) == 0
                    and float(balance["free"]) > 0
                    and float(balance["locked"]) == 0
                ):
                    sell_order(
                        symbol, str(float(balance["free"])), calc["secondTakeProfit"]
                    )
                    return

                else:
                    bot.send_message(CHAT_ID, "🟥 No time for Take Profit.")
                    return

        elif "calc" in message.text:

            if len(message.text.split()) != 3:
                bot.send_message(CHAT_ID, "🟥 Incorrect command. ~symbol calc division~")
                return

            calc = calculations(message.text)

            if calc == -1:
                bot.send_message(CHAT_ID, "🟥 There is no such Symbol.")
            elif calc == -2:
                bot.send_message(CHAT_ID, "🟥 Failed to download candles.")
            elif calc == -3:
                bot.send_message(CHAT_ID, "🟥 Failed to get USDT balance.")
            elif calc == -4:
                bot.send_message(CHAT_ID, "🟥 There is no strategy enter.")
            else:
                bot.send_message(
                    CHAT_ID,
                    f"🟩 First buy at: {calc['firstBuyPrice']}"
                    + f"\nTake Profit at: {calc['firstTakeProfit']}"
                    + f"\nQuantity: {calc['firstQty']}"
                    + f"\nProfit will be: {calc['firstProfit']} USDT\n"
                    + f"\n🟩 Second buy at: {calc['secondBuyPrice']}"
                    + f"\nTake Profit at: {calc['secondTakeProfit']}"
                    + f"\nQuantity: {calc['secondQty']}"
                    + f"\nProfit will be: {calc['secondProfit']} USDT",
                )


######################################################################

if __name__ == "__main__":
    main_bot()
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as ex:
            print(ex)
