import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math
from secrets import real_token

stocks = pd.read_csv('sp_500_stocks.csv')
symbol = 'AAPL'

real_api_url = f'https://cloud.iexapis.com/stable/stock/{symbol}/quote/?token={real_token}'
data = requests.get(real_api_url).json()

price = data['latestPrice']
market_cap = data['marketCap']

my_columns = ['Ticker', 'Stock Price', 'Market Capitalisation', 'Number of Shares to Buy']
final_dataframe = pd.DataFrame(columns=my_columns)

final_dataframe = final_dataframe.append(
    pd.Series(
        [
            symbol,
            price,
            market_cap,
            'N/A'
        ],
        index=my_columns
    ),
    ignore_index=True
)

# print('Testing:\n')
# print(final_dataframe)


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))

final_dataframe = pd.DataFrame(columns=my_columns)

for symbol_string in symbol_strings:
    batch_api_call_url = f"https://cloud.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote&token={real_token}"
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        final_dataframe = final_dataframe.append(
            pd.Series([symbol,
                       data[symbol]['quote']['latestPrice'],
                       data[symbol]['quote']['marketCap'],
                       'N/A'],
                      index=my_columns),
            ignore_index=True)

# print(final_dataframe)

portfolio_size = input('Enter the value of your portfolio: ')
try:
    val = float(portfolio_size)
except ValueError:
    portfolio_size = input("That's not a number, please try again.\nEnter the value of your portfolio: ")
    val = float(portfolio_size)

position_size = float(portfolio_size) / len(final_dataframe.index)
for i in range(0, len(final_dataframe['Ticker'])-1):
    final_dataframe.loc[i, 'Number Of Shares to Buy'] = math.floor(position_size / final_dataframe['Stock Price'][i])
print(final_dataframe)

writer = pd.ExcelWriter('recommended_trades.xlsx', engine='xlsxwriter')
final_dataframe.to_excel(writer, 'Recommended Trades', index=False)
background_colour = '#54bb99'
font_colour = '#ffffff'

string_format = writer.book.add_format(
    {
        'font_color': font_colour,
        'bg_color': background_colour,
        'border': 1
    }
)

dollar_format = writer.book.add_format(
    {
        'num_format': '$0.00',
        'font_color': font_colour,
        'bg_color': background_colour,
        'border': 1
    }
)

integer_format = writer.book.add_format(
    {
        'num_format': '0',
        'font_color': font_colour,
        'bg_color': background_colour,
        'border': 1
    }
)

writer.sheets['Recommended Trades'].set_column('A:A', 18, string_format)
writer.sheets['Recommended Trades'].set_column('B:B', 18, string_format)
writer.sheets['Recommended Trades'].set_column('C:C', 18, string_format)
writer.sheets['Recommended Trades'].set_column('D:D', 18, string_format)
writer.save()
