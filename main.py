# Binance Exchange
# Account rebalancer
import json
import config
import time

from rebalance import rebalance
from binance.client import Client
from binance.exceptions import BinanceAPIException

client = Client(config.API_KEY, config.API_SECRET)
record = open("record.txt", "a")
money = open("money.txt", "a")

VALUE = "value"
BALANCE = "balance"
SYMB = "symbol"
TICKER = "ticker"
PER = "percentage"


def is_exceed_margin(coins=None, margin=0, portfolio_value=0):
    if portfolio_value > 0:
        max_per = 0
        min_per = 10000000000

        for coin in coins:
            if coin[PER] > max_per:
                max_per = coin[PER]
            if coin[PER] < min_per:
                min_per = coin[PER]
        return (max_per - min_per) >= margin
    else:
        return False


# Get coins from percentage.json
coins = json.load(open('data.json'))["coins"]
margin = json.load(open('data.json'))["margin"]

portfolio_value = 0
bitcoin_price = 0
print("Margin: " + str(margin))
record.write("Today is: " + time.strftime("%Y-%m-%d %H:%M") + "\n")
record.write("Margin: " + str(margin) + "\n")

try:
    bitcoin_price = float(client.get_symbol_ticker(symbol="BTCUSDT")["price"])
except BinanceAPIException as e:
        print(e)
        raise

# Get percentage of currencies of the portfolio
for coin in coins:
    print("Target: " + coin[SYMB] + " " + str(coin["target"]) + "%")
    record.write("Target: " + coin[SYMB] + " " + str(coin["target"]) + "%" + "\n\n")

    if not config.OFFLINE:
        try:
            coin[BALANCE] = float(client.get_asset_balance(asset=coin[SYMB])["free"])
            print("Balance is: " + str(coin[BALANCE]) + " " + coin[SYMB])
            record.write("Balance is: " + str(coin[BALANCE]) + " " + coin[SYMB] + "\n")
        except BinanceAPIException as e:
            print(e)
            raise

        try:
            coin[TICKER] = float(client.get_symbol_ticker(symbol=coin[SYMB] + "BTC")["price"]) * bitcoin_price
            print("Price is: $" + str(coin[TICKER]) + "\n")
            record.write("Price is: $" + str(coin[TICKER]) + "\n\n")
        except BinanceAPIException as e:
            print(e)
            raise

        coin[VALUE] = coin[BALANCE] * coin[TICKER]
        portfolio_value += coin[VALUE]

# Calculate percentages of portfolio
if portfolio_value > 0:
    for coin in coins:
        coin[PER] = coin[VALUE] * 100 / portfolio_value
        coin["delta"] = coin[PER] - coin["target"]

# If the difference between any two currencies is >= 10% rebalance
print("Portfolio value: " + str(portfolio_value))
print("**************** Begin Selling ****************")
record.write("Portfolio value: " + str(portfolio_value) + "\n")
record.write("**************** Begin Selling ****************" + "\n")
money.write(str(portfolio_value) + "\n")
money.close()

if is_exceed_margin(coins=coins, margin=margin, portfolio_value=portfolio_value):
    rebalance(portfolio_value, coins)
    print("You have rebalanced your portfolio! Congratulations, go celebrate with a drink and a movie!")
    record.write("You have rebalanced your portfolio! Congratulations, go celebrate with a drink and a movie!" + "\n")
else:
    print("You do not need to rebalance your portfolio! Go read a book or something in the meantime!")
    record.write("You do not need to rebalance your portfolio! Go read a book or something in the meantime!" + "\n")
record.close()
