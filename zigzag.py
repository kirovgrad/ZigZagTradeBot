prd = 7
low_range = 4
high_range = 10
terminator = 0.618  # [0.5, 0.618, 0.786]


def highestbars(high, prd, current_index, bars_high):
    list_slice = bars_high[current_index - prd : current_index + 1]
    max_high = max(list_slice)
    max_high_index = bars_high.index(max_high, current_index - prd, current_index + 1)
    return current_index - max_high_index


def lowestbars(low, prd, current_index, bars_low):
    list_slice = bars_low[current_index - prd : current_index + 1]
    min_low = min(list_slice)
    min_low_index = bars_low.index(min_low, current_index - prd, current_index + 1)
    return current_index - min_low_index


def add_to_zigzag(pointer, value, bIndex):
    pointer.insert(0, value)
    pointer.insert(1, bIndex)
    if len(pointer) > 12:
        pointer[:-2]


def update_zigzag(pointer, value, bIndex, direction):
    if len(pointer) == 0:
        add_to_zigzag(pointer, value, bIndex)
    else:
        if (direction == 1 and value > pointer[0]) or (
            direction == -1 and value < pointer[0]
        ):
            pointer[0], pointer[1] = value, bIndex


def zigzag(response, mode="parse"):
    bars_high = response["h"]
    bars_low = response["l"]
    candles_length = len(response["h"])

    oldDirection = 0
    zigzag = []

    for i in range(prd, candles_length):
        pHigh = (
            response["h"][i]
            if highestbars(response["h"][i], prd, i, bars_high) == 0
            else None
        )
        pLow = (
            response["l"][i]
            if lowestbars(response["l"][i], prd, i, bars_low) == 0
            else None
        )

        direction = (
            1 if pHigh and not pLow else -1 if pLow and not pHigh else oldDirection
        )
        oldZigzag = zigzag.copy()
        dirChanged = direction != oldDirection

        if pHigh or pLow:
            if dirChanged:
                add_to_zigzag(zigzag, pHigh if direction == 1 else pLow, i)
            else:
                update_zigzag(zigzag, pHigh if direction == 1 else pLow, i, direction)

        oldDirection = direction

    if len(zigzag) < 12:
        return -1

    long_entry_normal = (
        zigzag[0] > zigzag[2]
        and zigzag[0] > zigzag[4]
        and zigzag[4] > zigzag[8]
        and zigzag[2] > zigzag[6]
    )

    long_entry_extra = (
        zigzag[2] > zigzag[4]
        and zigzag[2] > zigzag[6]
        and zigzag[6] > zigzag[10]
        and zigzag[4] > zigzag[8]
    )

    if long_entry_normal:
        highest_bar_price = max(response["o"][zigzag[1]], response["c"][zigzag[1]])
        lowest_bar_price = min(response["o"][zigzag[3]], response["c"][zigzag[3]])

        price_range = round(
            (highest_bar_price - lowest_bar_price) * 100 / highest_bar_price, 2
        )
        price_range_condition = low_range <= price_range <= high_range

        if price_range_condition:
            price_diff = zigzag[0] - zigzag[2]

            max_allowed_price = zigzag[0] - (price_diff * terminator)
            min_allowed_price = zigzag[0] - (price_diff * 1.618)

            if mode == "parse":
                return ["🟩Long", f"{price_range}%", zigzag[0], zigzag[2]]

            elif mode == "scan":
                if zigzag[1] < len(response["l"]) - 1:
                    last_min_price = response["l"][-1]
                    if min_allowed_price < last_min_price < max_allowed_price:
                        return [
                            "🟩Long",
                            f"{price_range}%",
                            zigzag[0],
                            zigzag[2],
                        ]

    elif long_entry_extra:
        highest_bar_price = max(response["o"][zigzag[3]], response["c"][zigzag[3]])
        lowest_bar_price = min(response["o"][zigzag[5]], response["c"][zigzag[5]])

        price_range = round(
            (highest_bar_price - lowest_bar_price) * 100 / highest_bar_price, 2
        )
        price_range_condition = low_range <= price_range <= high_range

        if price_range_condition:
            price_diff = zigzag[2] - zigzag[4]

            max_allowed_price = zigzag[2] - (price_diff * 0.786)

            if zigzag[0] < max_allowed_price:
                return ["🟩Long", f"{price_range}%", zigzag[2], zigzag[4]]

    return -1
