import math, sys

TOP_PRICE = 0.17350
LOW_PRICE = 0.15369
DEPOSIT = 10087
DECIMALS = 5
IS_SPLITABLE = 1

difference = TOP_PRICE - LOW_PRICE


def calculateLong():
    price_range = difference * 100 / LOW_PRICE

    price_a = round(TOP_PRICE - (difference * 50.0 / 100), DECIMALS)
    price_b = round(TOP_PRICE - (difference * 61.8 / 100), DECIMALS)
    price_c = round(TOP_PRICE - (difference * 78.6 / 100), DECIMALS)
    price_d = LOW_PRICE
    stopLoss = round(TOP_PRICE - (difference * 161.8 / 100), DECIMALS)

    firstQty = None
    secondQty = None

    if IS_SPLITABLE:
        firstQty = round((DEPOSIT * 25 / 100) / price_c, 4)
        secondQty = round((DEPOSIT * 75 / 100) / price_d, 4)
    else:
        firstQty = math.floor((DEPOSIT * 25 / 100) / price_c)
        secondQty = math.floor((DEPOSIT * 75 / 100) / price_d)

    totalQty = firstQty + secondQty

    if not IS_SPLITABLE:
        if firstQty == 0 or secondQty == 0:
            sys.exit("There is not enough money for make orders. Cancel.")

    firstProfit = round(
        ((firstQty * 0.25) * price_b + (firstQty * 0.75) * price_a)
        - (firstQty * price_c),
        DECIMALS,
    )
    secondProfit = round(
        ((totalQty * 0.25) * price_c + (totalQty * 0.75) * price_b)
        - (firstQty * price_c + secondQty * LOW_PRICE),
        DECIMALS,
    )

    stopLossLose = round(DEPOSIT - totalQty * stopLoss, DECIMALS)

    separateProfit = round(firstProfit + secondProfit, DECIMALS)

    print(f"Growth percent: {str(round(price_range, 2))}%")

    print(
        f"\nFirst buy:"
        + f"\nBy price: {price_c}"
        + f"\nQuantity: {firstQty}"
        + f"\nTake profit at: {price_b}"
        + f"\nStop loss at: {stopLoss}"
        + f"\nProfit at that level will be: {firstProfit} = +{round(firstProfit * 100 / DEPOSIT, 2)}%"
    )

    print(
        f"\nSecond buy:"
        + f"\nBy price: {price_d}"
        + f"\nQuantity: {secondQty}"
        + f"\nTake profit at: {price_c}"
        + f"\nStop loss at: {stopLoss}"
        + f"\nProfit at that level will be: {secondProfit} = +{round(secondProfit * 100 / DEPOSIT, 2)}%"
    )

    print(
        f"\nIf stop-loss, you lose: {stopLossLose} = -{round(stopLossLose * 100 / DEPOSIT, 2)}%"
    )

    print(
        f"\nThe separate profit will be: {separateProfit} = +{round(separateProfit * 100 / DEPOSIT, 2)}%"
    )


calculateLong()
