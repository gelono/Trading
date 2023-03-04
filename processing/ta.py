import numpy as np


def week_ma_envelop(table_week, date_of_trade, period: int, k: float):
    date_week_list = table_week['week_date'].to_list()
    high_week_list = table_week['week_high'].to_list()
    low_week_list = table_week['week_low'].to_list()

    for i in range(period, table_week.shape[0]):
        if date_week_list[i - 1] < date_of_trade <= date_week_list[i]:
            temp_list = []
            if date_of_trade == date_week_list[i]:
                for j in range(i - period + 1, i + 1):
                    temp_list.append((high_week_list[j] - low_week_list[j]) / low_week_list[j])
                avg_atr = np.mean(temp_list)
                return avg_atr * k
            else:
                for j in range(i - period, i):
                    temp_list.append((high_week_list[j] - low_week_list[j]) / low_week_list[j])
                avg_atr = np.mean(temp_list)
                return avg_atr * k


def standard_deviation_mom(close_list, period, day):
    mom_list = []
    for i in range(day - period, day + 1):
        mom = close_list[i] - close_list[i - 3]
        mom_list.append(mom)

    stand_dev = np.std(mom_list) * 2
    return stand_dev
