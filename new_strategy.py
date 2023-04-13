import math

top = 61.0
low = 56.9
deposit = 1000 / 3
decimals = 1


def calculateLong():
    diff = top - low
    price_range = diff * 100 / low

    price_a = round(top - (diff * 50 / 100), decimals)
    price_b = round(top - (diff * 61.8 / 100), decimals)
    price_c = round(top - (diff * 78.6 / 100), decimals)
    price_d = round(top - (diff * 140 / 100), decimals)
    price_e = round(top - (diff * 161.8 / 100), decimals)

    qty1 = round((deposit * 45 / 100) / price_c, 2)
    qty2 = round((deposit * 30 / 100) / low, 2)
    qty3 = round((deposit * 25 / 100) / price_e, 2)
    qty = [qty1, qty2, qty3]

    tax = 0.00075

    fee1buy = (qty1 * price_c) * tax
    fee1sell = (qty1 * price_a) * tax

    fee2buy = (qty2 * low) * tax
    fee2sell = (sum(qty[:2]) * price_c) * tax

    fee3buy = (qty3 * price_e) * tax
    fee3sell = (sum(qty) * price_d) * tax

    feebuy = [fee1buy, fee2buy, fee3buy]

    profit1 = round((qty1 * price_a - qty1 * price_c) - (fee1buy + fee1sell), 2)
    profit2 = round(
        (sum(qty[:2]) * price_c - sum(qty[:2]) * low) - (sum(feebuy[:2]) + fee2sell), 2
    )
    profit3 = round(
        (sum(qty) * price_d - sum(qty) * price_e) - (sum(feebuy) + fee3sell), 2
    )

    print(f"Profit 1: {profit1}")
    print(f"Profit 2: {profit2}")
    print(f"Profit 3: {profit3}")


calculateLong()
