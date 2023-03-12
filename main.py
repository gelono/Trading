from pprint import pprint
from processing.processing_data import *
from processing.processing_trades import *

from processing.reporting import *

pd.set_option('display.max_columns', None)


# file = './Data/BTCUSD_1D_11_2017.csv'
# file = './Data/ETH_USD Binance.csv'
# file = './Data/BNB_USD.csv'
# file = './Data/LTC_USD.csv'
# file = './Data/XMR_USD.csv'
# file = './Data/S&P 500.csv'
file = './Data/ES.csv'
# file = './Data/XAU_USD.csv'
# file = './Data/WTI.csv'
# file = './Data/JPM.csv'
# file = './Data/BAC.csv'
# file = './Data/AAPL.csv'

data = ProcessingDate(file, crypto=False, week_ma_len=3, week_ma_shift=3)

buy_results = processing_buy_trades(
    data.table,
    data.table_week,
    4,  # Задержка в днях
    3,  # Моментум
    10, # АТР дневной
    2,  # Размер стопа в АТР
    2,  # Кол-во усреднений
    3   # АТР недельный
)

sell_results = processing_sell_trades(
    data.table,
    data.table_week,
    4,  # Задержка в днях
    3,  # Моментум
    10, # АТР дневной
    2,  # Размер стопа в АТР
    2,  # Кол-во усреднений
    3   # АТР недельный
)

lst_buy = [e[1] for e in buy_results]
lst_date_buy = [e[0] for e in buy_results]
lst_sell = [e[1] for e in sell_results]
lst_date_sell = [e[0] for e in sell_results]
list_buy_risk = [e[5] for e in buy_results]
list_sell_risk = [e[5] for e in sell_results]


print(f'Total profit buy trades: {sum(lst_buy)}')
print(f'Amount of buy trades: {len(buy_results)}')
report_by_year(buy_results, 'buy')

high_risk_total_buy = []
low_risk_total_buy = []
for result, risk in zip(lst_buy, list_buy_risk):
    if risk == 'high risk':
        high_risk_total_buy.append(result)
    else:
        low_risk_total_buy.append(result)

print(f'high_risk_total_buy: {sum(high_risk_total_buy)} | trades: {len(high_risk_total_buy)}')
print(f'low_risk_total_buy: {sum(low_risk_total_buy)} | trades: {len(low_risk_total_buy)}')
print('\n')

print(f'Total profit sell trades: {sum(lst_sell)}')
print(f'Amount of sell trades: {len(sell_results)}')
report_by_year(sell_results, 'sell')

high_risk_total_sell = []
low_risk_total_sell = []
for result, risk in zip(lst_sell, list_sell_risk):
    if risk == 'high risk':
        high_risk_total_sell.append(result)
    else:
        low_risk_total_sell.append(result)
print(f'high_risk_total_sell: {sum(high_risk_total_sell)} | trades: {len(high_risk_total_sell)}')
print(f'low_risk_total_sell: {sum(low_risk_total_sell)} | trades: {len(low_risk_total_sell)}')

pprint(buy_results)
# print('----------------------------------------')
# pprint(sell_results)

# print(table.head(60))
# print(table.tail(60))

plot_results(data.table, lst_buy, lst_date_buy, lst_sell, lst_date_sell)