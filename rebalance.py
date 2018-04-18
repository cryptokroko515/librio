from binance.client import Client
from binance.exceptions import BinanceAPIException
from decimal import Decimal

import config
# import json

client = Client(config.API_KEY, config.API_SECRET)
record = open("record.txt", "a")

exchange_info = client.get_exchange_info()["symbols"]


def rebalance(total_value, coins=None):
    plus = []
    minus = []
    eth_price = 0

    # coins = json.load(open('test.json'))['coins']

    for coin in coins:
        if coin["delta"] > 0:
            plus.append(coin)
        else:
            minus.append(coin)
        if coin["symbol"] == "ETH":
            eth_price = coin["ticker"]

    buy_coin = minus.pop()
    sell_coin = plus.pop()

    while True:

        sell_delta = abs(sell_coin["delta"])
        buy_delta = abs(buy_coin["delta"])

        while sell_delta != 0 and buy_delta != 0:

            market = sell_coin["symbol"] + '-' + buy_coin["symbol"]

            print("Sell delta: " + str(sell_delta) + " Buy delta: " + str(buy_delta) + "\n")
            record.write("Sell delta: " + str(sell_delta) + " Buy delta: " + str(buy_delta) + "\n\n")

            if sell_delta > buy_delta:
                # Sell as much as you can buy of the Buy coin
                value = buy_delta * total_value / 100.0
                sell_delta -= buy_delta
                print("Market: " + market)
                print("Sell delta: " + str(sell_delta) + "\n")

                record.write("Market: " + market + "\n")
                record.write("Sell delta: " + str(sell_delta) + "\n\n")

                # Sell time boyz
                sell_time_boyz(sell_coin, buy_coin, value, eth_price)

                if minus:
                    buy_coin = minus.pop()
                    buy_delta = abs(buy_coin["delta"])
                    print("Popped: " + buy_coin["symbol"] + "\n")
                    record.write("Popped: " + buy_coin["symbol"] + "\n\n")
            else:
                # Sell as much as you can sell of the Sell coin
                value = sell_delta * total_value / 100.0
                buy_delta -= sell_delta
                sell_delta = 0
                print("Market: " + market)
                print("Buy delta: " + str(buy_delta))

                # Sell time boyz
                sell_time_boyz(sell_coin, buy_coin, value, eth_price)

                if plus:
                    sell_coin = plus.pop()
                    sell_delta = abs(sell_coin["delta"])
                    print("Popped: " + sell_coin["symbol"] + "\n")
                    record.write("Popped: " + sell_coin["symbol"] + "\n\n")

        if not minus:
            break

    record.close()
    return


def sell_time_boyz(sell_coin, buy_coin, value, eth_price):
    print("Selling in progress...")

    quantity = value / sell_coin["ticker"]

    if sell_coin["symbol"] != "ETH" and buy_coin["symbol"] != "ETH":
        # Sell into ETH first then buy
        print("Sell " + str(quantity) + " " + sell_coin["symbol"] + " into ETH")
        record.write("Sell " + str(quantity) + " " + sell_coin["symbol"] + " into ETH" + "\n")

        exchange_type = sell_coin["symbol"] + "ETH"
        eth_exchange_type = buy_coin["symbol"] + "ETH"
        quantity = more_than_min_quantity(quantity, exchange_type, exchange_info)
        buy_quantity = more_than_min_quantity(value / buy_coin["ticker"], eth_exchange_type, exchange_info)

        if quantity != -1 and buy_quantity != -1:
            try:
                client.order_market_sell(symbol=exchange_type, quantity=quantity)
            except BinanceAPIException as e:
                print(e)
                raise
        else:
            print("***Could not sell, too small a quantity***")
            record.write("***Could not sell, too small a quantity***" + "\n")
            return

        print("Buy " + str(buy_quantity) + " " + buy_coin["symbol"] + " using ETH\n")
        record.write("Buy " + str(buy_quantity) + " " + buy_coin["symbol"] + " using ETH\n\n")

        try:
            client.order_market_buy(symbol=eth_exchange_type, quantity=buy_quantity)
        except BinanceAPIException as e:
            print(e)
            raise
    else:
        # Sell directly
        print("Sell " + str(quantity) + " " + sell_coin["symbol"] + " into " + buy_coin["symbol"] + "\n")
        record.write("Sell " + str(quantity) + " " + sell_coin["symbol"] + " into " + buy_coin["symbol"] + "\n\n")
        exchange_type = sell_coin["symbol"] + buy_coin["symbol"]
        quantity = more_than_min_quantity(quantity, exchange_type, exchange_info)

        if sell_coin["symbol"] == "ETH":
            exchange_type = buy_coin["symbol"] + sell_coin["symbol"]
            quantity = more_than_min_quantity(value / buy_coin["ticker"], exchange_type, exchange_info)
            try:
                client.order_market_buy(symbol=exchange_type, quantity=quantity)
            except BinanceAPIException as e:
                print(e)
                raise
            return

        if quantity != -1:
            try:
                client.order_market_sell(symbol=exchange_type, quantity=quantity)
            except BinanceAPIException as e:
                print(e)
                raise
        else:
            print("***Could not sell, too small a quantity***")
            record.write("***Could not sell, too small a quantity***" + "\n")


def more_than_min_quantity(quantity, exchange_type, info):
    for symbol in info:
        if symbol["symbol"] == exchange_type:
            for filter in symbol["filters"]:
                if filter["filterType"] == "LOT_SIZE":
                    if quantity >= float(filter["minQty"]):
                        return Decimal(quantity).quantize(Decimal(format_number(filter["stepSize"])))
                    else:
                        return -1
    return -1


def format_number(num):

    dec = Decimal(num)
    tup = dec.as_tuple()
    delta = len(tup.digits) + tup.exponent
    digits = ''.join(str(d) for d in tup.digits)
    if delta <= 0:
        zeros = abs(tup.exponent) - len(tup.digits)
        val = '0.' + ('0' * zeros) + digits
    else:
        val = digits[:delta] + ('0' * tup.exponent) + '.' + digits[delta:]
    val = val.rstrip('0')
    if val[-1] == '.':
        val = val[:-1]
    if tup.sign:
        return '-' + val
    return val
