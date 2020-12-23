import pandas as pd
import requests
import math
from time import sleep
from datetime import date, datetime
from os import system
import calendar
from secrets import api_token, stocks_dictionary, stocks_list


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


# Invert both booleans when not debugging
weekend = False
market_open = True

# --------------------TERMINAL BEGINS HERE--------------------

message = f"Starting with $6,000 on {get_date()} at {get_time()}"
print(message)

while weekend:
    if get_weekday() == 'Sunday' or get_weekday() == 'Saturday':
        print("It's the weekend!  The market is closed.")
        sleep(3600)
    else:
        weekend = False

# if get_hour() >= 15:
#     sleep((24 - get_hour()) * 3600)
#
# # Sleep until the time is HH:MM:00
# sleep(60 - int(get_time()[-2:]))
#
# # Sleep until the time is HH:00:00
# sleep((60 - int(get_time()[3:5])) * 60)
#
# hours_remaining = 7 - get_hour()
#
# # Sleep until the time is 09:00:00 EST
# sleep(hours_remaining * 3600)

while not market_open:
    if get_time() == '07:00:00':
        market_open = True
    elif get_time() == '06:59:59':
        sleep(1)
        market_open = True
    else:
        print(f'The time is {get_time()}')
        sleep(1)
        clear_screen()

initial_check = check_prices('all', 'price')
tsla_stocks = initial_check['Shares to Buy'][0]
rtx_stocks = initial_check['Shares to Buy'][1]
hon_stocks = initial_check['Shares to Buy'][2]
kbr_stocks = initial_check['Shares to Buy'][3]
aapl_stocks = initial_check['Shares to Buy'][4]

tsla_price = initial_check['Stock Price'][0]
rtx_price = initial_check['Stock Price'][1]
hon_price = initial_check['Stock Price'][2]
kbr_price = initial_check['Stock Price'][3]
aapl_price = initial_check['Stock Price'][4]

tsla_value = tsla_price * tsla_stocks
rtx_value = rtx_price * rtx_stocks
hon_value = hon_price * hon_stocks
kbr_value = kbr_price * kbr_stocks
aapl_value = aapl_price * aapl_stocks
total_value = tsla_value + rtx_value + hon_value + kbr_value + aapl_value

print(f"Buying {tsla_stocks} TSLA @ {tsla_price} (Total: {tsla_value})")
print(f"Buying {rtx_stocks} TSLA @ {rtx_price} (Total: {rtx_value})")
print(f"Buying {hon_stocks} TSLA @ {hon_price} (Total: {hon_value})")
print(f"Buying {kbr_stocks} TSLA @ {kbr_price} (Total: {kbr_value})")
print(f"Buying {aapl_stocks} TSLA @ {aapl_price} (Total: {aapl_value})")
print(f"Total spent: {total_value}/6000 ({(6000 - total_value).__round__(2)} remaining)")
