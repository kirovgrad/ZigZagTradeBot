import math, sys

from util import float_to_str
from config import trend


def calculateLong(TOP_PRICE, LOW_PRICE, DEPOSIT):
    DECIMALS = max(
        len(float_to_str(TOP_PRICE).split(".")[1]),
        len(float_to_str(LOW_PRICE).split(".")[1]),
    )

    difference = TOP_PRICE - LOW_PRICE

    if trend == "consalidation":
        price_a = round(TOP_PRICE - (difference * 0.50), DECIMALS)
        price_c = round(TOP_PRICE - (difference * 0.786), DECIMALS)
        price_d = LOW_PRICE
    elif trend == "bull":
        price_a = round(TOP_PRICE - (difference * 0.382), DECIMALS)
        price_c = round(TOP_PRICE - (difference * 0.618), DECIMALS)
        price_d = round(TOP_PRICE - (difference * 0.786), DECIMALS)
    # elif trend == "bear":
    #     price_a = round(TOP_PRICE - (difference * 0.382), DECIMALS)
    #     price_c = round(TOP_PRICE - (difference * 0.618), DECIMALS)
    #     price_d = round(TOP_PRICE - (difference * 0.786), DECIMALS)

    firstQty = round((DEPOSIT * 39 / 100) / price_c, 8)
    secondQty = round((DEPOSIT * 61 / 100) / price_d, 8)
    totalQty = firstQty + secondQty

    fee_first_buy = (firstQty * price_c) * 0.00075
    fee_second_buy = (secondQty * price_d) * 0.00075
    fee_first_sell = (firstQty * price_a) * 0.00075
    fee_second_sell = (totalQty * price_c) * 0.00075

    firstProfit = round(
        (firstQty * price_a - firstQty * price_c) - (fee_first_buy + fee_first_sell), 2
    )
    secondProfit = round(
        (totalQty * price_c - (firstQty * price_c + secondQty * price_d))
        - (fee_first_buy + fee_second_buy + fee_second_sell),
        2,
    )

    return {
        "firstBuyPrice": price_c,
        "firstTakeProfit": price_a,
        "firstQty": firstQty,
        "firstProfit": firstProfit,
        "secondBuyPrice": price_d,
        "secondTakeProfit": price_c,
        "secondQty": secondQty,
        "secondProfit": secondProfit,
    }
