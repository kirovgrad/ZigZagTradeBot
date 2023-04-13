def float_to_str(f):
    import decimal

    ctx = decimal.Context()
    ctx.prec = 20
    d1 = ctx.create_decimal(repr(f))
    return format(d1, "f")

def get_TP_prices(top_price, low_price):

    decimals = max(
        len(float_to_str(top_price).split(".")[1]),
        len(float_to_str(low_price).split(".")[1]),
    )

    difference = top_price - low_price

    firstTP = round(top_price - (difference * 0.5), decimals)
    secondTP = round(top_price - (difference * 0.786), decimals)

    return [float_to_str(firstTP), float_to_str(secondTP)]

def parse_enter_prices(message):
    if "\n" in message:
        lines = message.split("\n")
    else:
        lines = [message]

    result = {}
    for line in lines:
        array = line.split(" ")
        prices = array[1].split("-")
        result[array[0].upper()] = [float(prices[0]), float(prices[1])]

    return result

