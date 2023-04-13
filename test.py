import finnhub
from config import *

finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

coins = finnhub_client.crypto_symbols("BINANCE")
bnbpairs = []
btcpairs = []
busdpairs = []
ethpairs = []

for i in coins:
    if i["symbol"].endswith("BNB"):
        bnbpairs.append(i["symbol"])
    elif i["symbol"].endswith("BTC"):
        btcpairs.append(i["symbol"])
    elif i["symbol"].endswith("BUSD"):
        busdpairs.append(i["symbol"])
    elif i["symbol"].endswith("ETH"):
        ethpairs.append(i["symbol"])

with open("bnbpairs.txt", "w") as file:
    file.write("\n".join(bnbpairs))
with open("btcpairs.txt", "w") as file:
    file.write("\n".join(btcpairs))
with open("busdpairs.txt", "w") as file:
    file.write("\n".join(busdpairs))
with open("ethpairs.txt", "w") as file:
    file.write("\n".join(ethpairs))
