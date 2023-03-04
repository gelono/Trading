from pprint import pprint
from processing.processing_data import *
from processing.processing_trades import *
import numpy as np

from processing.reporting import *

pd.set_option('display.max_columns', None)


columns = ['date', 'close', 'open', 'high', 'min', 'vol', 'change']
drop_col = ['vol', 'change']
prices = ['close', 'open', 'high', 'min']

table, crypto = read_data('./Data/BTCUSD_1D_11_2017.csv', columns, drop_col), True
# table, crypto = read_data('./Data/ETH_USD Binance.csv', columns, drop_col), True
# table, crypto = read_data('./Data/BNB_USD.csv', columns, drop_col), True
# table, crypto = read_data('./Data/LTC_USD.csv', columns, drop_col), True
# table, crypto = read_data('./Data/XMR_USD.csv', columns, drop_col), True  # no
# table, crypto = read_data('./Data/S&P 500.csv', columns, drop_col), False
# table, crypto = read_data('./Data/XAU_USD.csv', columns, drop_col), False
# table, crypto = read_data('./Data/WTI.csv', columns, drop_col), False
# table, crypto = read_data('./Data/JPM.csv', columns, drop_col), False  # no
# table, crypto = read_data('./Data/BAC.csv', columns, drop_col), False  # no
# table, crypto = read_data('./Data/AAPL.csv', columns, drop_col), False

table = formatting_dates(table, 'date')
table = columns_format_to_float(table, prices)
table = sort_data_by_date(table)

table['dayofweek'] = table['date'].dt.dayofweek
# ------------------------------------------------------
if not crypto:
    table = table.drop(np.where(table['dayofweek'] == 5)[0])
    table = table.reset_index(drop=True)
    table = table.drop(np.where(table['dayofweek'] == 6)[0])
    table = table.reset_index(drop=True)
    last_day_of_work_week = 4
else:
    last_day_of_work_week = 6
# ------------------------------------------------------

table['closeofweak_temp'] = closeofweak_temp_create(table, last_day_of_work_week)


# days_in_week = 5  # 7, non crypto - 5
table['ma_week_shift'] = calculate_ma_week(table, 'date', 'closeofweak_temp', 3, 3)
table['ma_week_shift'] = ma_week_filling(table)

close = table['close'].to_frame()
table['ma3x3_day'] = close['close'].rolling(3).mean()
table['ma3x3_day'] = table['ma3x3_day'].shift(3)
table['ma3x3_day'].fillna(0, inplace=True)

table['direction'] = direction(table, 'closeofweak_temp', 'ma_week_shift')
table.to_excel('table_save.xlsx')


week_date, week_close, week_high, week_low = table_week(table, 'date', 'closeofweak_temp', 'high', 'min', last_day_of_work_week+1)
week_cols = ['week_date', 'week_close', 'week_high', 'week_low']
table_week = pd.DataFrame(columns=week_cols)
table_week['week_date'] = week_date
table_week['week_close'] = week_close
table_week['week_high'] = week_high
table_week['week_low'] = week_low

buy_results = processing_buy_trades(
    table,
    table_week,
    7,  # Задержка в днях
    3,  # Моментум
    14, # АТР дневной
    1,  # Размер стопа в АТР
    1,  # Кол-во усреднений
    3   # АТР недельный
)

sell_results = processing_sell_trades(
    table,
    table_week,
    7,  # Задержка в днях
    3,  # Моментум
    14, # АТР дневной
    1,  # Размер стопа в АТР
    1,  # Кол-во усреднений
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

# pprint(buy_results)
# print('----------------------------------------')
# pprint(sell_results)

# print(table.head(60))
# print(table.tail(60))

plot_results(table, lst_buy, lst_date_buy, lst_sell, lst_date_sell)