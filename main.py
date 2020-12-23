import pandas as pd
import requests
import math
from time import sleep
from datetime import date, datetime
from os import system
import calendar
from secrets import api_token, stocks_dictionary


def bash_command(user_in):
    _ = system(user_in)


def clear_screen():
    _ = system('clear')


def check_prices(stock_or_all, price_or_shares2buy):
    if price_or_shares2buy.lower() == 'price':
        price_or_shares2buy = 'Stock Price'
    elif price_or_shares2buy.lower() == 'shares2buy':
        price_or_shares2buy = 'Shares to Buy'
    else:
        print(f"{price_or_shares2buy} is neither 'prices', nor 'shares2buy', sorry.")
        return
    stocks = pd.read_csv('stocks_list.csv')
    my_columns = ['Ticker', 'Stock Price', 'Shares to Buy']

    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    symbol_groups = list(chunks(stocks['Ticker'], 100))
    symbol_strings = []
    for i in range(0, len(symbol_groups)):
        symbol_strings.append(','.join(symbol_groups[i]))

    final_dataframe = pd.DataFrame(columns=my_columns)

    for symbol_string in symbol_strings:
        batch_api_call_url = f"https://cloud.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote&token={api_token}"
        data = requests.get(batch_api_call_url).json()
        for symbol in symbol_string.split(','):
            final_dataframe = final_dataframe.append(
                pd.Series([symbol,
                           data[symbol]['quote']['latestPrice'],
                           'N/A'],
                          index=my_columns),
                ignore_index=True)

    portfolio_size = 6000

    # The following lines are unnecessary unless the user inputs portfolio_size
    # try:
    #     val = float(portfolio_size)
    # except ValueError:
    #     portfolio_size = input("That's not a number, please try again.\nEnter the value of your portfolio: ")
    #     val = float(portfolio_size)

    position_size = float(portfolio_size) / len(final_dataframe.index)
    for i in range(0, len(final_dataframe['Ticker'])):
        final_dataframe.loc[i, 'Shares to Buy'] = math.floor(position_size / final_dataframe['Stock Price'][i])

    if stock_or_all.lower() == 'all':
        return final_dataframe
    else:
        return final_dataframe.iloc[stocks_dictionary[f'{stock_or_all}']][f'{price_or_shares2buy}']


def get_date():
    current_date = date.today().strftime("%d %B %Y")
    return current_date


def get_time():
    current_time = datetime.now().strftime("%H:%M:%S")
    return current_time


def get_weekday():
    day_of_the_week = calendar.day_name[date.today().weekday()]
    return day_of_the_week


def get_hour():
    if int(get_time()[0]) == 0:
        hour = int(get_time()[1])
    else:
        hour = int(get_time()[0:2])
    return hour


# Invert both booleans when debugging (to True/False)
weekend = True
market_open = False
money = 6000


class Stock:
    def __init__(self, symbol, num_of_shares, price_at_sale):
        self.symbol = symbol
        self.num_of_shares = num_of_shares
        self.price_at_sale = price_at_sale

    def buy_shares(self, num_to_buy, price_per_share):
        self.num_of_shares = num_to_buy
        cost = num_to_buy * price_per_share
        self.price_at_sale = price_per_share
        return cost

    def sell_shares(self, price_per_share):
        earnings = self.num_of_shares * price_per_share
        self.num_of_shares = 0
        self.price_at_sale = price_per_share
        return earnings

    def value(self, current_value):
        share_value = self.num_of_shares * current_value
        return share_value


TSLA = Stock('TSLA', 0, 0)
RTX = Stock('RTX', 0, 0)
HON = Stock('HON', 0, 0)
KBR = Stock('KBR', 0, 0)
AAPL = Stock('AAPL', 0, 0)


def buy_all_shares():
    price_check = check_prices('all', 'price')
    money = 6000
    money -= TSLA.buy_shares(price_check['Shares to Buy'][0], price_check['Stock Price'][0])
    print(f"Bought {price_check['Shares to Buy'][0]} share(s) of TSLA for ${price_check['Stock Price'][0]}.")
    money -= RTX.buy_shares(price_check['Shares to Buy'][1], price_check['Stock Price'][1])
    print(f"Bought {price_check['Shares to Buy'][1]} share(s) of RTX for ${price_check['Stock Price'][1]}.")
    money -= HON.buy_shares(price_check['Shares to Buy'][2], price_check['Stock Price'][2])
    print(f"Bought {price_check['Shares to Buy'][2]} share(s) of HON for ${price_check['Stock Price'][2]}.")
    money -= KBR.buy_shares(price_check['Shares to Buy'][3], price_check['Stock Price'][3])
    print(f"Bought {price_check['Shares to Buy'][3]} share(s) of KBR for ${price_check['Stock Price'][3]}.")
    money -= AAPL.buy_shares(price_check['Shares to Buy'][4], price_check['Stock Price'][4])
    print(f"Bought {price_check['Shares to Buy'][4]} share(s) of AAPL for ${price_check['Stock Price'][4]}.")
    return money
    sleep(60)


def try_to_sell_stocks(money=money):
    sold_all_stocks = False
    tsla_old_price = TSLA.price_at_sale
    rtx_old_price = RTX.price_at_sale
    hon_old_price = HON.price_at_sale
    kbr_old_price = KBR.price_at_sale
    aapl_old_price = AAPL.price_at_sale
    while not sold_all_stocks:
        price_check = check_prices('all', 'price')
        tsla_potential_profit = TSLA.value(price_check['Stock Price'][0]) - (TSLA.num_of_shares * tsla_old_price)
        rtx_potential_profit = RTX.value(price_check['Stock Price'][1]) - (RTX.num_of_shares * rtx_old_price)
        hon_potential_profit = HON.value(price_check['Stock Price'][2]) - (HON.num_of_shares * hon_old_price)
        kbr_potential_profit = KBR.value(price_check['Stock Price'][3]) - (KBR.num_of_shares * kbr_old_price)
        aapl_potential_profit = AAPL.value(price_check['Stock Price'][4]) - (AAPL.num_of_shares * aapl_old_price)
        if tsla_potential_profit >= 1 and TSLA.num_of_shares != 0:
            money += TSLA.sell_shares(price_check['Stock Price'][0])
            print(f"Sold {price_check['Shares to Buy'][0]} share(s) of TSLA at ${price_check['Stock Price'][0]} (from ${tsla_old_price}) each at {get_time()}.")
            TSLA.num_of_shares = 0
        if rtx_potential_profit >= 1 and RTX.num_of_shares != 0:
            money += RTX.sell_shares(price_check['Stock Price'][1])
            print(f"Sold {price_check['Shares to Buy'][1]} share(s) of RTX at ${price_check['Stock Price'][1]} (from ${rtx_old_price}) each at {get_time()}.")
            RTX.num_of_shares = 0
        if hon_potential_profit >= 1 and HON.num_of_shares != 0:
            money += HON.sell_shares(price_check['Stock Price'][2])
            print(f"Sold {price_check['Shares to Buy'][2]} share(s) of HON at ${price_check['Stock Price'][2]} (from ${hon_old_price}) each at {get_time()}.")
            HON.num_of_shares = 0
        if kbr_potential_profit >= 1 and KBR.num_of_shares != 0:
            money += KBR.sell_shares(price_check['Stock Price'][3])
            print(f"Sold {price_check['Shares to Buy'][3]} share(s) of KBR at ${price_check['Stock Price'][3]} (from ${kbr_old_price}) each at {get_time()}.")
            KBR.num_of_shares = 0
        if aapl_potential_profit >= 1 and AAPL.num_of_shares != 0:
            money += AAPL.sell_shares(price_check['Stock Price'][4])
            print(f"Sold {price_check['Shares to Buy'][4]} share(s) of AAPL at ${price_check['Stock Price'][4]} (from ${aapl_old_price}) each at {get_time()}.")
            AAPL.num_of_shares = 0

        sleep(60)
        if TSLA.num_of_shares == 0 and RTX.num_of_shares == 0 and HON.num_of_shares == 0 and KBR.num_of_shares == 0 and AAPL.num_of_shares == 0:
            sold_all_stocks = True


def wait_to_buy_stocks(money=money):
    sold_all_stocks = True
    tsla_old_price = TSLA.price_at_sale
    rtx_old_price = RTX.price_at_sale
    hon_old_price = HON.price_at_sale
    kbr_old_price = KBR.price_at_sale
    aapl_old_price = AAPL.price_at_sale
    while sold_all_stocks:
        price_check = check_prices('all', 'price')
        tsla_potential_loss = TSLA.value(price_check['Stock Price'][0]) - (TSLA.num_of_shares * tsla_old_price)
        rtx_potential_loss = RTX.value(price_check['Stock Price'][1]) - (RTX.num_of_shares * rtx_old_price)
        hon_potential_loss = HON.value(price_check['Stock Price'][2]) - (HON.num_of_shares * hon_old_price)
        kbr_potential_loss = KBR.value(price_check['Stock Price'][3]) - (KBR.num_of_shares * kbr_old_price)
        aapl_potential_loss = AAPL.value(price_check['Stock Price'][4]) - (AAPL.num_of_shares * aapl_old_price)
        if tsla_potential_loss >= -1 and TSLA.num_of_shares == 0:
            money -= TSLA.buy_shares(price_check['Shares to Buy'[0]], price_check['Stock Price'][0])
            print(f"Bought {price_check['Shares to Buy'][0]} share(s) of TSLA at ${price_check['Stock Price'][0]} each at {get_time()}.")
        if rtx_potential_loss >= -1 and RTX.num_of_shares == 0:
            money -= RTX.buy_shares(price_check['Shares to Buy'][1], price_check['Stock Price'][1])
            print(f"Bought {price_check['Shares to Buy'][1]} share(s) of RTX at ${price_check['Stock Price'][1]} each at {get_time()}.")
        if hon_potential_loss >= -1 and HON.num_of_shares == 0:
            money -= HON.buy_shares(price_check['Shares to Buy'][2], price_check['Stock Price'][2])
            print(f"Bought {price_check['Shares to Buy'][2]} share(s) of HON at ${price_check['Stock Price'][2]} each at {get_time()}.")
        if kbr_potential_loss >= -1 and KBR.num_of_shares == 0:
            money -= KBR.buy_shares(price_check['Shares to Buy'][3], price_check['Stock Price'][3])
            print(f"Bought {price_check['Shares to Buy'][3]} share(s) of KBR at ${price_check['Stock Price'][3]} each at {get_time()}.")
        if aapl_potential_loss >= -1 and AAPL.num_of_shares == 0:
            money -= AAPL.buy_shares(price_check['Shares to Buy'][4], price_check['Stock Price'][4])
            print(f"Bought {price_check['Shares to Buy'][4]} share(s) of AAPL at ${price_check['Stock Price'][4]} each at {get_time()}.")

        sleep(60)
        if TSLA.num_of_shares != 0 and RTX.num_of_shares != 0 and HON.num_of_shares != 0 and KBR.num_of_shares != 0 and AAPL.num_of_shares != 0:
            sold_all_stocks = False


message_1 = f"Starting with $6,000 on {get_date()} at {get_time()}."

# --------------------TERMINAL BEGINS HERE--------------------

clear_screen()
print(message_1)

today = get_weekday()
while today != 'Saturday' and today != 'Sunday':
    hour = get_hour()
    while 7 <= hour < 15:
        if TSLA.num_of_shares == 0 and RTX.num_of_shares == 0 and HON.num_of_shares == 0 and KBR.num_of_shares == 0 and AAPL.num_of_shares == 0:
            money = buy_all_shares()
            message_2 = f"Cash on hand: ${money.__round__(2)}"
            print(message_2)
            hour = get_hour()
        try_to_sell_stocks()
        hour = get_hour()
        wait_to_buy_stocks()
        hour = get_hour()

    clear_screen()
    print(f'Money at close: ${money}')
    price_check = check_prices('all', 'price')
    tsla_value = TSLA.value(price_check['Stock Price'][0])
    rtx_value = RTX.value(price_check['Stock Price'][1])
    hon_value = HON.value(price_check['Stock Price'][2])
    kbr_value = KBR.value(price_check['Stock Price'][3])
    aapl_value = AAPL.value(price_check['Stock Price'][4])
    print(
        f'Portfolio at close: ${(money + tsla_value + rtx_value + hon_value + kbr_value + aapl_value).__round__(2)}\n')
    print(f"""TSLA: ${tsla_value}
        RTX: ${rtx_value}
        HON: ${hon_value}
        KBR: ${kbr_value}
        AAPL: ${aapl_value}""")
    sleep(60)
    today = get_weekday()

print("It's the weekend, market is closed.")
sleep(3600)
today = get_weekday()
