import numpy as np


class TradeActions:
    table = None

    def __init__(self, table):
        self.table = table

    def early_enter_buy(self, day):
        if self.table['direction'][day] == 1 \
                and self.table['close'][day] < self.table['ma3x3_day'][day] \
                and self.table['close'][day - 1] >= self.table['ma3x3_day'][day - 1] \
                and self.table['close'][day] > self.table['ma_week_shift'][day]:
            return True
        else:
            return False

    def late_enter_buy(self, day):
        if self.table['direction'][day] == 1 \
                and self.table['close'][day] > self.table['ma3x3_day'][day] \
                and self.table['close'][day - 1] <= self.table['ma3x3_day'][day - 1] \
                and self.table['close'][day] > self.table['ma_week_shift'][day]:
            return True
        else:
            return False

    def early_enter_sell(self, day):
        if self.table['direction'][day] == 0 \
                and self.table['close'][day] > self.table['ma3x3_day'][day] \
                and self.table['close'][day - 1] <= self.table['ma3x3_day'][day - 1] \
                and self.table['close'][day] < self.table['ma_week_shift'][day]:
            return True
        else:
            return False

    def late_enter_sell(self, day):
        if self.table['direction'][day] == 0 \
                and self.table['close'][day] < self.table['ma3x3_day'][day] \
                and self.table['close'][day - 1] >= self.table['ma3x3_day'][day - 1] \
                and self.table['close'][day] < self.table['ma_week_shift'][day]:
            return True
        else:
            return False

    @staticmethod
    def avg_enter_buy(results, close_list, min_list, date_of_trade, date_list, direction_list, trade_category, day, avg_price_days, stop_loss, koef):
        price_list = [close_list[day]]
        open_price_buy = np.mean(price_list)
        stop_price_buy = open_price_buy * (1-(stop_loss*koef))
        count = 1
        for i in range(day + 1, day + avg_price_days):
            try:
                if min_list[i] <= stop_price_buy:
                    result = (date_of_trade, (((stop_price_buy - open_price_buy) / open_price_buy) * 100) * (count / avg_price_days),
                              date_list[i], stop_price_buy, 'Stop-loss', trade_category)
                    results.append(result)
                    return False, i, open_price_buy, stop_price_buy
                elif direction_list[i] == 0:
                    result = (date_of_trade, (((close_list[i] - open_price_buy) / open_price_buy) * 100) * (count / avg_price_days),
                              date_list[i], stop_price_buy, 'Direction has changed', trade_category)
                    results.append(result)
                    return False, i, open_price_buy, stop_price_buy
                else:
                    price_list.append(close_list[i])
                    open_price_buy = np.mean(price_list)
                    stop_price_buy = open_price_buy * (1-(stop_loss*koef))
                    count += 1
                    day = i
            except IndexError:
                result = (date_of_trade, (((close_list[-1] - open_price_buy) / open_price_buy) * 100) * (count / avg_price_days),
                          date_list[-1], stop_price_buy, 'End of the data', trade_category)
                results.append(result)
                return False, i, open_price_buy, stop_price_buy

        return True, day, open_price_buy, stop_price_buy

    @staticmethod
    def avg_enter_sell(results, close_list, high_list, date_of_trade, date_list, direction_list, trade_category, day, avg_price_days,
                       stop_loss, koef):
        price_list = [close_list[day]]
        open_price_sell = np.mean(price_list)
        stop_price_sell = open_price_sell * (1 + (stop_loss * koef))
        count = 1
        for i in range(day + 1, day + avg_price_days):
            try:
                if high_list[i] >= stop_price_sell:
                    result = (
                    date_of_trade, (((open_price_sell - stop_price_sell) / open_price_sell) * 100) * (count / avg_price_days),
                    date_list[i], stop_price_sell, 'Stop-loss', trade_category)
                    results.append(result)
                    return False, i, open_price_sell, stop_price_sell
                elif direction_list[i] == 1:
                    result = (date_of_trade, (((open_price_sell - close_list[i]) / open_price_sell) * 100) * (count / avg_price_days),
                              date_list[i], stop_price_sell, 'Direction has changed', trade_category)
                    results.append(result)
                    return False, i, open_price_sell, stop_price_sell
                else:
                    price_list.append(close_list[i])
                    open_price_sell = np.mean(price_list)
                    stop_price_sell = open_price_sell * (1 + (stop_loss * koef))
                    count += 1
                    day = i
            except IndexError:
                result = (date_of_trade, (((open_price_sell - close_list[-1]) / open_price_sell) * 100) * (count / avg_price_days),
                          date_list[-1], stop_price_sell, 'End of the data', trade_category)
                results.append(result)
                return False, i, open_price_sell, stop_price_sell

        return True, day, open_price_sell, stop_price_sell